"""Freeze a balanced, outcome-blind four-needle ordinal-transfer cohort."""

from __future__ import annotations

from collections import Counter
import functools
import hashlib
import json
import os
from pathlib import Path
import re
import stat

import pyarrow.parquet as pq
import tiktoken
from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
CACHE = Path("/project/alex_phd/research-cache/datasets/openai-mrcr-fourneedle-f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d")
ACQUISITION = ROOT.parents[1] / "operations/2026-09-12-fourneedle-acquisition/ACQUISITION.json"
SHORT = SIDE / "openai-mrcr-short-root-data-v1"
LONG = SIDE / "openai-mrcr-long-transfer-data-v1"
FRESH = SIDE / "openai-mrcr-short-next8-data-v1"
MODEL = Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554")
NAMESPACE = "mrcr-fourneedle-ordinal-transfer-20260912"
SOURCE_SHA = {
    "4needle_0.parquet": "4d4fa3d11ce064749de3cd039eef1a621e30a81c2c9b3e64f1df37f8afeaf312",
    "4needle_1.parquet": "8dfdb94a208cf3eee73c4e7ac6ee8a5ccb7236c6934c13c6c5f67c0a9928cdf3",
}


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def read(path: Path):
    return json.loads(Path(path).read_text())


def write_json(path: Path, value, mode: int = 0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def _core(messages):
    return messages[1:-1]


def _pair_hashes(messages):
    core = _core(messages)
    return {digest([user, assistant]) for user, assistant in zip(core[::2], core[1::2], strict=True)}


def _answer_hashes(messages):
    return {text_sha(item["content"]) for item in _core(messages)[1::2]}


def _load_exposure(public_path: Path, gold_path: Path, public_key=None, gold_key=None):
    public = read(public_path)
    gold = read(gold_path)
    if public_key is not None:
        public = public[public_key]
    if gold_key is not None:
        gold = gold[gold_key]
    values = []
    for row in public:
        messages = json.loads(Path(row["prompt_json_path"]).read_text())
        truth = gold[row["id"]]
        values.append(
            {
                "row_sha256": row["source_row_sha256"],
                "pairs": _pair_hashes(messages),
                "answers": _answer_hashes(messages),
                "target": text_sha(truth["answer"].removeprefix(truth["random_string_to_prepend"])),
            }
        )
    return values


@functools.lru_cache(maxsize=1)
def exposure():
    old_public = read(SHORT / "MODEL_INPUTS_V2.json")
    old_gold = read(SHORT / "host/HOST_GOLD.json")
    old = []
    for split in ("train", "heldout"):
        for row in old_public[split]:
            messages = json.loads(Path(row["prompt_json_path"]).read_text())
            truth = old_gold[split][row["id"]]
            old.append({"row_sha256": row["source_row_sha256"], "pairs": _pair_hashes(messages), "answers": _answer_hashes(messages), "target": text_sha(truth["answer"].removeprefix(truth["random_string_to_prepend"]))})
    long = _load_exposure(LONG / "MODEL_INPUTS.json", LONG / "host/HOST_GOLD.json", "records")
    fresh = _load_exposure(FRESH / "MODEL_INPUTS.json", FRESH / "host/HOST_GOLD.json", "records")
    rows = old + long + fresh
    if len(rows) != 72:
        raise ValueError("expected exact 48+16+8 exposure rows")
    return {
        "rows": {row["row_sha256"] for row in rows},
        "pairs": set().union(*(row["pairs"] for row in rows)),
        "core_answers": set().union(*(row["answers"] for row in rows)),
        "targets": {row["target"] for row in rows},
    }


def _question_exact(raw, messages, occurrence):
    target = messages[raw["desired_msg_index"]]["content"]
    parsed = re.fullmatch(r"write an? (.+)", target)
    if parsed is None:
        return False
    ordinal = {3: "3rd", 4: "4th"}[occurrence]
    expected = f"Prepend {raw['random_string_to_prepend']} to the {ordinal} (1 indexed) {parsed.group(1)}. Do not include any other text in your response."
    return messages[-1]["content"] == expected


@functools.lru_cache(maxsize=1)
def scan():
    acquired = read(ACQUISITION)
    if acquired["revision"] != "f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d" or acquired["license"] != "MIT":
        raise ValueError("acquisition provenance changed")
    enc = tiktoken.get_encoding("o200k_base")
    rows = []
    source_ordinal = 0
    for path in sorted((CACHE / "4needle").glob("*.parquet")):
        if sha(path) != SOURCE_SHA[path.name]:
            raise ValueError("four-needle source changed")
        source_row = 0
        for batch in pq.ParquetFile(path).iter_batches(batch_size=8):
            for raw in batch.to_pylist():
                messages = json.loads(raw["prompt"])
                desired = raw["desired_msg_index"]
                target = messages[desired]["content"]
                positions = [index for index in range(1, len(messages) - 1, 2) if messages[index]["content"] == target]
                occurrence = positions.index(desired) + 1
                if raw["n_needles"] != 4 or len(positions) != 4 or messages[desired + 1]["content"] != raw["answer"].removeprefix(raw["random_string_to_prepend"]):
                    raise ValueError("official four-needle row contract changed")
                total_tokens = None
                if raw["n_chars"] <= 200000:
                    total_tokens = sum(len(enc.encode(item["content"], disallowed_special=())) for item in messages) + len(enc.encode(raw["answer"], disallowed_special=()))
                row_sha = digest(raw)
                rows.append({
                    "source_ordinal": source_ordinal,
                    "source_shard": path.name,
                    "source_row": source_row,
                    "row_sha256": row_sha,
                    "raw": raw,
                    "messages": messages,
                    "pairs": _pair_hashes(messages),
                    "core_answers": _answer_hashes(messages),
                    "target_answer_sha256": text_sha(raw["answer"].removeprefix(raw["random_string_to_prepend"])),
                    "ordered_core_sha256": digest(_core(messages)),
                    "target_occurrence_one_indexed": occurrence,
                    "n_needles": raw["n_needles"],
                    "o200k_prompt_plus_answer": total_tokens,
                    "official_question_exact": occurrence in (3, 4) and _question_exact(raw, messages, occurrence),
                })
                source_ordinal += 1
                source_row += 1
    if len(rows) != 800:
        raise ValueError("expected exact800 four-needle rows")
    return rows


def _reasons(row, exposed):
    reasons = []
    if row["o200k_prompt_plus_answer"] is None or row["o200k_prompt_plus_answer"] > 8192:
        reasons.append("outside_original_short_band")
    if row["target_occurrence_one_indexed"] not in (3, 4):
        reasons.append("not_third_or_fourth_request")
    if not row["official_question_exact"]:
        reasons.append("official_question_template_mismatch")
    if row["row_sha256"] in exposed["rows"]:
        reasons.append("direct_exposed_row")
    if row["pairs"] & exposed["pairs"]:
        reasons.append("exact_core_pair_with_exposed")
    if row["target_answer_sha256"] in exposed["core_answers"]:
        reasons.append("candidate_target_in_exposed_core")
    if row["core_answers"] & exposed["targets"]:
        reasons.append("exposed_target_in_candidate_core")
    return reasons


@functools.lru_cache(maxsize=1)
def select():
    exposed = exposure()
    candidates = []
    for row in scan():
        if row["target_occurrence_one_indexed"] not in (3, 4):
            continue
        reasons = _reasons(row, exposed)
        candidates.append({"row": row, "reasons": reasons, "rank_sha256": text_sha(NAMESPACE + "|" + str(row["target_occurrence_one_indexed"]) + "|" + row["row_sha256"])})
    selected = []
    eligible_counts = {}
    for occurrence in (3, 4):
        eligible = sorted((item for item in candidates if item["row"]["target_occurrence_one_indexed"] == occurrence and not item["reasons"]), key=lambda item: (item["rank_sha256"], item["row"]["row_sha256"]))
        eligible_counts[str(occurrence)] = len(eligible)
        for item in eligible:
            row = item["row"]
            conflict = any(row["pairs"] & prior["pairs"] or row["target_answer_sha256"] in prior["core_answers"] or prior["target_answer_sha256"] in row["core_answers"] for prior in selected)
            if not conflict:
                selected.append(row)
            if sum(prior["target_occurrence_one_indexed"] == occurrence for prior in selected) == 8:
                break
    conflicts = []
    for index, left in enumerate(selected):
        for right in selected[index + 1:]:
            if left["pairs"] & right["pairs"]:
                conflicts.append({"left": left["row_sha256"], "right": right["row_sha256"], "kind": "exact_core_pair"})
            if left["target_answer_sha256"] in right["core_answers"] or right["target_answer_sha256"] in left["core_answers"]:
                conflicts.append({"left": left["row_sha256"], "right": right["row_sha256"], "kind": "target_core"})
    public_selected = [{key: row[key] for key in ("source_ordinal", "source_shard", "source_row", "row_sha256", "ordered_core_sha256", "target_answer_sha256", "target_occurrence_one_indexed", "n_needles", "o200k_prompt_plus_answer", "official_question_exact")} for row in selected]
    return {
        "schema": "openai-mrcr-fourneedle-ordinal-transfer-selection-v1",
        "namespace": NAMESPACE,
        "source_rows": len(scan()),
        "exposed_rows": 72,
        "considered_third_fourth": len(candidates),
        "short_counts": {str(occurrence): sum(item["row"]["target_occurrence_one_indexed"] == occurrence and item["row"]["o200k_prompt_plus_answer"] is not None and item["row"]["o200k_prompt_plus_answer"] <= 8192 for item in candidates) for occurrence in (3, 4)},
        "eligible_counts": eligible_counts,
        "exclusion_reason_counts": dict(Counter(reason for item in candidates for reason in item["reasons"])),
        "skip_ledger": [{"source_ordinal": item["row"]["source_ordinal"], "row_sha256": item["row"]["row_sha256"], "target_occurrence_one_indexed": item["row"]["target_occurrence_one_indexed"], "rank_sha256": item["rank_sha256"], "reasons": item["reasons"]} for item in candidates],
        "selected": public_selected,
        "selected_conflicts": conflicts,
        "selection_uses_model_answers": False,
        "selection_uses_previous_outcomes": False,
    }


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (ROOT / "DATA_READY.json").exists():
        raise ValueError("unused CPU-only data freeze required")
    selection = select()
    if len(selection["selected"]) != 16 or selection["selected_conflicts"]:
        write_json(ROOT / "FEASIBILITY.json", selection)
        raise ValueError("frozen balanced cohort infeasible")
    selected_rows = {row["row_sha256"]: row for row in scan() if row["row_sha256"] in {item["row_sha256"] for item in selection["selected"]}}
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL), local_files_only=True)
    public, gold = [], {}
    for selected in selection["selected"]:
        row = selected_rows[selected["row_sha256"]]
        raw, messages = row["raw"], row["messages"]
        identifier = "omrcr-four-" + row["row_sha256"][:20]
        folder = ROOT / "inputs/records" / identifier
        prompt, question = raw["prompt"].encode(), messages[-1]["content"].encode()
        folder.mkdir(parents=True, exist_ok=True)
        for path, value in ((folder / "prompt.json", prompt), (folder / "question.txt", question)):
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(value)
        encoded = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, enable_thinking=False, return_dict=True)
        public.append({
            "id": identifier,
            **selected,
            "prompt_json_path": str(folder / "prompt.json"),
            "prompt_json_sha256": sha(folder / "prompt.json"),
            "prompt_json_bytes": len(prompt),
            "final_question_path": str(folder / "question.txt"),
            "final_question_sha256": sha(folder / "question.txt"),
            "source_conversation_qwen_chat_input_tokens": len(encoded["input_ids"]),
            "external_json_string_qwen_tokens": len(tokenizer.encode(raw["prompt"], add_special_tokens=False)),
            "external_file_length_is_not_neural_root_prompt_length": True,
            "no_added_answer_position_or_parser_hint": True,
        })
        gold[identifier] = {"answer": raw["answer"], "random_string_to_prepend": raw["random_string_to_prepend"], "desired_msg_index": raw["desired_msg_index"], "target_occurrence_one_indexed": row["target_occurrence_one_indexed"], "source_row_sha256": row["row_sha256"]}
    write_json(ROOT / "SELECTION.json", selection)
    write_json(ROOT / "MODEL_INPUTS.json", {"records": public})
    host = ROOT / "host"
    host.mkdir(mode=0o700)
    write_json(host / "HOST_GOLD.json", gold, 0o600)
    if stat.S_IMODE(host.stat().st_mode) != 0o700 or stat.S_IMODE((host / "HOST_GOLD.json").stat().st_mode) != 0o600:
        raise ValueError("host truth permissions differ")
    scorer = SHORT / "official_score.py"
    (ROOT / "official_score.py").write_bytes(scorer.read_bytes())
    generated = [ROOT / name for name in ("DESIGN.md", "prepare.py", "test_prepare.py", "SELECTION.json", "MODEL_INPUTS.json", "official_score.py")]
    generated += [Path(row[key]) for row in public for key in ("prompt_json_path", "final_question_path")]
    source = {str(ACQUISITION): sha(ACQUISITION), str(CACHE / "README.md"): sha(CACHE / "README.md"), **{str(CACHE / "4needle" / name): value for name, value in SOURCE_SHA.items()}, str(SHORT / "DATA_READY_V2.json"): sha(SHORT / "DATA_READY_V2.json"), str(LONG / "DATA_READY.json"): sha(LONG / "DATA_READY.json"), str(FRESH / "DATA_READY.json"): sha(FRESH / "DATA_READY.json")}
    manifest = {
        "schema": "openai-mrcr-fourneedle-ordinal-transfer-data-manifest-v1",
        "status": "DATA_ONLY_NO_MODEL_QUERY_OR_TRAINING",
        "dataset": "openai/mrcr 4needle",
        "revision": "f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d",
        "license": "MIT from pinned official dataset card/acquisition receipt",
        "records": 16,
        "third_occurrence": 8,
        "fourth_occurrence": 8,
        "short_band_o200k_prompt_plus_answer_max": 8192,
        "excluded_prior_rows": 72,
        "pairwise_and_exposure_conflicts": 0,
        "selection_uses_model_answers": False,
        "selection_uses_previous_outcomes": False,
        "unknown_base_pretraining_exposure": True,
        "common_fewshot_retained": True,
        "public_contains_gold": False,
        "host_gold_mode": "0600",
        "model_queries": 0,
        "optimizer_steps": 0,
        "files_sha256": {str(path): sha(path) for path in generated},
        "host_gold_sha256": sha(host / "HOST_GOLD.json"),
        "source_sha256": source,
        "claim_boundary": "third/fourth request ordinal transfer within the same official task and short length band; not a new benchmark",
    }
    write_json(ROOT / "MANIFEST.json", manifest)
    ready = {"schema": "openai-mrcr-fourneedle-ordinal-transfer-data-ready-v1", "status": "DATA_ONLY_NO_GPU_OR_EVALUATOR", "records": 16, "manifest_sha256": sha(ROOT / "MANIFEST.json"), "selection_sha256": sha(ROOT / "SELECTION.json"), "model_inputs_sha256": sha(ROOT / "MODEL_INPUTS.json"), "closure_sha256": {**manifest["files_sha256"], **source, str(host / "HOST_GOLD.json"): sha(host / "HOST_GOLD.json"), str(ROOT / "MANIFEST.json"): sha(ROOT / "MANIFEST.json")}}
    ready["identity"] = digest(ready)
    write_json(ROOT / "DATA_READY.json", ready)
    print(json.dumps({"identity": ready["identity"], "sha256": sha(ROOT / "DATA_READY.json"), "short_counts": selection["short_counts"], "eligible_counts": selection["eligible_counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
