"""Additive V2 identity: restore ordered schema and decode native token IDs."""

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
V1_ROOT = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-qualification-v1"
V1_ATTEMPT = V1_ROOT / "outputs/attempt-001"
_spec = importlib.util.spec_from_file_location("fresh_helper_qualification_v1_study", V1_ROOT / "study.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

ATTEMPT = ROOT / "outputs/attempt-001"
INPUTS = base.INPUTS
CAP = base.CAP
OUTER_CAP = base.OUTER_CAP
NATIVE = base.NATIVE
TRAIN_PYTHON = base.TRAIN_PYTHON
V1 = base.V1
OLD_DATASET = base.OLD_DATASET
HOST_GOLD = base.HOST_GOLD
SOURCE_BINDING = base.SOURCE_BINDING
FEEDBACK = base.FEEDBACK
BATCH_ROOT = base.BATCH_ROOT
SERVICE_WRAPPER = base.SERVICE_WRAPPER
SERVICE_READY = base.SERVICE_READY
BASE_MODEL = base.BASE_MODEL
CHILD_START = base.CHILD_START
CHILD_ALIAS = base.CHILD_ALIAS
CHILD_SHA = base.CHILD_SHA
CONTEXTS = base.CONTEXTS
SEEDS = base.SEEDS
TOKENIZER_FILES = tuple(BASE_MODEL / name for name in ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"))
read = base.read
sha = base.sha
digest = base.digest
write_x = base.write_x
binding = base.binding
feedback_study = base.feedback_study


def source_prompts():
    value = read(INPUTS)
    for group in value["groups"]:
        schema = json.loads(group["schema_ordered_json"])
        if list(schema["properties"]) != group["requested_ids"] or schema["required"] != group["requested_ids"]:
            raise ValueError("sealed ordered schema differs from requested IDs")
        group["body_template"]["sampling_params"]["structured_outputs"]["json"] = schema
    return value


def schedule(source=None):
    source = source or source_prompts()
    rows = []
    for group_index, group in enumerate(source["groups"]):
        for repeat in range(24):
            seed = SEEDS[group_index * 24 + repeat]
            body = copy.deepcopy(group["body_template"])
            body["sampling_params"]["seed"] = seed
            identity = {
                "namespace": "fresh-batch-invariant-helper-qualification-2026091213",
                "context_id": group["context_id"],
                "repeat": repeat,
                "seed": seed,
            }
            rows.append(
                {
                    **identity,
                    "coordinate_id": digest(identity),
                    "group_index": group_index,
                    "source_split": "train",
                    "requested_ids": group["requested_ids"],
                    "schema_ordered_json": group["schema_ordered_json"],
                    "schema_ordered_sha256": group["schema_ordered_sha256"],
                    "body": body,
                }
            )
    return rows


def plan():
    v1_ready = V1_ROOT / "READY_V4.json"
    v1_terminal = V1_ATTEMPT / "OWNER_TERMINAL.json"
    return {
        "schema": "fresh-batch-invariant-helper-qualification-ready-v2",
        "status": "CPU_READY_QUALIFICATION_ONLY",
        "repair": "restore ordered schema at runtime and decode exact native action IDs with pinned tokenizer",
        "v1_preserved": True,
        "v1_ready": str(v1_ready),
        "v1_ready_sha256": sha(v1_ready),
        "v1_failed_terminal": str(v1_terminal),
        "v1_failed_terminal_sha256": sha(v1_terminal),
        "output": str(ATTEMPT),
        "cap_seconds": CAP,
        "outer_cap_seconds": OUTER_CAP,
        "episodes": 48,
        "groups": 2,
        "group_sizes": [24, 24],
        "seeds": list(SEEDS),
        "schedule_sha256": digest(schedule()),
        "source_prompts_sha256": sha(INPUTS),
        "tokenizer_files_sha256": {str(path): sha(path) for path in TOKENIZER_FILES},
        "child_adapter_sha256": sha(CHILD_START / "adapter_model.safetensors"),
        "service_ready": str(SERVICE_READY),
        "service_ready_sha256": sha(SERVICE_READY),
        "runtime_scope": "VLLM_BATCH_INVARIANT=1, helper-only concurrency4 on this allocation/config",
        "objective": {
            "reward": "fraction correct over 16 train labels",
            "advantage": "within exact prompt/schema RLOO against other 23, scaled by 16",
            "temperature": 0.5,
            "importance_ratio": "raw exp(sum HF target logprob - sum vLLM behavior logprob)",
            "ess_min": 38.4,
            "max_normalized_weight": 0.1,
            "clipping": None,
            "self_normalization": None,
        },
        "optimizer_steps": 0,
        "pass_status": "QUALIFIED_NO_UPDATE",
        "command": [str(NATIVE), str(ROOT / "owner.py"), "run", "--outer-seconds", str(CAP)],
        "launch_authority": "MAIN only; one-GPU CUDA_VISIBLE_DEVICES and private credential environment",
    }


def verify():
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready.get("identity"):
        raise ValueError("READY identity changed")
    for key, value in plan().items():
        if ready.get(key) != value:
            raise ValueError("sealed V2 plan changed: " + key)
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed V2 closure changed: " + path)
    return ready
