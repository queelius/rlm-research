"""Frozen new-panel requests; only record partition changes between fresh arms."""

import copy
import functools
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
C32 = SIDE / "helper-unseen-generalization-c32-baseline-v1"
PANEL = SIDE / "helper-unseen-generalization-panel-v1"
INVARIANT = SIDE / "root-qs6-fixed-helper-top20-batch-invariant-v1"
SERVICE = INVARIANT / "service_batch_invariant_v4.py"
CONTEXT_SOURCE = INVARIANT / "outputs/attempt-003/service/service/inference.json"
ATTEMPT = ROOT / "outputs/attempt-001"
CAP = 1200
SEED = 202609120730
SIZES = (16, 4, 1)
CALLS = 336
PREDICTIONS = 768


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def source():
    return load("unseen_sizes_c32_source", C32 / "unseen_panel_study.py")


@functools.lru_cache(maxsize=1)
def builder():
    return load("unseen_sizes_frozen_prompt_builder", PANEL / "build_panel.py")


@functools.lru_cache(maxsize=1)
def validator():
    previous = sys.modules.get("unseen_panel_study")
    sys.modules["unseen_panel_study"] = source()
    try:
        return load("unseen_sizes_existing_call_validator", C32 / "owner.py")
    finally:
        if previous is None:
            sys.modules.pop("unseen_panel_study", None)
        else:
            sys.modules["unseen_panel_study"] = previous


read = source().read
digest = source().digest
NATIVE = source().NATIVE
MODEL = source().MODEL
CHILD_ALIAS = source().CHILD_ALIAS


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def make_schedule():
    from transformers import AutoTokenizer

    _, _, public, _, requests = source().panel()
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    first = requests[0]
    needle = tokenizer.encode(first["request_text"], add_special_tokens=False)
    original = first["body_template"]["token_ids"]
    hits = [
        index
        for index in range(len(original) - len(needle) + 1)
        if original[index : index + len(needle)] == needle
    ]
    if len(hits) != 1:
        raise ValueError("source helper request is not one exact token subsequence")
    prefix, suffix = original[: hits[0]], original[hits[0] + len(needle) :]
    originals = {(row["dataset"], row["start"]): row for row in requests}
    rows = []
    for dataset_index, dataset in enumerate(("trec", "ag_news")):
        records = [row for row in public["records"] if row["dataset"] == dataset]
        if len(records) != 128:
            raise ValueError("wrong frozen dataset inventory")
        for block in range(8):
            shift = (dataset_index + block) % 3
            for size in SIZES[shift:] + SIZES[:shift]:
                for offset in range(0, 16, size):
                    start = block * 16 + offset
                    selected = records[start : start + size]
                    request_text, labels = builder().prompt(dataset, selected)
                    ids = [row["id"] for row in selected]
                    schema = {
                        "type": "object",
                        "properties": {key: {"type": "string", "enum": labels} for key in ids},
                        "required": ids,
                        "additionalProperties": False,
                    }
                    ordered_schema = json.dumps(schema, separators=(",", ":"))
                    body = copy.deepcopy(first["body_template"])
                    body["model"] = CHILD_ALIAS
                    body["token_ids"] = (
                        prefix + tokenizer.encode(request_text, add_special_tokens=False) + suffix
                    )
                    body["sampling_params"]["seed"] = SEED + dataset_index
                    body["sampling_params"]["structured_outputs"]["json"] = schema
                    if size == 4 and (
                        request_text != originals[(dataset, start)]["request_text"]
                        or body["token_ids"]
                        != originals[(dataset, start)]["body_template"]["token_ids"]
                    ):
                        raise ValueError(
                            "fresh size4 prompt differs from frozen panel wording/wrapper"
                        )
                    rows.append(
                        {
                            "call_id": digest([ROOT.name, dataset, size, start]),
                            "dataset": dataset,
                            "batch_size": size,
                            "block": block,
                            "start": start,
                            "ids": ids,
                            "request_text": request_text,
                            "schema_ordered_json": ordered_schema,
                            "body": body,
                        }
                    )
    if len(rows) != CALLS or sum(len(row["ids"]) for row in rows) != PREDICTIONS:
        raise ValueError("wrong336/768 schedule")
    return rows


def schedule():
    rows = read(ROOT / "inputs/SCHEDULE.json")
    for row in rows:
        schema = json.loads(row["schema_ordered_json"])
        if list(schema["properties"]) != row["ids"] or schema["required"] != row["ids"]:
            raise ValueError("frozen request schema order changed")
        row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
    return rows


@functools.lru_cache(maxsize=1)
def dependencies():
    suite = source().dependencies()
    suite.SERVE = SERVICE
    suite.life.ALLOCATION_SERVICE = SERVICE
    return suite


def attest(service_directory):
    start = read(service_directory / "SERVER_START.json")
    receipt = read(service_directory / "ENGINE_ENV_ATTESTATION.json")
    wrapper = sha(SERVICE)
    if start["launcher_sha256"] != wrapper:
        raise ValueError("service did not launch through sealed batch-invariant-v4 wrapper")
    expected = {
        "schema": "batch-invariant-engine-preexec-attestation-v1",
        "pid": start["pid"],
        "VLLM_BATCH_INVARIANT": "1",
        "command_sha256": digest(start["command"]),
        "wrapper_sha256": wrapper,
        "credentials_persisted": False,
    }
    if receipt != expected:
        raise ValueError("batch-invariant engine attestation changed")
    configuration = Path(start["command"][-1])
    context_limit = read(configuration)["vllm"]["max_model_len"]
    expected_context = read(ROOT / "MANIFEST.json")["context_bound"]
    if context_limit != expected_context["service_max_model_len"]:
        raise ValueError("actual service context cap differs from frozen bound")
    if expected_context["maximum_prompt_plus_output_tokens"] > context_limit:
        raise ValueError("frozen request exceeds actual service context cap")
    return {
        "verified": True,
        "attestation": receipt,
        "attestation_sha256": sha(service_directory / "ENGINE_ENV_ATTESTATION.json"),
        "server_start_sha256": sha(service_directory / "SERVER_START.json"),
        "service_configuration_sha256": sha(configuration),
        "context_bound": expected_context,
    }


def verify():
    ready = read(ROOT / "READY.json")
    if ready["status"] != "CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected unseen size-comparison READY")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed input changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]:
        raise ValueError("frozen size schedule changed")
    return ready
