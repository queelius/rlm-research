"""Instruction-only binary verbalizer treatment; immutable native seams."""

import copy
import difflib
import functools
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT.parent / "helper-targeted-category-counts-v1"
spec = importlib.util.spec_from_file_location(
    "yesno_sealed_target_seams", TARGET / "target_study.py"
)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
prior = target.prior
read, write, sha, digest = prior.read, prior.write, prior.sha, prior.digest
NATIVE, MODEL, CHILD_ALIAS = prior.NATIVE, prior.MODEL, prior.CHILD_ALIAS
PANEL, SERVICE, CONTEXT_SOURCE = prior.PANEL, prior.SERVICE, prior.CONTEXT_SOURCE
source, dependencies = prior.source, prior.dependencies
context_bound, engine_marker = target.context_bound, target.engine_marker
CAP, CALLS, PREDICTIONS = 750, 56, 896
ATTEMPT = ROOT / "outputs/attempt-001"
OLD_RESULT = TARGET / "outputs/attempt-001/RESULT.json"


@functools.lru_cache(maxsize=1)
def make_schedule():
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    rows = []
    for original in target.schedule():
        if original["dataset"] != "trec":
            continue
        row = copy.deepcopy(original)
        row["source_call_id"] = original["call_id"]
        row["call_id"] = digest([ROOT.name, original["call_id"]])
        if row["arm"] == "targeted":
            definitions, marker, rest = original["request_text"].partition("\nTarget category:")
            instruction, separator, records = rest.partition("\nQuestions: ")
            old_allowed = "Allowed labels: " + json.dumps(
                [row["target"], "other"], separators=(",", ":")
            )
            if (
                not marker
                or not separator
                or instruction.count("return the target label") != 1
                or instruction.count(old_allowed) != 1
            ):
                raise ValueError("original instruction boundaries changed")
            revised = instruction.replace("return the target label", "return `yes`").replace(
                "`other`", "`no`"
            )
            revised = revised.replace(old_allowed, 'Allowed labels: ["yes","no"]')
            row["request_text"] = definitions + marker + revised + separator + records
            old_tokens = original["body"]["token_ids"]
            needle = tokenizer.encode(original["request_text"], add_special_tokens=False)
            hits = [
                i
                for i in range(len(old_tokens) - len(needle) + 1)
                if old_tokens[i : i + len(needle)] == needle
            ]
            if len(hits) != 1:
                raise ValueError("original wrapper not uniquely recoverable")
            row["body"]["token_ids"] = (
                old_tokens[: hits[0]]
                + tokenizer.encode(row["request_text"], add_special_tokens=False)
                + old_tokens[hits[0] + len(needle) :]
            )
            schema = json.loads(row["schema_ordered_json"])
            for value in schema["properties"].values():
                value["enum"] = ["yes", "no"]
            row["schema_ordered_json"] = json.dumps(schema, separators=(",", ":"))
            row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
            row["instruction_diff"] = "".join(
                difflib.unified_diff(
                    (definitions + marker + instruction + "\n").splitlines(keepends=True),
                    (definitions + marker + revised + "\n").splitlines(keepends=True),
                    fromfile="literal-target-other",
                    tofile="yes-no",
                )
            )
        elif row["body"] != original["body"]:
            raise ValueError("full-control body changed")
        rows.append(row)
    if len(rows) != CALLS:
        raise ValueError("wrong56-call schedule")
    return rows


def schedule():
    rows = read(ROOT / "inputs/SCHEDULE.json")
    for row in rows:
        schema = json.loads(row["schema_ordered_json"])
        if list(schema["properties"]) != row["ids"] or schema["required"] != row["ids"]:
            raise ValueError("ordered schema inventory changed")
        row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
    return rows


def response_record(row, raw, tokenizer):
    allowed = ["yes", "no"] if row["arm"] == "targeted" else row["labels"]
    return target.response_record({**row, "arm": "full", "labels": allowed}, raw, tokenizer)


@functools.lru_cache(maxsize=1)
def wire_send():
    import yesno_metrics

    aliases = {"target_study": sys.modules[__name__], "metrics": yesno_metrics}
    previous = {key: sys.modules.get(key) for key in aliases}
    sys.modules.update(aliases)
    try:
        module = prior.load("yesno_existing_target_wire_sender", TARGET / "owner.py")
    finally:
        for key, value in previous.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    return module.send


def attest(service_directory):
    result = prior.attest(service_directory)
    configuration = Path(read(service_directory / "SERVER_START.json")["command"][-1])
    bound = context_bound(schedule(), read(configuration)["vllm"]["max_model_len"])
    if bound != read(ROOT / "MANIFEST.json")["context_bound"]:
        raise ValueError("actual context cap differs")
    result["context_bound"] = bound
    return result


def verify():
    ready = read(ROOT / "READY.json")
    if ready["status"] != "CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected READY")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed source changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]:
        raise ValueError("schedule changed")
    return ready
