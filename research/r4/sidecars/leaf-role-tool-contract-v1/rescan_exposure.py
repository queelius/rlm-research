"""Timestamped repeat of the named-input exposure scan; frozen DATA is read-only."""

import datetime as dt
import hashlib
import json
import os
import re
import time
from pathlib import Path

import pyarrow.parquet as pq

import select_data as selection
import study as s


def main():
    output = s.ROOT / "EXPOSURE_RESCAN.json"
    if output.exists():
        raise FileExistsError("rescan already recorded")
    started_ns = time.time_ns()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    sources = {"agnews": selection.AG / "test.parquet", "sst2": selection.SST / "train.parquet"}
    columns = {"agnews": "text", "sst2": "sentence"}
    universe = set()
    for dataset, path in sources.items():
        universe.update(s.group(row[columns[dataset]]) for row in pq.read_table(path).to_pylist())
    selected = {record["group_id"] for context in s.read(s.ROOT / "DATA.json")["contexts"]
                for record in context["records"]}
    matched = set()
    catalogs = []
    skipped = []
    prune = {"outputs", "output", "qualification", "qualifications", "tests", "test",
             "analyses", "research-cache", "checkpoints", ".git", ".venv", "venv",
             "__pycache__", "service", "source", "src", "node_modules", "probe-outputs",
             "exports", "training"}
    pattern = re.compile(r"(?:DATA|PUBLIC(?:_CATALOGS)?|GROUPS|SPEC(?:[-_.][\w.-]+)?|CONTEXTS|RESERVATIONS)\.json")
    for base, directories, files in os.walk(selection.RUNS):
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
            selection._visit(value, universe, found)
            if found:
                matched.update(found)
                catalogs.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                                 "matching_groups": len(found)})
    overlap = sorted(selected & matched)
    if overlap:
        raise ValueError("frozen selected groups now occur in an external named input: " + overlap[0])
    ended_ns = time.time_ns()
    ended_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    s.write_once(output, {"schema": "leaf-role-tool-exposure-rescan-v1",
        "actual_scan_started_utc": started_utc, "actual_scan_ended_utc": ended_utc,
        "actual_scan_started_epoch_ns": started_ns, "actual_scan_ended_epoch_ns": ended_ns,
        "elapsed_seconds": (ended_ns - started_ns) / 1e9,
        "scope": "All /project/alex_phd/runs roots; named DATA/PUBLIC/GROUPS/SPEC/CONTEXTS/RESERVATIONS JSON under 32MB; own sidecar, outputs, analyses, training and provenance-only branches excluded.",
        "catalogs": catalogs, "oversize_candidates_skipped": skipped,
        "matched_external_groups": len(matched), "frozen_selected_groups": len(selected),
        "selected_external_overlap": overlap,
        "correction": "DATA's 20:00 UTC field is an evidence cutoff, not the original scan execution timestamp. Original filesystem bounds are select_data.py finalized 20:08:52.370 UTC and DATA created 20:09:15.407 UTC. This timestamped repeat supplies an actual scan interval without changing DATA or membership.",
        "limit": "Named-catalog crosswalk only; no whole-history, semantic-near-duplicate, or model-pretraining guarantee."})
    print(s.serialize({"started": started_utc, "ended": ended_utc,
                       "catalogs": len(catalogs), "selected_overlap": 0}))


if __name__ == "__main__":
    main()
