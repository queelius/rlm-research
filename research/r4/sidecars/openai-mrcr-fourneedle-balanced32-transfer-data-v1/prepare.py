"""Freeze 8 examples for each requested ordinal from pinned official four-needle data."""

from __future__ import annotations

from collections import Counter
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat

from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PREVIOUS = SIDE / "openai-mrcr-fourneedle-ordinal-transfer-data-v1"
SHORT = SIDE / "openai-mrcr-short-root-data-v1"
LONG = SIDE / "openai-mrcr-long-transfer-data-v1"
FRESH = SIDE / "openai-mrcr-short-next8-data-v1"
MODEL = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
NAMESPACE = "mrcr-fourneedle-balanced-transfer-20260912"
SEED_START = 202609270000


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load("mrcr_fourneedle_balanced_source", PREVIOUS / "prepare.py")


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def read(path: Path):
    return json.loads(Path(path).read_text())


def write_json(path: Path, value, mode: int = 0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def pair_hashes(messages):
    return base._pair_hashes(messages)


def answer_hashes(messages):
    return base._answer_hashes(messages)


@functools.lru_cache(maxsize=1)
def exposures():
    values = []
    short_public = read(SHORT / "MODEL_INPUTS_V2.json")
    short_gold = read(SHORT / "host/HOST_GOLD.json")
    for split in ("train", "heldout"):
        for row in short_public[split]:
            messages = json.loads(Path(row["prompt_json_path"]).read_text())
            truth = short_gold[split][row["id"]]
            values.append(
                {
                    "source": f"short48:{split}",
                    "row_sha256": row["source_row_sha256"],
                    "pairs": pair_hashes(messages),
                    "answers": answer_hashes(messages),
                    "target": text_sha(
                        truth["answer"].removeprefix(truth["random_string_to_prepend"])
                    ),
                }
            )
    sources = (
        ("long16", LONG / "MODEL_INPUTS.json", LONG / "host/HOST_GOLD.json"),
        ("fresh8", FRESH / "MODEL_INPUTS.json", FRESH / "host/HOST_GOLD.json"),
        (
            "prior-fourneedle16",
            PREVIOUS / "MODEL_INPUTS.json",
            PREVIOUS / "host/HOST_GOLD.json",
        ),
    )
    for label, public_path, gold_path in sources:
        public, gold = read(public_path)["records"], read(gold_path)
        for row in public:
            messages = json.loads(Path(row["prompt_json_path"]).read_text())
            truth = gold[row["id"]]
            values.append(
                {
                    "source": label,
                    "row_sha256": row.get("source_row_sha256", row.get("row_sha256")),
                    "pairs": pair_hashes(messages),
                    "answers": answer_hashes(messages),
                    "target": text_sha(
                        truth["answer"].removeprefix(truth["random_string_to_prepend"])
                    ),
                }
            )
    if len(values) != 88:
        raise ValueError("explicit exposure inventory must be 48+16+8+16")
    return {
        "rows": {row["row_sha256"] for row in values},
        "pairs": set().union(*(row["pairs"] for row in values)),
        "core_answers": set().union(*(row["answers"] for row in values)),
        "targets": {row["target"] for row in values},
        "source_counts": dict(Counter(row["source"] for row in values)),
    }


def occurrence(row) -> int:
    raw, messages = row["raw"], row["messages"]
    target = messages[raw["desired_msg_index"]]["content"]
    positions = [
        index
        for index in range(1, len(messages) - 1, 2)
        if messages[index]["content"] == target
    ]
    return positions.index(raw["desired_msg_index"]) + 1


def question_exact(row, requested: int) -> bool:
    raw, messages = row["raw"], row["messages"]
    target = messages[raw["desired_msg_index"]]["content"]
    parsed = re.fullmatch(r"write an? (.+)", target)
    if parsed is None:
        return False
    ordinal = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}[requested]
    expected = (
        f"Prepend {raw['random_string_to_prepend']} to the {ordinal} (1 indexed) "
        f"{parsed.group(1)}. Do not include any other text in your response."
    )
    return messages[-1]["content"] == expected


def reasons(row, exposed, answer_tokens: int) -> list[str]:
    requested = occurrence(row)
    values = []
    if row["o200k_prompt_plus_answer"] is None or row["o200k_prompt_plus_answer"] > 8192:
        values.append("outside_original_short_band")
    if requested not in (1, 2, 3, 4):
        values.append("requested_ordinal_outside_1_4")
    elif not question_exact(row, requested):
        values.append("official_question_template_mismatch")
    if answer_tokens > 2048:
        values.append("target_exceeds_action_cap_2048")
    if row["row_sha256"] in exposed["rows"]:
        values.append("direct_exposed_row")
    if row["pairs"] & exposed["pairs"]:
        values.append("exact_core_pair_with_exposed")
    if row["target_answer_sha256"] in exposed["core_answers"]:
        values.append("candidate_target_in_exposed_core")
    if row["core_answers"] & exposed["targets"]:
        values.append("exposed_target_in_candidate_core")
    return values


@functools.lru_cache(maxsize=1)
def select():
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL), local_files_only=True)
    exposed = exposures()
    candidates = []
    for row in base.scan():
        requested = occurrence(row)
        answer_tokens = len(tokenizer.encode(row["raw"]["answer"], add_special_tokens=False))
        excluded = reasons(row, exposed, answer_tokens)
        candidates.append(
            {
                "row": row,
                "requested_ordinal": requested,
                "answer_qwen_tokens": answer_tokens,
                "base_reasons": excluded,
                "rank_sha256": text_sha(
                    NAMESPACE + "|" + str(requested) + "|" + row["row_sha256"]
                ),
            }
        )
    selected = []
    decision = []
    eligible_counts = {}
    for requested in (1, 2, 3, 4):
        ranked = sorted(
            (
                item
                for item in candidates
                if item["requested_ordinal"] == requested and not item["base_reasons"]
            ),
            key=lambda item: (item["rank_sha256"], item["row"]["row_sha256"]),
        )
        eligible_counts[str(requested)] = len(ranked)
        accepted = 0
        for item in ranked:
            row = item["row"]
            conflicts = []
            for prior in selected:
                if row["pairs"] & prior["pairs"]:
                    conflicts.append("exact_core_pair_with_selected")
                if row["target_answer_sha256"] in prior["core_answers"]:
                    conflicts.append("candidate_target_in_selected_core")
                if prior["target_answer_sha256"] in row["core_answers"]:
                    conflicts.append("selected_target_in_candidate_core")
            choose = not conflicts and accepted < 8
            decision.append(
                {
                    "source_ordinal": row["source_ordinal"],
                    "row_sha256": row["row_sha256"],
                    "requested_ordinal": requested,
                    "rank_sha256": item["rank_sha256"],
                    "selected": choose,
                    "mutual_conflict_reasons": sorted(set(conflicts)),
                }
            )
            if choose:
                selected.append(row)
                accepted += 1
            if accepted == 8:
                break
    full_skip = []
    selected_hashes = {row["row_sha256"] for row in selected}
    decisions = {row["row_sha256"]: row for row in decision}
    for item in candidates:
        row = item["row"]
        full_skip.append(
            {
                "source_ordinal": row["source_ordinal"],
                "row_sha256": row["row_sha256"],
                "requested_ordinal": item["requested_ordinal"],
                "rank_sha256": item["rank_sha256"],
                "base_reasons": item["base_reasons"],
                "mutual_conflict_reasons": decisions.get(row["row_sha256"], {}).get(
                    "mutual_conflict_reasons", []
                ),
                "selected": row["row_sha256"] in selected_hashes,
            }
        )
    summary = [
        {
            "source_ordinal": row["source_ordinal"],
            "source_shard": row["source_shard"],
            "source_row": row["source_row"],
            "row_sha256": row["row_sha256"],
            "ordered_core_sha256": row["ordered_core_sha256"],
            "target_answer_sha256": row["target_answer_sha256"],
            "requested_ordinal": occurrence(row),
            "o200k_prompt_plus_answer": row["o200k_prompt_plus_answer"],
            "answer_qwen_tokens": len(
                tokenizer.encode(row["raw"]["answer"], add_special_tokens=False)
            ),
        }
        for row in selected
    ]
    return {
        "schema": "openai-mrcr-fourneedle-balanced32-selection-v1",
        "namespace": NAMESPACE,
        "source_rows": len(candidates),
        "explicit_exposed_rows": len(exposed["rows"]),
        "explicit_exposure_source_counts": exposed["source_counts"],
        "eligible_counts_before_mutual_disjointness": eligible_counts,
        "exclusion_reason_counts": dict(
            Counter(reason for item in candidates for reason in item["base_reasons"])
        ),
        "selected": summary,
        "skip_ledger": full_skip,
        "selection_uses_model_answers": False,
        "selection_uses_previous_outcomes": False,
        "unknown_model_pretraining_exposure": True,
    }


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (ROOT / "DATA_READY.json").exists():
        raise ValueError("unused CPU-only data freeze required")
    selection = select()
    counts = Counter(row["requested_ordinal"] for row in selection["selected"])
    if len(selection["selected"]) != 32 or counts != Counter({1: 8, 2: 8, 3: 8, 4: 8}):
        write_json(ROOT / "FEASIBILITY.json", selection)
        raise ValueError(f"balanced32 infeasible: {dict(counts)}")
    chosen = {row["row_sha256"] for row in selection["selected"]}
    source_rows = {row["row_sha256"]: row for row in base.scan() if row["row_sha256"] in chosen}
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL), local_files_only=True)
    public, gold = [], {}
    for index, selected in enumerate(selection["selected"]):
        row = source_rows[selected["row_sha256"]]
        raw, messages = row["raw"], row["messages"]
        identifier = "omrcr-four-balanced-" + row["row_sha256"][:20]
        folder = ROOT / "inputs/records" / identifier
        folder.mkdir(parents=True, exist_ok=True)
        payloads = {
            folder / "prompt.json": raw["prompt"].encode(),
            folder / "question.txt": messages[-1]["content"].encode(),
        }
        for path, value in payloads.items():
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(value)
        encoded = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            enable_thinking=False,
            return_dict=True,
        )
        public.append(
            {
                "id": identifier,
                **selected,
                "seed": SEED_START + index,
                "prompt_json_path": str(folder / "prompt.json"),
                "prompt_json_sha256": sha(folder / "prompt.json"),
                "prompt_json_bytes": len(payloads[folder / "prompt.json"]),
                "final_question_path": str(folder / "question.txt"),
                "final_question_sha256": sha(folder / "question.txt"),
                "source_conversation_qwen_chat_input_tokens": len(encoded["input_ids"]),
                "external_json_string_qwen_tokens": len(
                    tokenizer.encode(raw["prompt"], add_special_tokens=False)
                ),
                "external_file_length_is_not_neural_root_prompt_length": True,
                "no_added_answer_position_or_parser_hint": True,
            }
        )
        gold[identifier] = {
            "answer": raw["answer"],
            "random_string_to_prepend": raw["random_string_to_prepend"],
            "desired_msg_index": raw["desired_msg_index"],
            "target_occurrence_one_indexed": selected["requested_ordinal"],
            "source_row_sha256": row["row_sha256"],
        }
    write_json(ROOT / "SELECTION.json", selection)
    write_json(ROOT / "MODEL_INPUTS.json", {"schema": "mrcr-fourneedle-balanced32-public-v1", "records": public})
    host = ROOT / "host"
    host.mkdir(mode=0o700)
    write_json(host / "HOST_GOLD.json", gold, 0o600)
    if stat.S_IMODE(host.stat().st_mode) != 0o700 or stat.S_IMODE((host / "HOST_GOLD.json").stat().st_mode) != 0o600:
        raise ValueError("host truth permissions differ")
    scorer = SHORT / "official_score.py"
    (ROOT / "official_score.py").write_bytes(scorer.read_bytes())
    generated = [
        ROOT / name
        for name in ("DESIGN.md", "prepare.py", "test_prepare.py", "SELECTION.json", "MODEL_INPUTS.json", "official_score.py")
    ]
    generated += [Path(row[key]) for row in public for key in ("prompt_json_path", "final_question_path")]
    exposure_sources = {
        str(SHORT / "DATA_READY_V2.json"): sha(SHORT / "DATA_READY_V2.json"),
        str(LONG / "DATA_READY.json"): sha(LONG / "DATA_READY.json"),
        str(FRESH / "DATA_READY.json"): sha(FRESH / "DATA_READY.json"),
        str(PREVIOUS / "DATA_READY.json"): sha(PREVIOUS / "DATA_READY.json"),
    }
    source_pins = {
        str(base.ACQUISITION): sha(base.ACQUISITION),
        str(base.CACHE / "README.md"): sha(base.CACHE / "README.md"),
        **{str(base.CACHE / "4needle" / name): value for name, value in base.SOURCE_SHA.items()},
        **exposure_sources,
    }
    manifest = {
        "schema": "openai-mrcr-fourneedle-balanced32-data-manifest-v1",
        "status": "DATA_ONLY_NO_MODEL_QUERY_OR_TRAINING",
        "dataset": "openai/mrcr 4needle",
        "revision": "f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d",
        "license": "MIT from pinned official dataset card/acquisition receipt",
        "records": 32,
        "records_per_requested_ordinal": {"1": 8, "2": 8, "3": 8, "4": 8},
        "short_band_o200k_prompt_plus_answer_max": 8192,
        "action_token_cap": 2048,
        "explicit_prior_rows": 88,
        "selection_uses_model_answers": False,
        "selection_uses_previous_outcomes": False,
        "unknown_model_pretraining_exposure": True,
        "development_selected_lr1e4_comparison": True,
        "files_sha256": {str(path): sha(path) for path in generated},
        "host_gold_sha256": sha(host / "HOST_GOLD.json"),
        "source_sha256": source_pins,
        "model_queries": 0,
        "optimizer_steps": 0,
        "claim_boundary": "same-task ordinal-balanced fresh project contexts; not independent confirmation or pretraining-clean",
    }
    write_json(ROOT / "MANIFEST.json", manifest)
    ready = {
        "schema": "openai-mrcr-fourneedle-balanced32-data-ready-v1",
        "status": "DATA_ONLY_NO_GPU_OR_EVALUATOR",
        "records": 32,
        "seed_namespace": [SEED_START, SEED_START + 31],
        "manifest_sha256": sha(ROOT / "MANIFEST.json"),
        "selection_sha256": sha(ROOT / "SELECTION.json"),
        "model_inputs_sha256": sha(ROOT / "MODEL_INPUTS.json"),
        "closure_sha256": {
            **manifest["files_sha256"],
            **source_pins,
            str(host / "HOST_GOLD.json"): sha(host / "HOST_GOLD.json"),
            str(ROOT / "MANIFEST.json"): sha(ROOT / "MANIFEST.json"),
        },
    }
    ready["identity"] = digest(ready)
    write_json(ROOT / "DATA_READY.json", ready)
    print(json.dumps({"identity": ready["identity"], "sha256": sha(ROOT / "DATA_READY.json"), "eligible": selection["eligible_counts_before_mutual_disjointness"]}, sort_keys=True))


if __name__ == "__main__":
    main()
