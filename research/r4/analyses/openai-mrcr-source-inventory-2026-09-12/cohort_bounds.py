"""Length-only feasibility bounds, never a designated train/heldout split."""

import json

import pyarrow.parquet as pq
import tiktoken

from inventory import CACHE, ROOT, sha, write_json

rows = [json.loads(line) for line in (ROOT / "ROWS.jsonl").read_text().splitlines()]
cohorts = {date: sorted([row for row in rows if row["date_added"] == date], key=lambda row: (row["n_chars"], row["ordinal"]))
           for date in sorted({row["date_added"] for row in rows})}
repaired = cohorts["12-05-2025"][:16]
required = {row["ordinal"] for row in repaired if row["o200k_base_tokens_if_short"] is None}
extra = {}
enc = tiktoken.get_encoding("o200k_base")
ordinal = 0
for path in sorted((CACHE / "2needle").glob("*.parquet")):
    for batch in pq.ParquetFile(path).iter_batches(batch_size=4, columns=["prompt", "answer"]):
        for raw in batch.to_pylist():
            if ordinal in required:
                messages = json.loads(raw["prompt"])
                prompt_tokens = sum(len(enc.encode(m["content"], disallowed_special=())) for m in messages)
                answer_tokens = len(enc.encode(raw["answer"], disallowed_special=()))
                extra[ordinal] = {"prompt_content": prompt_tokens, "answer": answer_tokens,
                                  "prompt_content_plus_answer": prompt_tokens + answer_tokens}
            ordinal += 1
assert set(extra) == required
report = {"schema": "openai-mrcr-cohort-length-feasibility-v1", "no_split_designated": True,
          "cohorts": {date: {"rows": len(group), "chars_at16th_smallest": group[15]["n_chars"],
              "chars_at32nd_smallest": group[31]["n_chars"],
              "known_short_token_counts": {str(cap): sum(row["o200k_base_tokens_if_short"] is not None and
                row["o200k_base_tokens_if_short"]["prompt_content_plus_answer"] <= cap for row in group)
                for cap in (8192, 16384, 32768)},
              "scope_of_counts": "all source rows with<=200000 content characters tokenized"}
            for date, group in cohorts.items()},
          "corrected_16_shortest_character_orderstat_inventory": [{"ordinal": row["ordinal"],
              "shard": row["shard"], "source_row": row["source_row"], "row_sha256": row["row_sha256"],
              "n_chars": row["n_chars"], "o200k_base": row["o200k_base_tokens_if_short"] or extra[row["ordinal"]]}
              for row in repaired],
          "exact_32train_16held_short_design_feasibility": {
              "source": "101 original-cohort candidates at<=8192 o200k prompt-content+answer tokens",
              "89_singleton_exact_core_components": True,
              "all101_target_answers_absent_from_other_candidate_cores": True,
              "proposal": "future deterministic component-aware32/16 from short pool; shared fewshot remains",
              "not_semantic_independence_or_actual_Qwen_context_admission": True}}
write_json(ROOT / "COHORT_LENGTH_BOUNDS.json", report)
write_json(ROOT / "COHORT_LENGTH_MANIFEST.json", {"source_sha256": sha(__file__),
    "source_inventory_manifest_sha256": sha(ROOT / "MANIFEST.json"),
    "cohort_bounds_sha256": sha(ROOT / "COHORT_LENGTH_BOUNDS.json"), "extra_rows_tokenized": len(extra),
    "GPU_queries": 0, "raw_answers_published": False, "no_split_designated": True})
print({"extra_rows_tokenized": len(extra), "corrected16_max_o200k_total": max(
    row["o200k_base"]["prompt_content_plus_answer"] for row in report["corrected_16_shortest_character_orderstat_inventory"])})
