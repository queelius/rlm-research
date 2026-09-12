"""Freeze exactly MAIN's outcome-blind rank and original JSON/query bytes."""

import ast
import hashlib
import importlib.util
import json
import os
import platform
import re
import stat
import time
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parent.parent
INVENTORY = STORE / "analyses/openai-mrcr-source-inventory-2026-09-12"
CACHE = Path("/project/alex_phd/research-cache/datasets/openai-mrcr-f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d")
MODEL = Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554")
NAMESPACE = "openai-mrcr-short-root-v1-20260912"


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def write_bytes(path, value, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(value)


def write_json(path, value, mode=0o644):
    write_bytes(path, (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode(), mode)


def question_check(raw, messages):
    desired = raw["desired_msg_index"]
    target = messages[desired]["content"]
    positions = [i for i in range(1, len(messages) - 1, 2) if messages[i]["content"] == target]
    occurrence = positions.index(desired) + 1
    parsed = re.fullmatch(r"write an? (.+)", target)
    if parsed is None or occurrence not in (1, 2):
        return {"template_covered": False, "exact_question_match": False,
                "marker_in_visible_question": raw["random_string_to_prepend"] in messages[-1]["content"]}
    ordinal = {1: "1st", 2: "2nd"}[occurrence]
    expected = (f"Prepend {raw['random_string_to_prepend']} to the {ordinal} (1 indexed) "
                f"{parsed.group(1)}. Do not include any other text in your response.")
    return {"template_covered": True, "exact_question_match": messages[-1]["content"] == expected,
            "marker_in_visible_question": raw["random_string_to_prepend"] in messages[-1]["content"]}


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (ROOT / "RANKING.json").exists():
        raise ValueError("unused CPU-only data freeze required")
    started = time.monotonic()
    manifest = read(INVENTORY / "MANIFEST.json")
    for path, expected in manifest["artifacts_sha256"].items():
        if sha(path) != expected:
            raise ValueError("upstream inventory artifact changed")
    rows = [json.loads(line) for line in (INVENTORY / "ROWS.jsonl").read_text().splitlines()]
    candidates = {row["ordinal"] for row in rows if row["o200k_base_tokens_if_short"]
                  and row["o200k_base_tokens_if_short"]["prompt_content_plus_answer"] <= 8192}
    if len(candidates) != 101:
        raise ValueError("expected exact101 original short candidates")
    shared = set()
    for line in (INVENTORY / "CORE_PAIR_INCIDENCE.jsonl").read_text().splitlines():
        incident = set(json.loads(line)["row_ordinals"]) & candidates
        if len(incident) > 1:
            shared.update(incident)
    eligible = [row for row in rows if row["ordinal"] in candidates - shared]
    if len(eligible) != 89:
        raise ValueError("expected89 exact-core singleton candidates")
    ranking = sorted([{"ordinal": row["ordinal"], "row_sha256": row["row_sha256"],
                       "rank_sha256": hashlib.sha256((NAMESPACE + "|" + row["row_sha256"]).encode()).hexdigest(),
                       "shard": row["shard"], "source_row": row["source_row"]} for row in eligible],
                     key=lambda row: (row["rank_sha256"], row["row_sha256"]))
    for index, row in enumerate(ranking):
        row["rank"] = index + 1
        row["assignment"] = "train" if index < 32 else "heldout" if index < 48 else "unused"
    write_json(ROOT / "RANKING.json", {"namespace": NAMESPACE, "candidate_count": 101,
        "singleton_eligible_count": 89, "ranking": ranking,
        "committed_before_selected_gold_demo_or_question_audit": True})
    selected = {row["ordinal"]: row for row in ranking[:48]}
    raw_selected, demos, checks = {}, {}, []
    ordinal = 0
    for path in sorted((CACHE / "2needle").glob("*.parquet")):
        if sha(path) != manifest["source_files"][str(path)]["sha256"]:
            raise ValueError("source Parquet changed")
        for batch in pq.ParquetFile(path).iter_batches(batch_size=4):
            for raw in batch.to_pylist():
                if digest(raw) != rows[ordinal]["row_sha256"]:
                    raise ValueError("actual source row differs from ranked hash")
                messages = json.loads(raw["prompt"])
                demos[digest(messages[0])] = messages[0]["content"]
                checks.append({"ordinal": ordinal, "row_sha256": rows[ordinal]["row_sha256"],
                               **question_check(raw, messages)})
                if ordinal in selected:
                    raw_selected[ordinal] = raw
                ordinal += 1
    unknown = [row for row in checks if not row["template_covered"]]
    mismatch = [row for row in checks if row["template_covered"] and not row["exact_question_match"]]
    missing_marker = [row for row in checks if not row["marker_in_visible_question"]]
    demo_errors = []
    for ordinal, raw in raw_selected.items():
        answer = raw["answer"].removeprefix(raw["random_string_to_prepend"])
        for demo_hash, demo in demos.items():
            exact = answer in demo
            normalized = " ".join(answer.split()) in " ".join(demo.split())
            if exact or normalized:
                demo_errors.append({"ordinal": ordinal, "demo_sha256": demo_hash,
                                    "exact_containment": exact, "normalized_containment": normalized})
    audit = {"all800_question_template_checked": True, "covered": 800 - len(unknown),
             "exact_question_matches": sum(row["exact_question_match"] for row in checks),
             "unknowns": unknown, "mismatches": mismatch, "missing_markers": missing_marker,
             "checks": checks, "selected_target_demo_containment": demo_errors,
             "demo_variants_checked": len(demos), "selected_targets_checked": len(raw_selected),
             "scope": "literal target request/ordinal/marker template and exact or whitespace-normalized answer containment, not semantic proof"}
    write_json(ROOT / "DATA_LINK_AUDIT.json", audit)
    if unknown or mismatch or missing_marker or demo_errors:
        write_json(ROOT / "ABORT.json", {"reason": "question or demo issue; no reranking or query rewrite",
            "ranking_sha256": sha(ROOT / "RANKING.json"), "audit_sha256": sha(ROOT / "DATA_LINK_AUDIT.json")})
        raise ValueError("data issue found; freeze stopped before model-input materialization")
    if len(raw_selected) != 48 or any(set(rows[i]["target_answer_other_core_rows"]) & set(selected)
                                     for i in selected):
        raise ValueError("selected target-answer exposure differs")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    public, gold = {"train": [], "heldout": []}, {"train": {}, "heldout": {}}
    for ranked in ranking[:48]:
        ordinal, split = ranked["ordinal"], ranked["assignment"]
        raw = raw_selected[ordinal]
        messages = json.loads(raw["prompt"])
        identifier = "omrcr-" + ranked["row_sha256"][:20]
        folder = ROOT / "inputs" / split / identifier
        prompt, question = raw["prompt"].encode(), messages[-1]["content"].encode()
        write_bytes(folder / "prompt.json", prompt)
        write_bytes(folder / "question.txt", question)
        if (folder / "prompt.json").read_bytes() != prompt or (folder / "question.txt").read_bytes() != question:
            raise ValueError("source JSON or final-question byte preservation failed")
        public[split].append({"id": identifier, "prompt_json_path": str(folder / "prompt.json"),
            "prompt_json_sha256": sha(folder / "prompt.json"), "prompt_json_bytes": len(prompt),
            "final_question_path": str(folder / "question.txt"), "final_question_sha256": sha(folder / "question.txt"),
            "external_context_representation": "original JSON document containing a list of message objects",
            "model_metadata_allowlist": ["external_context_type", "external_context_size"],
            "no_added_target_needle_or_parser_hint": True,
            "source_row_sha256": ranked["row_sha256"], "source_shard": ranked["shard"],
            "source_row": ranked["source_row"], "source_ordinal": ordinal,
            "fewshot_sha256": rows[ordinal]["fewshot_sha256"],
            "ordered_core_sha256": rows[ordinal]["ordered_core_sha256"],
            "source_conversation_qwen_chat_input_tokens": len(tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, enable_thinking=False)),
            "external_json_string_qwen_tokens": len(tokenizer.encode(raw["prompt"], add_special_tokens=False)),
            "final_question_qwen_tokens": len(tokenizer.encode(messages[-1]["content"], add_special_tokens=False)),
            "external_file_length_is_not_neural_root_prompt_length": True})
        gold[split][identifier] = {"answer": raw["answer"],
            "random_string_to_prepend": raw["random_string_to_prepend"],
            "source_row_sha256": ranked["row_sha256"], "desired_msg_index": raw["desired_msg_index"],
            "n_needles": raw["n_needles"]}
    host = ROOT / "host"
    host.mkdir(mode=0o700)
    write_json(host / "HOST_GOLD.json", gold, 0o600)
    if stat.S_IMODE(host.stat().st_mode) != 0o700 or stat.S_IMODE((host / "HOST_GOLD.json").stat().st_mode) != 0o600:
        raise ValueError("host gold permissions differ")
    write_json(ROOT / "MODEL_INPUTS.json", public)
    card = (CACHE / "README.md").read_text()
    block = re.search(r"```python\n(.*?)```", card, re.S).group(1)
    node = next(node for node in ast.parse(block).body if isinstance(node, ast.FunctionDef) and node.name == "grade")
    scorer = "from difflib import SequenceMatcher\n\n" + ast.get_source_segment(block, node) + "\n"
    write_bytes(ROOT / "official_score.py", scorer.encode())
    spec = importlib.util.spec_from_file_location("frozen_openai_mrcr_grade", ROOT / "official_score.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.grade("markeranswer", "markeranswer", "marker") == 1
    assert module.grade("prefixmarkeranswer", "markeranswer", "marker") == 0
    assert module.grade("marker answer", "markeranswer", "marker") < 1
    paths = [ROOT / "RANKING.json", ROOT / "DATA_LINK_AUDIT.json", ROOT / "MODEL_INPUTS.json",
             ROOT / "official_score.py", host / "HOST_GOLD.json", ROOT / "PLAN.md", Path(__file__)]
    paths.extend(Path(row[key]) for split in public.values() for row in split
                 for key in ("prompt_json_path", "final_question_path"))
    sources = {str(INVENTORY / "MANIFEST.json"): sha(INVENTORY / "MANIFEST.json"),
               str(CACHE / "README.md"): sha(CACHE / "README.md")}
    sources.update({path: value["sha256"] for path, value in manifest["source_files"].items()})
    sources.update({str(MODEL / name): sha(MODEL / name) for name in ("tokenizer.json", "tokenizer_config.json", "config.json")})
    result = {"schema": "openai-mrcr-short-root-frozen-data-v1", "namespace": NAMESPACE,
        "source_revision": "f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d", "license": "MIT declared in pinned card",
        "records": {key: len(value) for key, value in public.items()}, "source_date_cohort": "04-12-2025",
        "source_row_selection": "first32 train, next16 heldout from fixed hash-ranked89 core singletons",
        "root_model_has_not_queried_inputs": True, "GPU_queries": 0, "optimizer_steps": 0,
        "full800_context_overlap_not_excluded": True, "common_fewshot_retained": True,
        "selected_fewshot_variants": len({r["fewshot_sha256"] for v in public.values() for r in v}),
        "train_held_fewshot_hashes_shared": len({r["fewshot_sha256"] for r in public["train"]}
                                               & {r["fewshot_sha256"] for r in public["heldout"]}),
        "selected_core_pair_and_target_cross_exposure": 0,
        "selected_target_absent_from_all9_demo_variants_exact_and_wsnormalized": True,
        "visible_final_question_exact_template_matches": 800,
        "host_gold_mode": "0600", "host_directory_mode": "0700",
        "qwen_tokenizer_path": str(MODEL), "python": platform.python_version(),
        "counts": {split: {"source_chat_tokens_min": min(row["source_conversation_qwen_chat_input_tokens"] for row in values),
                           "source_chat_tokens_max": max(row["source_conversation_qwen_chat_input_tokens"] for row in values),
                           "external_json_tokens_min": min(row["external_json_string_qwen_tokens"] for row in values),
                           "external_json_tokens_max": max(row["external_json_string_qwen_tokens"] for row in values),
                           "question_tokens_min": min(row["final_question_qwen_tokens"] for row in values),
                           "question_tokens_max": max(row["final_question_qwen_tokens"] for row in values)} for split, values in public.items()},
        "future_neural_prompt_or_trajectory_budget": "not defined or admitted by this data artifact",
        "files_sha256": {str(path): sha(path) for path in paths}, "source_sha256": sources,
        "elapsed_seconds": time.monotonic() - started,
        "claim_boundary": "new local optimization inputs and exact core-disjoint short split; shared demos and unknown pretraining remain"}
    write_json(ROOT / "MANIFEST.json", result)
    ready = {"schema": "openai-mrcr-short-root-data-ready-v1", "status": "DATA_ONLY_NO_GPU_OR_TRAINING_ADMISSION",
             "manifest_sha256": sha(ROOT / "MANIFEST.json"), "records": result["records"],
             "closure_sha256": {**result["files_sha256"], **sources, str(ROOT / "MANIFEST.json"): sha(ROOT / "MANIFEST.json")}}
    ready["identity"] = digest(ready)
    write_json(ROOT / "DATA_READY.json", ready)
    print({"DATA_READY_sha256": sha(ROOT / "DATA_READY.json"), "identity": ready["identity"],
           "records": ready["records"], "counts": result["counts"], "seconds": result["elapsed_seconds"]})


if __name__ == "__main__":
    main()
