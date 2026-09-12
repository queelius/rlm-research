"""Frozen broader-AG teacher schedule and SFT endpoint contract."""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
import os
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
DATA = SIDE / "helper-agnews-broader-data-v1"
SOURCE = SIDE / "helper-agnews-native-hf-onestep-v1"
RL = SIDE / "helper-agnews-native-hf-eightstep-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/"
    "gpu/training/.venv/bin/python"
)
CAP, OUTER_CAP = 900, 1000
SEED = 202609125000
LR = 1e-5
LABELS = ("World", "Sports", "Business", "Sci/Tech")
DATA_MANIFEST_SHA256 = "b5e9cc22161959fc09f5e1f15afd03e722a32818bca692a01f9e265fd6c81c2d"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source = load("ag_sft_source_study", SOURCE / "ag_study.py")
BASE_MODEL, CHILD_START, CHILD_SHA = source.BASE_MODEL, source.CHILD_START, source.CHILD_SHA
CHILD_ALIAS = source.CHILD_ALIAS


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending-" + uuid.uuid4().hex)
    try:
        with temporary.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@functools.lru_cache(maxsize=1)
def tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(BASE_MODEL, local_files_only=True)


def label_spans(target, values):
    spans, cursor = [], 0
    for value in values:
        needle = json.dumps(value)
        start = target.find(needle, cursor)
        if start < 0:
            raise ValueError("gold label span absent from compact target")
        spans.append((start, start + len(needle)))
        cursor = start + len(needle)
    return spans


@functools.lru_cache(maxsize=1)
def teacher_schedule():
    tok, steps = tokenizer(), []
    for step in range(1, 9):
        directory = DATA / f"inputs/step-{step:03d}"
        scheduled, gold = read(directory / "REQUESTS.json"), read(directory / "HOST_GOLD.json")
        groups = {}
        for row in scheduled:
            groups.setdefault(row["context_id"], []).append(row)
        if len(groups) != 32 or any(len(rows) != 4 for rows in groups.values()):
            raise ValueError("each frozen step must contain 32 groups x4 repeats")
        examples = []
        for context, rows in groups.items():
            rows = sorted(rows, key=lambda row: row["repeat"])
            first = rows[0]
            for other in rows[1:]:
                if (
                    other["request_text"] != first["request_text"]
                    or other["requested_ids"] != first["requested_ids"]
                    or other["body"]["token_ids"] != first["body"]["token_ids"]
                    or other["schema_ordered_json"] != first["schema_ordered_json"]
                ):
                    raise ValueError("repeat prompt/schema changed within teacher group")
            values = [gold["labels"][identifier] for identifier in first["requested_ids"]]
            gold_map = dict(zip(first["requested_ids"], values, strict=True))
            target = json.dumps(gold_map, separators=(",", ":"))
            encoded = tok(target, add_special_tokens=False, return_offsets_mapping=True)
            action_ids = list(encoded["input_ids"]) + [tok.eos_token_id]
            offsets = list(encoded["offset_mapping"])
            spans = label_spans(target, values)
            label_action_mask = [
                any(start < right and end > left for left, right in spans)
                for start, end in offsets
            ] + [False]
            prompt_ids = list(first["body"]["token_ids"])
            if tok.decode(action_ids[:-1], skip_special_tokens=False) != target:
                raise ValueError("compact target token round trip changed")
            full = prompt_ids + action_ids
            if len(full) > 8192 or action_ids[-1] != tok.eos_token_id:
                raise ValueError("teacher example context/end token differs")
            examples.append(
                {
                    "step": step,
                    "context_id": context,
                    "requested_ids": first["requested_ids"],
                    "request_text": first["request_text"],
                    "prompt_ids": prompt_ids,
                    "target_text": target,
                    "gold_map": gold_map,
                    "input_ids": full,
                    "labels": [-100] * len(prompt_ids) + action_ids,
                    "label_token_mask": [False] * len(prompt_ids) + label_action_mask,
                    "prompt_tokens": len(prompt_ids),
                    "supervised_tokens": len(action_ids),
                    "content_tokens": len(action_ids) - 1,
                    "source_request_ids": [row["coordinate_id"] for row in rows],
                }
            )
        steps.append(examples)
    if [sum(row["content_tokens"] for row in rows) for rows in steps] != [
        2551, 2547, 2557, 2521, 2552, 2539, 2547, 2521
    ]:
        raise ValueError("pinned compact-target token inventory differs")
    return steps


def plan():
    steps = teacher_schedule()
    return {
        "schema": "agnews-eightstep-answer-only-sft-ready-v1",
        "status": "CPU_READY_CONDITIONAL_MAIN_ADMISSION",
        "question": "Does frozen broader AG contain learnable supervised signal after eight updates?",
        "output": str(ATTEMPT),
        "command": [str(TRAIN_PYTHON), str(ROOT / "owner.py"), "run", "--outer-seconds", str(CAP)],
        "owner_cap_seconds": CAP,
        "external_cap_seconds": OUTER_CAP,
        "starting_adapter": str(CHILD_START),
        "starting_adapter_sha256": CHILD_SHA,
        "training_data_manifest_sha256": DATA_MANIFEST_SHA256,
        "inventory": {
            "steps": 8,
            "teacher_maps": 256,
            "unique_records": 1024,
            "label_decisions": 1024,
            "supervised_tokens": sum(row["supervised_tokens"] for rows in steps for row in rows),
            "content_tokens": sum(row["content_tokens"] for rows in steps for row in rows),
        },
        "policy": {
            "objective": "ordinary full-vocabulary answer-only cross entropy",
            "maps_per_update": 32,
            "microbatch": 1,
            "lr": LR,
            "weight_decay": 0,
            "gradient_clip": 1,
            "optimizer": "fresh AdamW carried across eight steps",
            "dropout": "off",
            "base_dtype": "bfloat16",
            "lora_dtype": "float32",
            "attention": "sdpa",
        },
        "seed": SEED,
        "teacher_schedule_sha256": digest(steps),
        "checkpoint_policy": "commit every applied update; checkpoint8 only endpoint",
        "evaluation": "shared fresh512 c32/RL8/SFT8 evaluator; no intermediate selection",
        "claim_boundary": "data-signal positive control; not pure objective/support/dose isolation",
        "gpu_launch_authority": "MAIN only",
    }


def verify():
    ready = read(ROOT / "READY.json")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("READY identity differs")
    for key, value in plan().items():
        if ready.get(key) != value:
            raise ValueError("READY plan differs: " + key)
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("source closure changed: " + path)
    return ready


def endpoint():
    ready = verify()
    previous = None
    for step in range(1, 9):
        checkpoint = ATTEMPT / f"checkpoint-{step:04d}"
        commit, state = read(checkpoint / "STEP_COMMIT.json"), read(checkpoint / "state.json")
        if (
            commit["status"] != "UPDATED"
            or commit["step"] != step
            or commit["optimizer_steps"] != step
            or commit["ready_identity"] != ready["identity"]
            or commit["parent_step_commit_sha256"] != previous
            or state["status"] != "UPDATED"
            or state["step"] != step
            or state["optimizer_state_steps"] != [step]
            or len(state["step_metrics"]) != step
            or state["starting_adapter_sha256"] != CHILD_SHA
            or not state["root_unchanged"]
        ):
            raise ValueError("SFT committed lineage differs")
        for path, expected in commit["files_sha256"].items():
            if sha(path) != expected:
                raise ValueError("SFT committed file changed: " + path)
        previous = sha(checkpoint / "STEP_COMMIT.json")
    result, terminal = read(ATTEMPT / "RESULT.json"), read(ATTEMPT / "OWNER_TERMINAL.json")
    if (
        result["status"] != "UPDATED_STEP8"
        or result["optimizer_steps"] != 8
        or result["step_commit_sha256"] != previous
        or not terminal["complete"]
        or terminal["errors"]
        or terminal["result_sha256"] != sha(ATTEMPT / "RESULT.json")
    ):
        raise ValueError("SFT fixed checkpoint8 endpoint is incomplete")
    binding = read(ATTEMPT / "checkpoint-0008/EVAL_BINDING.json")
    return {
        "eligible": True,
        "checkpoint": str(ATTEMPT / "checkpoint-0008"),
        "binding": binding,
        "binding_sha256": sha(ATTEMPT / "checkpoint-0008/EVAL_BINDING.json"),
        "state_sha256": sha(ATTEMPT / "checkpoint-0008/state.json"),
        "step_commit_sha256": previous,
        "training_result_sha256": sha(ATTEMPT / "RESULT.json"),
        "ready_identity": ready["identity"],
        "ready_sha256": sha(ROOT / "READY.json"),
        "selection": "none; exact fixed checkpoint8",
    }
