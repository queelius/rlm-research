"""Build four balanced AG singleton steps through the standard AG prompt builder."""

from collections import defaultdict
import copy
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
FROZEN = SIDE / "helper-agnews-data-vs-mechanics-v1/inputs"
BUILDER = SIDE / "helper-unseen-generalization-panel-v1/build_panel.py"
BATCH_SOURCES = SIDE / "root-c32-helper-batchsize-v1/inputs/SOURCES.json"
MODEL = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
AG_VALUES = ("World", "Sports", "Business", "Sci/Tech")


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("ag_standard_panel_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_inputs():
    from transformers import AutoTokenizer

    builder = load_builder()
    public = read(FROZEN / "TRAIN_PUBLIC.json")
    gold_source = read(FROZEN / "TRAIN_GOLD.json")
    if public.get("contains_gold") is not False or len(public["records"]) != 128:
        raise ValueError("frozen training public inventory differs")
    if set(gold_source["labels"]) != {row["id"] for row in public["records"]}:
        raise ValueError("frozen training gold inventory differs")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    historical = read(BATCH_SOURCES)["contexts"]["question-sensitive-sft-train-05"][
        "partitions"
    ]["4"]["0"]
    old_request_ids = tokenizer.encode(historical["request_text"], add_special_tokens=False)
    body_ids = historical["body"]["token_ids"]
    hits = [
        index
        for index in range(len(body_ids) - len(old_request_ids) + 1)
        if body_ids[index : index + len(old_request_ids)] == old_request_ids
    ]
    if len(hits) != 1:
        raise ValueError("historical request is not one exact token subsequence")
    offset = hits[0]
    prefix_ids = body_ids[:offset]
    suffix_ids = body_ids[offset + len(old_request_ids) :]
    by_label = defaultdict(list)
    for row in public["records"]:
        by_label[gold_source["labels"][row["id"]]].append(row)
    if {key: len(value) for key, value in by_label.items()} != {
        label: 32 for label in AG_VALUES
    }:
        raise ValueError("frozen AG train labels differ")
    step_groups = [[] for _ in range(4)]
    train_gold = {}
    for label in AG_VALUES:
        for position, row in enumerate(by_label[label]):
            request_text, labels = builder.prompt("ag_news", [row])
            if tuple(labels) != AG_VALUES:
                raise ValueError("standard AG label order differs")
            identifier = row["id"]
            schema = {
                "type": "object",
                "properties": {identifier: {"type": "string", "enum": list(AG_VALUES)}},
                "required": [identifier],
                "additionalProperties": False,
            }
            schema_text = json.dumps(schema, separators=(",", ":"), ensure_ascii=False)
            group_id = "agnews-train:" + identifier
            group = {
                "group_id": group_id,
                "context_id": "agnews-train-step-%d" % (position // 8 + 1),
                "source_split": "train",
                "source_id": row["source_id"],
                "public_record": {key: row[key] for key in ("id", "text")},
                "requested_ids": [identifier],
                "request_text": request_text,
                "prompt_ids": prefix_ids
                + tokenizer.encode(request_text, add_special_tokens=False)
                + suffix_ids,
                "schema_ordered_json": schema_text,
                "schema_ordered_sha256": hashlib.sha256(schema_text.encode()).hexdigest(),
            }
            step_groups[position // 8].append(group)
            train_gold[group_id] = label
    if any(len(step) != 32 for step in step_groups):
        raise ValueError("expected four exact balanced32 steps")
    return {
        "step_groups": step_groups,
        "gold": train_gold,
        "audit": {
            "steps": 4,
            "groups_per_step": 32,
            "unique_groups": 128,
            "fresh_rollouts_per_group": 4,
            "total_fresh_actions": 512,
            "standard_prompt_builder": str(BUILDER),
            "standard_prompt_builder_sha256": sha(BUILDER),
            "historical_wrapper_source": str(BATCH_SOURCES),
            "historical_wrapper_source_sha256": sha(BATCH_SOURCES),
            "full_request_replaced": True,
            "ag_definitions_present": True,
            "trec_definitions_absent": True,
            "host_gold_separate": True,
        },
    }


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main():
    inputs = ROOT / "inputs"
    if inputs.exists():
        raise ValueError("immutable generated inputs already exist")
    bundle = make_inputs()
    write_x(inputs / "STEP_GROUPS.json", bundle["step_groups"])
    write_x(inputs / "TRAIN_GOLD.json", bundle["gold"])
    write_x(inputs / "BUILD_AUDIT.json", bundle["audit"])


if __name__ == "__main__":
    main()
