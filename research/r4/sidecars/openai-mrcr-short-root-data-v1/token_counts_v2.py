"""Additive correction for Transformers5 BatchEncoding default; no selected data change."""

import copy
import os

from transformers import AutoTokenizer

import prepare as source


if __name__ == "__main__":
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (source.ROOT / "DATA_READY_V2.json").exists():
        raise ValueError("unused CPU-only token-count receipt required")
    old = source.read(source.ROOT / "DATA_READY.json")
    for path, expected in old["closure_sha256"].items():
        if source.sha(path) != expected:
            raise ValueError("original freeze changed")
    public = source.read(source.ROOT / "MODEL_INPUTS.json")
    tokenizer = AutoTokenizer.from_pretrained(source.MODEL, local_files_only=True)
    proof = []
    for split, records in public.items():
        for row in records:
            messages = source.read(row["prompt_json_path"])
            default = tokenizer.apply_chat_template(messages, tokenize=True,
                add_generation_prompt=True, enable_thinking=False)
            explicit = tokenizer.apply_chat_template(messages, tokenize=True,
                add_generation_prompt=True, enable_thinking=False, return_dict=False)
            if (not isinstance(explicit, list) or not explicit
                    or default["input_ids"] != explicit
                    or any(type(value) is not int for value in explicit)):
                raise ValueError("actual explicit-list and BatchEncoding IDs differ")
            row["source_conversation_qwen_chat_input_tokens"] = len(explicit)
            proof.append({"id": row["id"], "split": split, "default_type": type(default).__name__,
                          "default_len_was_mapping_keys": len(default),
                          "explicit_input_ids_length": len(explicit), "actual_sequences_equal": True})
    source.write_json(source.ROOT / "MODEL_INPUTS_V2.json", public)
    source.write_json(source.ROOT / "TOKEN_COUNT_CORRECTION.json", {
        "reason": "Transformers5 returns BatchEncoding by default; len(mapping) is2 keys, not token count",
        "old_model_inputs_sha256": source.sha(source.ROOT / "MODEL_INPUTS.json"),
        "new_model_inputs_sha256": source.sha(source.ROOT / "MODEL_INPUTS_V2.json"),
        "old_fields_superseded": ["source_conversation_qwen_chat_input_tokens"],
        "actual48_return_shape_and_token_id_equivalence_checks": proof,
        "selection_source_prompt_question_gold_bytes_changed": False,
        "GPU_or_model_forward": False})
    manifest = copy.deepcopy(source.read(source.ROOT / "MANIFEST.json"))
    for split, rows in public.items():
        manifest["counts"][split]["source_chat_tokens_min"] = min(row["source_conversation_qwen_chat_input_tokens"] for row in rows)
        manifest["counts"][split]["source_chat_tokens_max"] = max(row["source_conversation_qwen_chat_input_tokens"] for row in rows)
    manifest["schema"] = "openai-mrcr-short-root-frozen-data-v2"
    manifest["model_inputs_path"] = str(source.ROOT / "MODEL_INPUTS_V2.json")
    manifest["supersedes_only_token_count_metadata_in"] = str(source.ROOT / "MANIFEST.json")
    for name in ("MODEL_INPUTS_V2.json", "TOKEN_COUNT_CORRECTION.json", "token_counts_v2.py"):
        manifest["files_sha256"][str(source.ROOT / name)] = source.sha(source.ROOT / name)
    source.write_json(source.ROOT / "MANIFEST_V2.json", manifest)
    closure = dict(old["closure_sha256"])
    closure.update(source.read(source.INVENTORY / "MANIFEST.json")["artifacts_sha256"])
    for name in ("DATA_READY.json", "MODEL_INPUTS_V2.json", "TOKEN_COUNT_CORRECTION.json",
                 "token_counts_v2.py", "MANIFEST_V2.json", "verify.py"):
        closure[str(source.ROOT / name)] = source.sha(source.ROOT / name)
    ready = {"schema": "openai-mrcr-short-root-data-ready-v2", "records": manifest["records"],
        "status": "DATA_ONLY_NO_GPU_OR_TRAINING_ADMISSION", "closure_sha256": closure,
        "manifest_path": str(source.ROOT / "MANIFEST_V2.json"),
        "manifest_sha256": source.sha(source.ROOT / "MANIFEST_V2.json"),
        "model_inputs_path": str(source.ROOT / "MODEL_INPUTS_V2.json"),
        "original_ready_sha256": source.sha(source.ROOT / "DATA_READY.json"),
        "rank_inputs_gold_unchanged": True, "correction": "actual48 tokenizer return-shape metadata only"}
    ready["identity"] = source.digest(ready)
    source.write_json(source.ROOT / "DATA_READY_V2.json", ready)
    print({"ready_sha256": source.sha(source.ROOT / "DATA_READY_V2.json"),
           "identity": ready["identity"], "counts": manifest["counts"], "pins": len(closure)})
