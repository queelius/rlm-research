"""Gold-free B4 prompt construction over the already frozen128 AG records."""

import copy
import json

import ag_study as study


def main():
    from transformers import AutoTokenizer

    if (study.ROOT / "inputs").exists():
        raise FileExistsError("inputs already frozen")
    source = study.load("ag_native_standard_builder_seam", study.EVAL / "prepare_eval.py")
    builder = source.load_builder()
    public = study.read(study.FROZEN / "TRAIN_PUBLIC.json")
    gold = study.read(study.FROZEN / "TRAIN_GOLD.json")
    heldout = study.read(study.FROZEN / "HELDOUT_PUBLIC.json")
    records = public["records"]
    ids = [row["id"] for row in records]
    if len(ids) != 128 or len(set(ids)) != 128 or set(ids) != set(gold["labels"]):
        raise ValueError("training128 identity differs")
    if public.get("contains_gold") is not False or set(ids) & {
        row["id"] for row in heldout["records"]
    }:
        raise ValueError("public training/heldout separation differs")
    decoder = AutoTokenizer.from_pretrained(study.BASE_MODEL, local_files_only=True)
    historical = study.read(source.BATCH_SOURCES)["contexts"]["question-sensitive-sft-train-05"][
        "partitions"
    ]["4"]["0"]
    body = historical["body"]
    old_ids = decoder.encode(historical["request_text"], add_special_tokens=False)
    hits = [
        i
        for i in range(len(body["token_ids"]) - len(old_ids) + 1)
        if body["token_ids"][i : i + len(old_ids)] == old_ids
    ]
    if len(hits) != 1:
        raise ValueError("original helper chat prefix/suffix differs")
    prefix, suffix = body["token_ids"][: hits[0]], body["token_ids"][hits[0] + len(old_ids) :]
    groups, host = [], {}
    for index in range(32):
        members = records[4 * index : 4 * index + 4]
        requested = [row["id"] for row in members]
        text, labels = builder.prompt("ag_news", members)
        schema = {
            "type": "object",
            "properties": {key: {"type": "string", "enum": labels} for key in requested},
            "required": requested,
            "additionalProperties": False,
        }
        schema_text = json.dumps(schema, separators=(",", ":"), ensure_ascii=False)
        context = f"agnews-train-b4-{index:03d}"
        template = {
            "model": study.CHILD_ALIAS,
            "token_ids": prefix + decoder.encode(text, add_special_tokens=False) + suffix,
            "sampling_params": {
                **body["sampling_params"],
                "temperature": 0.5,
                "top_p": 1.0,
                "top_k": -1,
                "min_p": 0.0,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "repetition_penalty": 1.0,
                "logprobs": 1,
                "max_tokens": 1024,
                "stop_token_ids": [151645, 151643],
                "structured_outputs": {"json": schema},
            },
            "cache_salt": "0",
        }
        groups.append(
            {
                "context_id": context,
                "requested_ids": requested,
                "request_text": text,
                "schema_ordered_json": schema_text,
                "schema_ordered_sha256": study.hashlib.sha256(schema_text.encode()).hexdigest(),
                "body": template,
            }
        )
        host[context] = {"labels": {key: gold["labels"][key] for key in requested}}
    rows = []
    for repeat in range(4):
        for index, group in enumerate(groups):
            row = copy.deepcopy(group)
            row["repeat"] = repeat
            row["seed"] = 202609122100 + 4 * index + repeat
            row["coordinate_id"] = study.digest(
                {
                    "namespace": "agnews-b4-native-hf-step1|20260912",
                    "group": index,
                    "repeat": repeat,
                }
            )
            row["body"]["sampling_params"]["seed"] = row["seed"]
            rows.append(row)
    study.write_x(study.ROOT / "inputs/REQUESTS.json", rows)
    study.write_x(study.HOST_GOLD, host)
    study.write_x(study.ROOT / "inputs/PUBLIC.json", public)
    study.write_x(
        study.ROOT / "inputs/BUILD_AUDIT.json",
        {
            "groups": 32,
            "records": 128,
            "record_order": "frozen public order; label blind",
            "manifest_sha256": study.sha(study.FROZEN / "MANIFEST.json"),
            "host_gold_prompted": False,
            "training_heldout_id_overlap": 0,
            "min_prompt_tokens": min(len(row["body"]["token_ids"]) for row in rows),
            "max_prompt_tokens": max(len(row["body"]["token_ids"]) for row in rows),
            "max_prompt_plus_completion": max(len(row["body"]["token_ids"]) for row in rows) + 1024,
            "public_sha256": study.sha(study.FROZEN / "TRAIN_PUBLIC.json"),
            "gold_sha256": study.sha(study.FROZEN / "TRAIN_GOLD.json"),
            "source_template": str(source.BATCH_SOURCES),
            "source_template_sha256": study.sha(source.BATCH_SOURCES),
            "builder_sha256": study.sha(source.BUILDER),
        },
    )
    print(study.read(study.ROOT / "inputs/BUILD_AUDIT.json"))


if __name__ == "__main__":
    main()
