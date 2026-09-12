"""Map the saved short32 batch into exact shaped-reward root-only HF inputs."""

from collections import defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import math_core


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SHORT = SIDE / "openai-mrcr-short32-base-calibration-v1"
ATTEMPT = SHORT / "outputs/attempt-002"
ANALYSIS = SIDE.parent / "analyses/openai-mrcr-short32-outcomes-2026-09-12"
SIGNAL = ANALYSIS / "SIGNAL_ADDENDUM.json"
EXTRACTOR = SIDE.parent / "analyses/mrcr-root-only-update-preflight-2026-09-12/extract_inputs.py"
SCORER = SIDE / "openai-mrcr-short-root-data-v1/official_score.py"
MODEL = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
PINS = {
    SHORT / "READY_V2.json": "aea688ffc6f2ef9d5dceb3037da972409a869a1555f9c375a0ac76feba3b414e",
    ATTEMPT / "OWNER_TERMINAL.json": "99a000f550c324fb46efb9e3316fb2cd3387b6d7df91b4c2341905e389d2f79f",
    ATTEMPT / "science/RESULT.json": "ac09e0a146daecce6e99396773cc918b1dbde8867842e40d15e509584a39f579",
    SIGNAL: "396bda9a0f914aaec53d4141367d532dd46303cffdf8a0f96477d84273d59e51",
    EXTRACTOR: "0f163af566b4bd360523733790f037c33d802be39c67d1cc9256248438d2ff02",
    SCORER: "b40431d62562bb0bd02b58099533a064a87aa2c85a700f4382288c29337be8f6",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def shaped_reward(raw_official_similarity, raw_exact):
    if not isinstance(raw_official_similarity, (int, float)) or not math.isfinite(
        raw_official_similarity
    ):
        raise ValueError("shaped reward requires a finite raw official score")
    if type(raw_exact) is not bool:
        raise ValueError("shaped reward exact flag must be boolean")
    return 0.5 * (raw_official_similarity >= 0.90) + 0.5 * raw_exact


def build():
    for path, expected in PINS.items():
        if sha(path) != expected:
            raise ValueError("pinned saved-batch source changed: " + str(path))
    terminal = read(ATTEMPT / "OWNER_TERMINAL.json")
    if not (
        terminal.get("complete") is True
        and terminal.get("released") is True
        and not terminal.get("errors")
        and terminal.get("recorded") == 32
    ):
        raise ValueError("saved short32 owner is not a complete clean release")
    signal = read(SIGNAL)
    public = read(SHORT / "inputs/PUBLIC.json")
    gold = read(SHORT / "inputs/HOST_GOLD.json")
    plan = {row["id"]: row for row in public["plan"]}
    if len(plan) != 32 or len(signal["records"]) != 32:
        raise ValueError("saved short32 coordinate inventory differs")
    by_group = defaultdict(list)
    for row in signal["records"]:
        by_group[row["record_id"]].append(row)
    if len(by_group) != 8 or any(len(rows) != 4 for rows in by_group.values()):
        raise ValueError("saved batch is not exact eight by four")
    admitted_groups = {
        group for group, rows in by_group.items() if all(row["available"] for row in rows)
    }
    if len(admitted_groups) != 6:
        raise ValueError("complete-group admission changed")
    excluded_groups = []
    for group, rows in sorted(by_group.items()):
        if group in admitted_groups:
            continue
        excluded_groups.append(
            {
                "group_id": group,
                "reason": "whole_group_excluded_because_at_least_one_rollout_unavailable",
                "coordinates": [row["coordinate_id"] for row in rows],
                "availability": [row["available"] for row in rows],
                "episode_sha256": [row["episode_sha256"] for row in rows],
                "relabelled_as_zero": False,
            }
        )
    extractor = load("shaped_mrcr_exact_extractor", EXTRACTOR)
    scorer = load("shaped_mrcr_official_scorer", SCORER)
    episode_paths = sorted((ATTEMPT / "science/episodes").glob("*.json"))
    episodes_by_id = {read(path)["coordinate"]["id"]: path for path in episode_paths}
    native_paths = sorted((ATTEMPT / "science/native-calls").glob("*-result.json"))
    native = [(path, read(path)) for path in native_paths]
    records = []
    consumed_native = set()
    for signal_row in sorted(
        (row for row in signal["records"] if row["record_id"] in admitted_groups),
        key=lambda row: (row["record_id"], row["repeat"]),
    ):
        coordinate_id = signal_row["coordinate_id"]
        coordinate = plan[coordinate_id]
        path = episodes_by_id[coordinate_id]
        wrapper = read(path)
        trace_rows = wrapper["episode"].get("traces") or []
        if len(trace_rows) != 1:
            raise ValueError("admitted episode does not have exactly one trace")
        trace = trace_rows[0]
        turns = extractor.trace_turns(trace)
        session = [
            (native_path, row)
            for native_path, row in native
            if row.get("session_id") == trace.get("id")
        ]
        if len(session) != len(turns) or any(row.get("status") != "returned" for _, row in session):
            raise ValueError("admitted trace/native inventory differs")
        matched = extractor.match_native(turns, [row for _, row in session])
        root_turns, fixed_children = [], []
        for turn in matched:
            native_path = session[turn["native_index"]][0]
            if native_path in consumed_native or not turn["usage_matches"]:
                raise ValueError("native result reused or usage differs")
            consumed_native.add(native_path)
            if turn["depth"] == 0:
                root_turns.append(
                    {
                        key: turn[key]
                        for key in (
                            "prompt_ids",
                            "action_ids",
                            "input_ids",
                            "labels",
                            "loss_mask",
                            "old_logprobs",
                            "depth",
                            "request_id",
                        )
                    }
                    | {
                        "credited": True,
                        "native_result": str(native_path),
                        "native_result_sha256": sha(native_path),
                    }
                )
            else:
                fixed_children.append(
                    {
                        "depth": turn["depth"],
                        "credited": False,
                        "loss_tokens": 0,
                        "action_tokens": turn["action_tokens"],
                        "action_ids_sha256": digest(turn["action_ids"]),
                        "native_result": str(native_path),
                        "native_result_sha256": sha(native_path),
                    }
                )
        if not root_turns:
            raise ValueError("admitted episode has no root actions")
        reply = trace.get("root_reply")
        truth = gold[signal_row["record_id"]]
        score = scorer.grade(reply, truth["answer"], truth["random_string_to_prepend"])
        exact = isinstance(reply, str) and reply == truth["answer"]
        if (
            abs(score - signal_row["official_raw_reward"]) > 1e-12
            or exact is not signal_row["raw_exact"]
        ):
            raise ValueError("raw reward inputs differ from authenticated episode")
        records.append(
            {
                "episode_id": coordinate_id,
                "group_id": signal_row["record_id"],
                "repeat": signal_row["repeat"],
                "reward": shaped_reward(score, exact),
                "raw_official_similarity": score,
                "raw_exact": exact,
                "advantage": None,
                "root_turns": root_turns,
                "fixed_child_turns": fixed_children,
                "all_native_calls_exactly_matched": True,
                "episode_path": str(path),
                "episode_sha256": sha(path),
                "source_row_sha256": coordinate["source_row_sha256"],
            }
        )
    rewards = [row["reward"] for row in records]
    groups = [row["group_id"] for row in records]
    advantages = math_core.rloo_advantages(rewards, groups)
    for row, advantage in zip(records, advantages, strict=True):
        row["advantage"] = advantage
    if len(records) != 24 or len(consumed_native) != sum(
        len(row["root_turns"]) + len(row["fixed_child_turns"]) for row in records
    ):
        raise ValueError("admitted root input inventory differs")
    mixed = sum(
        len({row["reward"] for row in records if row["group_id"] == group}) > 1
        for group in admitted_groups
    )
    if mixed < 2:
        raise ValueError("fewer than two complete shaped-reward mixed groups")
    return {
        "schema": "mrcr-short-shaped-root-hf-training-inputs-v1",
        "model": {
            "base": str(MODEL),
            "revision": "cdbee75f17c01a7cc42f958dc650907174af0554",
            "behavior_adapter": None,
            "root_new_adapter": "rank8-zero-effect",
            "child_frozen": True,
        },
        "sampling": {"temperature": 0.5, "rollouts_per_group": 4},
        "reward": {
            "formula": "0.5*I(raw_official_similarity>=0.90)+0.5*I(raw_exact)",
            "newline_or_output_repair": None,
            "raw_metrics_retained_per_episode": True,
        },
        "episodes": records,
        "excluded_groups": excluded_groups,
        "source": {
            "short32_ready_v2_sha256": sha(SHORT / "READY_V2.json"),
            "owner_terminal_sha256": sha(ATTEMPT / "OWNER_TERMINAL.json"),
            "science_result_sha256": sha(ATTEMPT / "science/RESULT.json"),
            "signal_addendum_sha256": sha(SIGNAL),
            "extractor_sha256": sha(EXTRACTOR),
            "native_result_files_total": len(native_paths),
            "native_result_files_admitted": len(consumed_native),
            "excluded_native_evidence_preserved": True,
        },
        "limits": {
            "training_contexts": 8,
            "admitted_complete_groups": 6,
            "episodes": 24,
            "mixed_groups": mixed,
            "heldout_model_queries": 0,
            "generalization_claim": False,
        },
    }

