"""Select four source-fresh contexts against a named-input catalog scan; no outcomes."""

import json
import os
import re
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

import study as s

RUNS = Path("/project/alex_phd/runs")
CACHE = Path("/project/alex_phd/research-cache/datasets")
AG = CACHE / "fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4"
SST = CACHE / "sst2-train-feasibility-20260909"
CUTOFF = "2026-09-09T20:00:00Z"


def _visit(value, universe, found):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"dedup", "acquisition", "source_sha256", "source_provenance", "freshness"} \
                    or "provenance" in key:
                continue
            if key in {"question", "text", "sentence"} and isinstance(item, str):
                identity = s.group(item)
                if identity in universe:
                    found.add(identity)
            _visit(item, universe, found)
    elif isinstance(value, list):
        for item in value:
            _visit(item, universe, found)
    elif isinstance(value, str) and value in universe:
        found.add(value)


def main():
    if (s.ROOT / "DATA.json").exists():
        raise FileExistsError("DATA already frozen")
    paths = {"agnews": AG / "test.parquet", "sst2": SST / "train.parquet"}
    expected = {"agnews": "71de87ec66bc5737752a2502204dfa6d7fe9856ade3ea444dc6317789a4f13fb",
                "sst2": "c7921283b75a42e685f50edecb96798607ea0fcbfd0739ee8975f22c12d55f09"}
    columns = {"agnews": "text", "sst2": "sentence"}
    labels = {"agnews": ["World", "Sports", "Business", "Sci/Tech"],
              "sst2": ["negative", "positive"]}
    pools = {}
    universe = set()
    source_sha256 = {}
    for dataset, path in paths.items():
        if s.sha(path) != expected[dataset]:
            raise ValueError("raw source changed")
        source_sha256[str(path)] = expected[dataset]
        pools[dataset] = [{"index": index, "text": row[columns[dataset]], "label": row["label"]}
                          for index, row in enumerate(pq.read_table(path).to_pylist())]
        universe.update(s.group(row["text"]) for row in pools[dataset])

    excluded = set()
    catalogs = []
    skipped = []
    prune = {"outputs", "output", "qualification", "qualifications", "tests", "test",
             "analyses", "research-cache", "checkpoints", ".git", ".venv", "venv",
             "__pycache__", "service", "source", "src", "node_modules", "probe-outputs",
             "exports", "training"}
    pattern = re.compile(r"(?:DATA|PUBLIC(?:_CATALOGS)?|GROUPS|SPEC(?:[-_.][\w.-]+)?|CONTEXTS|RESERVATIONS)\.json")
    for base, directories, files in os.walk(RUNS):
        directories[:] = [name for name in directories if name not in prune and
                           not name.startswith(("attempt", "service-", "qualification-"))]
        if Path(base).resolve() == s.ROOT.resolve():
            directories[:] = []
            continue
        for name in files:
            if not pattern.fullmatch(name):
                continue
            path = Path(base) / name
            if path.stat().st_size > 32_000_000:
                skipped.append(str(path))
                continue
            raw = path.read_bytes()
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                continue
            found = set()
            _visit(value, universe, found)
            if found:
                file_sha = __import__("hashlib").sha256(raw).hexdigest()
                source_sha256[str(path)] = file_sha
                catalogs.append({"path": str(path), "sha256": file_sha,
                                 "matching_groups": len(found)})
                excluded.update(found)

    contexts = []
    selections = {}
    for dataset in ("agnews", "sst2"):
        selected, audit = s.choose(pools[dataset], excluded, dataset, 128)
        selections[dataset] = audit
        for context_number in range(2):
            rows = selected[context_number * 64:(context_number + 1) * 64]
            numbers = sorted(range(1000, 10000),
                             key=lambda number: s.digest([s.MASTER_SEED, dataset,
                                                          context_number, "source-id", number]))[:64]
            records = []
            for position, (row, number) in enumerate(zip(rows, numbers, strict=True), 1):
                records.append({"source_row_index": row["index"],
                                "source_row_indexes": row["source_row_indexes"],
                                "source_file": str(paths[dataset]),
                                "source_split": "test" if dataset == "agnews" else "train",
                                "question": row["text"], "source_label": row["label"],
                                "group_id": row["group_id"],
                                "gold_label": labels[dataset][row["label"]],
                                "id": f"q{number:04d}", "source_position": position,
                                "input_position": position, "selection_hash": row["selection_hash"]})
            contexts.append({"index": len(contexts), "dataset": dataset,
                             "source_context_index": context_number,
                             "source_context_id": f"role-tool-{dataset}-{context_number:02d}",
                             "labels": labels[dataset], "records": records})
        audit["selected_label_counts"] = dict(Counter(row["label"] for row in selected))
        audit["selected_word_counts_capped10"] = dict(Counter(
            min(10, len(row["text"].split())) for row in selected))

    provenance = {"scan_cutoff_utc": CUTOFF,
                  "scan_scope": "All /project/alex_phd/runs roots; named DATA/PUBLIC/GROUPS/SPEC/CONTEXTS/RESERVATIONS JSON inputs under 32MB; outputs, analyses, training and provenance-only branches excluded.",
                  "scope_limit": "Positive named-catalog/input/reservation crosswalk, not an exhaustive whole-history, near-duplicate or model-pretraining certificate.",
                  "catalogs": catalogs, "oversize_candidates_skipped": skipped,
                  "source_sha256": source_sha256, "selection": selections,
                  "selection_rule": "NFKC/casefold/whitespace group SHA; conflicts excluded whole; SHA256(master,dataset,selection,group) first128; two contiguous64; earliest raw row; IDs label-independent.",
                  "underlying_dataset_license": "AG News and SST-2 unknown/unconfirmed; model license is separate."}
    data = {"schema": "leaf-role-tool-contract-data-v1", "contexts": contexts,
            "master_seed": s.MASTER_SEED, "sampling_seed": s.SAMPLE_SEED,
            "exposure": "Exact groups absent from the frozen named-catalog scan at its cutoff; SST train includes phrases/text units; near duplicates and model exposure unresolved.",
            "source_provenance": provenance}
    s.write_once(s.ROOT / "DATA.json", data)
    s.write_once(s.ROOT / "SELECTION_PROVENANCE.json", provenance)
    print(s.serialize({"contexts": 4, "selected": 256, "catalogs": len(catalogs),
                       "eligible": {key: value["eligible_groups"] for key, value in selections.items()}}))


if __name__ == "__main__":
    main()
