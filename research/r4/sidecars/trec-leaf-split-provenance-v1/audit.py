"""Read-only CPU provenance analysis, not a training/evaluation dataset generator."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDECARS = ROOT.parent
OLD = Path("/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv")
NEW = Path("/project/alex_phd/research-cache/2026-09-08-literature/trec-leaf-splits.4HU2Tz")
NAMESPACE = "trec-leaf-split-provenance-v1|20260908"
LABELS = {
    "abbreviation": "ABBR", "entity": "ENTY", "description and abstract concept": "DESC",
    "human being": "HUM", "location": "LOC", "numeric value": "NUM",
}


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalize(question: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", question).casefold()))


def trec(path: Path) -> list[dict]:
    rows = []
    for index, raw in enumerate(path.read_bytes().splitlines()):
        # Exact operation from the pinned, inspected official HF loader, not fuzzy matching.
        fine, _, question = raw.replace(b"\xf0", b" ").strip().decode("utf-8").partition(" ")
        coarse = fine.split(":")[0]
        assert coarse in LABELS.values() and question
        rows.append({"line_1based": index + 1, "question": question, "coarse": coarse})
    return rows


def group(rows: list[dict]) -> dict[str, list[dict]]:
    result = defaultdict(list)
    for row in rows:
        result[normalize(row["question"])].append(row)
    return dict(result)


def statistics(rows: list[dict]) -> dict:
    groups = group(rows)
    return {
        "rows": len(rows), "exact_unique_questions": len({r["question"] for r in rows}),
        "normalized_unique_questions": len(groups),
        "normalized_duplicate_groups": sum(len(v) > 1 for v in groups.values()),
        "normalized_excess_duplicate_rows": len(rows) - len(groups),
        "normalized_coarse_conflict_groups": [sha(k.encode()) for k, v in groups.items()
                                              if len({r["coarse"] for r in v}) > 1],
        "row_label_counts": dict(sorted(Counter(r["coarse"] for r in rows).items())),
        "unique_group_label_counts": dict(sorted(Counter(v[0]["coarse"] for v in groups.values()).items())),
    }


def overlap(first: list[dict], second: list[dict]) -> dict:
    a, b = group(first), group(second)
    shared = sorted(a.keys() & b.keys())
    return {"exact": len({r["question"] for r in first} & {r["question"] for r in second}),
            "normalized": len(shared),
            "normalized_group_sha256": [sha(key.encode()) for key in shared],
            "coarse_disagreements": [
                {"question_group_sha256": sha(key.encode()), "first": a[key][0]["coarse"],
                 "second": b[key][0]["coarse"]}
                for key in shared if a[key][0]["coarse"] != b[key][0]["coarse"]]}


def authenticated_paths() -> list[Path]:
    paths = [OLD / "PROVENANCE.json", NEW / "PROVENANCE.json", Path(__file__)]
    for manifest in paths[:2]:
        for row in json.loads(manifest.read_text())["files"]:
            path = Path(row["path"])
            assert path.stat().st_size == row["bytes"] and sha(path.read_bytes()) == row["sha256"]
            paths.append(path)
    return paths


def run() -> tuple[dict, dict]:
    # Self-check normalization equivalence and non-equivalence before counting actual inputs.
    assert normalize("What does NASA stand for ?") == normalize(" WHAT does NASA stand for?")
    assert normalize("What's viscosity?") == normalize("What ' s viscosity ?")
    assert normalize("How many hearts?") != normalize("How many lungs?")
    paths = authenticated_paths()
    train = trec(OLD / "train_5500.label")
    test = trec(NEW / "TREC_10.label")
    validated = [
        {"line_1based": i + 1, "question": row["input"], "coarse": LABELS[row["label"]]}
        for i, row in enumerate(json.loads(line) for line in
                                (OLD / "oolong__trec_coarse_validated.jsonl").read_text().splitlines())
    ]
    sources = {"trec_train": train, "trec_test": test, "oolong_validated_pool": validated}
    groups = {name: group(rows) for name, rows in sources.items()}
    tasks_path = SIDECARS / "official-rlm-prime-pilot-v1/data/tasks.jsonl"
    selection_path = tasks_path.with_name("selection.json")
    paths.extend([tasks_path, selection_path, SIDECARS / "trec-train-process-audit-v1/CONTEXT8_LABEL_MAP.json"])
    selection = json.loads(selection_path.read_text())
    assert sha(tasks_path.read_bytes()) == selection["tasks_sha256"]
    tasks = [json.loads(line) for line in tasks_path.read_text().splitlines()]
    contexts = {row["context_window_id"]: row["context"] for row in tasks}
    old_contexts = {}
    prior_questions = set()
    for context_id, text in sorted(contexts.items()):
        questions = re.findall(r"^Date: .*? \|\| User: .*? \|\| Instance: (.*)$", text, re.M)
        normalized = set(map(normalize, questions))
        assert len(questions) == 89 and normalized <= groups["trec_train"].keys()
        prior_questions.update(normalized)
        old_contexts[str(context_id)] = {
            "context_sha256": sha(text.encode()), "records": len(questions), "unique_groups": len(normalized),
            "local_splits": sorted({r["split"] for r in tasks if r["context_window_id"] == context_id}),
            "source_task_count": sum(r["context_window_id"] == context_id for r in tasks),
            "trec_train_matches": len(normalized & groups["trec_train"].keys()),
            "trec_test_matches": len(normalized & groups["trec_test"].keys()),
            "question_group_sha256": sorted(sha(key.encode()) for key in normalized),
        }
    prior_sources = []
    # Only these pointed-to prior input files are inspected; no run-output/full-repository scan.
    synthetic_paths = [SIDECARS / f"rlvr-e2e-pilot-v1/attempt-00{i}/tasks.json" for i in (1, 2)]
    synthetic_paths.append(SIDECARS / "single-gpu-rlvr-v2/outputs/attempt-001/inventory.json")
    for path in synthetic_paths:
        content = json.loads(path.read_text())
        rows = list(content["tasks"].values()) if isinstance(content, dict) else content
        strings = [record["text"] for row in rows for record in row.get("records", [])]
        if not strings:
            strings = [text for row in rows for text in
                       re.findall(r"^record_\d+ \[facet=[^\]]+\] (.+)$", row["prompt_text"], re.M)]
        assert strings
        normalized = set(map(normalize, strings))
        prior_questions.update(normalized)
        prior_sources.append({"path": str(path), "tasks": len(rows), "record_occurrences": len(strings),
                              "unique_questions": len(normalized),
                              "trec_train_overlap": len(normalized & groups["trec_train"].keys()),
                              "trec_test_overlap": len(normalized & groups["trec_test"].keys())})
        paths.append(path)
    a, b, pool = (set(groups[key]) for key in ("trec_train", "trec_test", "oolong_validated_pool"))
    conflicts = {key for collection in groups.values() for key, rows in collection.items()
                 if len({row["coarse"] for row in rows}) > 1}
    clean_test = b - a - pool - prior_questions - conflicts
    clean_train = a - b - conflicts
    development_candidates = clean_train - pool - prior_questions
    validation = set()
    for label in sorted(LABELS.values()):
        candidates = [key for key in development_candidates if groups["trec_train"][key][0]["coarse"] == label]
        count = 5 if label == "ABBR" else 59
        assert len(candidates) >= count
        candidates.sort(key=lambda key: sha(f"{NAMESPACE}|validation|{key}".encode()))
        validation.update(candidates[:count])
    training = clean_train - validation
    assert len(validation) == 300 and not training & validation and not clean_test & (training | validation)
    assert not validation & (pool | prior_questions) and not clean_test & prior_questions

    def partition(keys, source):
        return [
            {"question_group_sha256": sha(key.encode()),
             "source_line_1based": [row["line_1based"] for row in groups[source][key]],
             "coarse": groups[source][key][0]["coarse"]}
            for key in sorted(keys, key=lambda key: sha(f"{NAMESPACE}|{key}".encode()))
        ]

    split = {"schema": "trec-leaf-proposed-question-partitions-v1", "status": "proposal_not_training_spec",
             "namespace": NAMESPACE, "normalization": "official-loader byte repair; NFKC; casefold; Unicode word tokens joined by spaces",
             "source_train": partition(training, "trec_train"),
             "validation": partition(validation, "trec_train"),
             "test": partition(clean_test, "trec_test"),
             "excluded_test": partition(b - clean_test, "trec_test")}
    split["partition_id"] = sha(json.dumps(split, sort_keys=True, separators=(",", ":")).encode())
    metadata = json.loads((NEW / "oolong_hf_metadata.json").read_text())
    report = {
        "schema": "trec-leaf-split-provenance-inventory-v1", "date": "2026-09-08",
        "source_file_sha256": {str(path): sha(path.read_bytes()) for path in paths},
        "statistics": {name: statistics(rows) for name, rows in sources.items()},
        "overlap": {f"{a_name}__{b_name}": overlap(sources[a_name], sources[b_name])
                    for a_name, b_name in [("trec_train", "trec_test"),
                                            ("trec_train", "oolong_validated_pool"),
                                            ("trec_test", "oolong_validated_pool")]},
        "decoding": {"rule": "Official pinned HF parser replaces byte 0xf0 with ASCII space before UTF-8 decoding",
                     "repaired_train_byte_count": (OLD / "train_5500.label").read_bytes().count(b"\xf0"),
                     "effect": "The sister-city question now exactly matches OOLONG; no fuzzy match or label inference"},
        "old_contexts": old_contexts, "old_context_6_8_shared_questions": 178 - len(set().union(*[
            set(r["question_group_sha256"]) for r in old_contexts.values()])),
        "other_pointed_to_old_inputs": prior_sources,
        "oolong": {
            "dataset_id": "oolongbench/oolong-synth", "dataset_revision": metadata["sha"],
            "dataset_splits": metadata["cardData"]["dataset_info"]["splits"],
            "local_upstream_split": selection["dataset_split"],
            "local_train_contexts": [8], "local_eval_contexts": [6],
            "repository_revision": "0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c",
            "loader_split_behavior": "TREC_Coarse.__init__(split='train') ignores split and always reads validated_data/trec_coarse_validated.jsonl",
            "pool_is_entirely_official_train_after_documented_repair": pool <= a,
            "generating_commit_for_dataset_revision": "not proven; pinned code is corroborating source only",
        },
        "licenses": {"trec_data": "unknown/unspecified; no redistribution grant inferred",
                     "trec_hf_loader": "Apache-2.0 code, HF revision eb1e45c1ba990fecca7cf84b67ce845edbcf49bf",
                     "oolong_repository": "MIT code; upstream TREC rights unresolved",
                     "oolong_hf_dataset": "no license field at pinned revision"},
        "proposed_protocol": {
            "partition_id": split["partition_id"], "train_groups": len(training),
            "validation_groups": len(validation), "test_groups": len(clean_test),
            "test_groups_excluded": len(b - clean_test), "development_candidate_groups": len(development_candidates),
            "validation_counts": dict(sorted(Counter(row["coarse"] for row in split["validation"]).items())),
            "test_counts": dict(sorted(Counter(row["coarse"] for row in split["test"]).items())),
            "zero_normalized_overlap_asserted": ["train/validation", "train/test", "validation/test",
                                                 "validation/entire-validated-OOLONG-pool", "test/entire-validated-OOLONG-pool",
                                                 "validation/explicitly-inspected-prior-inputs", "test/explicitly-inspected-prior-inputs"],
            "aggregation_option": "Hash-shuffle 489 clean test groups into ten disjoint 48-record documents (480 used), with nine reserved. Label permutations/targets may vary, but all variants of a document remain one statistical group.",
            "smallest_training_option": "Predeclare 512 or 1024 source_train groups, one leaf-only SFT epoch, fixed canonical labels; validation decides checkpoint, never test. Freeze separate training recipe before any update.",
            "starting_weights": "Prefer frozen original 4B step0 for clean local-update attribution; compare same checkpoint before/after leaf SFT",
            "test_access_boundary": "Test question-group matching and stratification only in this audit; no model calls/outcome-based selection. Gold remains host/scorer-only in generated aggregation tasks.",
        },
        "unknowns": [
            "No full history/repository scan; only explicit source paths above were checked. Other prior input families/revisions are unverified.",
            "Excluding all official train and the entire validated OOLONG pool protects against prior contexts built from those pools, not arbitrary unknown old sources.",
            "Normalized question equality is not a semantic-paraphrase contamination audit.",
            "TREC is old/public; base-model pretraining contamination is unknown and no absence is claimed.",
            "The new protocol is custom source-disjoint aggregation, not official OOLONG benchmark-wide novelty.",
            "Validation has only five abbreviation questions outside the conservative OOLONG pool exclusion; classwise uncertainty is high.",
        ], "gpu_calls": 0, "frozen_sources_modified": False,
    }
    return report, split


if __name__ == "__main__":
    inventory, proposed = run()
    for name, value in (("INVENTORY.json", inventory), ("PROPOSED_SPLIT.json", proposed)):
        with (ROOT / name).open("x") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps({"statistics": inventory["statistics"],
                      "proposed_protocol": inventory["proposed_protocol"]}, indent=2))
