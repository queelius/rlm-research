"""Hash-only candidate/cohort incidence; no train/test assignment."""

import json
from collections import Counter

from inventory import ROOT, components, sha, write_json

rows = [json.loads(line) for line in (ROOT / "ROWS.jsonl").read_text().splitlines()]
pairs = [json.loads(line) for line in (ROOT / "CORE_PAIR_INCIDENCE.jsonl").read_text().splitlines()]
answers = [json.loads(line) for line in (ROOT / "TARGET_ANSWER_INCIDENCE.jsonl").read_text().splitlines()]
inventory = json.loads((ROOT / "INVENTORY.json").read_text())
subsets = {}
for name, selected in {
    "chars_le200k": [r for r in rows if r["n_chars"] <= 200000],
    **{f"short_o200k_total_le{cap}": [r for r in rows if r["o200k_base_tokens_if_short"]
       and r["o200k_base_tokens_if_short"]["prompt_content_plus_answer"] <= cap]
       for cap in (8192, 16384, 32768)},
}.items():
    ids = {r["ordinal"] for r in selected}
    index = {key: i for i, key in enumerate(sorted(ids))}
    shared_pairs = [{index[key] for key in pair["row_ordinals"] if key in ids} for pair in pairs]
    shared_answers = [{index[key] for key in answer["core_row_ordinals"] if key in ids}
                      for answer in answers]
    core_components = components(shared_pairs, len(ids))
    target_components = components(shared_answers, len(ids))
    subsets[name] = {"rows": len(ids), "date_added_counts": dict(Counter(r["date_added"] for r in selected)),
        "row_ordinals": sorted(ids),
        "rows_target_answer_in_another_selected_core": sum(bool(set(r["target_answer_other_core_rows"]) & ids) for r in selected),
        "rows_target_pair_in_another_selected_core": sum(bool(set(r["target_pair_other_core_rows"]) & ids) for r in selected),
        "core_pair_component_sizes": core_components["sizes"],
        "target_answer_component_sizes": target_components["sizes"],
        "no_split_designated": True}
cohorts = {}
for number, group in enumerate(inventory["core_pair_overlap_components"]["row_ordinals"]):
    selected = [rows[index] for index in group]
    cohorts[str(number)] = {"rows": len(selected), "date_added_counts": dict(Counter(r["date_added"] for r in selected)),
        "fewshot_hashes": sorted({r["fewshot_sha256"] for r in selected}),
        "target_user_hashes_count": len({r["target_user_sha256"] for r in selected}),
        "target_answers": len({r["target_answer_sha256"] for r in selected}),
        "short_chars_le200k": sum(r["n_chars"] <= 200000 for r in selected)}
left, right = inventory["core_pair_overlap_components"]["row_ordinals"]
cross = {field: len({rows[i][field] for i in left} & {rows[i][field] for i in right})
         for field in ("fewshot_sha256", "target_user_sha256", "target_answer_sha256", "target_pair_sha256")}
report = {"schema": "openai-mrcr-hash-only-subset-inventory-v1", "source_manifest_sha256": sha(ROOT / "MANIFEST.json"),
          "candidate_subsets": subsets, "full_core_components_date_mapping": cohorts,
          "cross_component_shared_hash_counts": cross,
          "caveat": "component separation is exact-byte separation, not semantic independence; date cohorts differ; no split made"}
write_json(ROOT / "SUBSET_INVENTORY.json", report)
write_json(ROOT / "SUBSET_MANIFEST.json", {"source_manifest_sha256": sha(ROOT / "MANIFEST.json"),
    "source_sha256": sha(__file__), "subset_inventory_sha256": sha(ROOT / "SUBSET_INVENTORY.json"),
    "raw_source_reparsed": False, "model_queries": 0})
print(json.dumps({"cohort_rows_dates": {k: (v["rows"], v["date_added_counts"]) for k,v in cohorts.items()},
                  "cross_component": cross, "subsets": {k: {field: v[field] for field in
                    ("rows", "date_added_counts", "rows_target_answer_in_another_selected_core", "core_pair_component_sizes", "target_answer_component_sizes")}
                    for k,v in subsets.items()}}, sort_keys=True))
