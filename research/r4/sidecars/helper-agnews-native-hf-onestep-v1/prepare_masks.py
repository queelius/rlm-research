"""CPU-only native-environment exact mask handoff; no HF/xgrammar import gap."""

import copy
import os

import ag_study as study
import native_collect


def prepare():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("native mask generation must hide CUDA")
    collection = study.read(study.ATTEMPT / "COLLECTION.json")
    rows = study.schedule()
    records = copy.deepcopy(collection["records"])
    if (
        collection["fresh_actions"] != 128
        or len(records) != 128
        or collection["errors"]
        or collection["historical_actions_or_logprobs_used"] is not False
    ):
        raise ValueError("complete fresh128 collection required")
    if [record["coordinate_id"] for record in records] != [row["coordinate_id"] for row in rows]:
        raise ValueError("action schedule differs")
    decoder = native_collect.tokenizer()
    gold = study.read(study.HOST_GOLD)
    for record, row in zip(records, rows, strict=True):
        for key in ("raw_request_path", "raw_response_path"):
            if study.sha(record[key]) != record[key.replace("path", "sha256")]:
                raise ValueError("saved raw bytes changed")
        if study.read(record["raw_request_path"]) != row["body"]:
            raise ValueError("raw request differs from frozen schedule")
        redecoded = native_collect.response_record(
            row,
            study.read(record["raw_response_path"]),
            decoder,
            record["started_epoch"],
            record["ended_epoch"],
            gold,
        )
        if any(record.get(key) != value for key, value in redecoded.items()):
            raise ValueError("native record differs from redecoded response/gold")
    modules = study.numeric_modules()
    advantages = modules.leaf.rloo_advantages(
        [row["reward"] for row in records], [row["group_id"] for row in records], reward_scale=4
    )
    for record, advantage in zip(records, advantages, strict=True):
        record["advantage"] = advantage
    inputs = study.ATTEMPT / "qualification-inputs"
    manifest = modules.prepare.generate_masks(records, inputs)
    dataset = {
        "schema": "agnews-native-hf-dataset-v1",
        "records": records,
        "collection_sha256": study.sha(study.ATTEMPT / "COLLECTION.json"),
        "inventory": {
            "groups": 32,
            "episodes": 128,
            "records_per_request": 4,
            "action_tokens": sum(len(row["action_ids"]) for row in records),
        },
        "c32_adapter_sha256": study.sha(study.CHILD_START / "adapter_model.safetensors"),
    }
    study.write_x(inputs / "DATASET.json", dataset)
    manifest["dataset_sha256"] = study.sha(inputs / "DATASET.json")
    study.write_x(inputs / "MASK_MANIFEST.json", manifest)
    study.write_x(
        study.ATTEMPT / "PREPARED.json",
        {
            "dataset_sha256": study.sha(inputs / "DATASET.json"),
            "masks_sha256": study.sha(inputs / "MASKS.npz"),
            "mask_manifest_sha256": study.sha(inputs / "MASK_MANIFEST.json"),
            "collection_sha256": dataset["collection_sha256"],
            "CUDA_VISIBLE_DEVICES": "",
            "optimizer_steps": 0,
            "xgrammar_version": manifest["xgrammar_version"],
        },
    )


if __name__ == "__main__":
    prepare()
