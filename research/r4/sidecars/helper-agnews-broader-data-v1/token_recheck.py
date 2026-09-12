"""Rebuild every distinct public prompt and token wrapper without model inference."""

import json
import os
from pathlib import Path

from transformers import AutoTokenizer

import prepare

ROOT = Path(__file__).resolve().parent
old = prepare.old


def main():
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == ""
    source = prepare.prompt_source
    tokenizer = AutoTokenizer.from_pretrained(source.MODEL, local_files_only=True)
    builder = source.load_builder()
    original = old.read(source.BATCH_SOURCES)["contexts"]["question-sensitive-sft-train-05"][
        "partitions"
    ]["4"]["0"]
    source_ids = original["body"]["token_ids"]
    text_ids = tokenizer.encode(original["request_text"], add_special_tokens=False)
    offsets = [
        i
        for i in range(len(source_ids) - len(text_ids) + 1)
        if source_ids[i : i + len(text_ids)] == text_ids
    ]
    assert len(offsets) == 1
    prefix, suffix = source_ids[: offsets[0]], source_ids[offsets[0] + len(text_ids) :]
    coordinate_count, unique_count, lengths = 0, 0, []
    pairs = [
        (
            ROOT / f"inputs/step-{step:03d}/PUBLIC.json",
            ROOT / f"inputs/step-{step:03d}/REQUESTS.json",
        )
        for step in range(1, 9)
    ]
    pairs.append((ROOT / "inputs/HELDOUT_PUBLIC.json", ROOT / "inputs/HELDOUT_REQUESTS.json"))
    for public_path, requests_path in pairs:
        public = old.read(public_path)
        assert public["contains_gold"] is False
        records = {row["id"]: row for row in public["records"]}
        seen = set()
        for request in old.read(requests_path):
            ids = request["requested_ids"]
            members = [records[key] for key in ids]
            text, labels = builder.prompt("ag_news", members)
            assert text == request["request_text"]
            encoded = prefix + tokenizer.encode(text, add_special_tokens=False) + suffix
            assert encoded == request["body"]["token_ids"]
            schema = json.loads(request["schema_ordered_json"])
            assert list(schema["properties"]) == schema["required"] == ids
            assert all(schema["properties"][key]["enum"] == labels for key in ids)
            assert schema["additionalProperties"] is False
            assert request["body"]["sampling_params"]["structured_outputs"]["json"] == schema
            assert len(encoded) + 1024 <= 8192
            coordinate_count += 1
            if tuple(ids) not in seen:
                seen.add(tuple(ids))
                unique_count += 1
                lengths.append(len(encoded))
    assert coordinate_count == 1152 and unique_count == 384
    receipt = {
        "status": "PASSED",
        "exact_coordinate_bodies_rebuilt": coordinate_count,
        "distinct_prompts_rebuilt": unique_count,
        "model_inference_calls": 0,
        "max_prompt_plus_completion": max(lengths) + 1024,
        "source_sha256": old.sha(Path(__file__)),
        "manifest_sha256": old.sha(ROOT / "inputs/MANIFEST.json"),
    }
    old.write_x(ROOT / "TOKEN_RECHECK.json", receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
