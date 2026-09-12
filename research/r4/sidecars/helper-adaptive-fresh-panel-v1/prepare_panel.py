"""CPU-only acquisition/selection receipt; no model runner or live-policy implementation."""

from collections import Counter
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import platform
import sys


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
BUILDER = SIDE / "helper-unseen-generalization-panel-v1/build_panel.py"
spec = importlib.util.spec_from_file_location("fresh_adaptive_source_panel", BUILDER)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
NAMESPACE = "helper-adaptive-fresh-panel-v1|202609121200"
QUOTAS = {
    "trec": {
        "human being": 13,
        "location": 13,
        "abbreviation": 0,
        "entity": 13,
        "description and abstract concept": 13,
        "numeric value": 12,
    },
    "ag_news": {"World": 16, "Sports": 16, "Business": 16, "Sci/Tech": 16},
}


def main():
    training, consumed = b.actual_training()
    old_path = BUILDER.parent / "PUBLIC.json"
    root_path = SIDE / "root-question-sensitive-sft-v1/inputs/GROUPS.json"
    old = b.read(old_path)["records"]
    new = [row["public_record"] for row in b.read(b.NEW32)]
    root_ids = {group for row in b.read(root_path) for group in row["group_ids"]}
    text_sets = {
        "actual_c32_train": list(training.values()),
        "current_helper_32": [row["text"] for row in new],
        "old_256_panel": [row["text"] for row in old],
    }
    norms = {
        name: ({b.word_norm(text) for text in texts}, {b.whitespace_norm(text) for text in texts})
        for name, texts in text_sets.items()
    }
    old_sources = {row["source_id"] for row in old}
    old_ids = {row["id"] for row in old}

    def overlap(row):
        word, ws = b.word_norm(row["text"]), b.whitespace_norm(row["text"])
        result = {
            name: word in words or ws in spaces for name, (words, spaces) in norms.items()
        }
        result["known_root_sft_ids"] = row["source_id"] in root_ids or b.text_sha(word) in root_ids
        result["actual_c32_group_ids"] = row["source_id"] in training
        result["old_panel_source_ids"] = row["source_id"] in old_sources
        return result

    inventory, selected = {}, []
    for dataset, candidates in (("trec", b.trec_candidates()), ("ag_news", b.ag_candidates())):
        reasons = {row["source_id"]: overlap(row) for row in candidates}
        eligible = [row for row in candidates if not any(reasons[row["source_id"]].values())]
        picked = b.select(eligible, QUOTAS[dataset], NAMESPACE + "|" + dataset)
        for row in picked:
            row["dataset"] = dataset
            row["id"] = ("t" if dataset == "trec" else "a") + b.text_sha(
                dataset + "|" + row["source_id"]
            )[:15]
            row["word_normalized_sha256"] = b.text_sha(b.word_norm(row["text"]))
            row["whitespace_normalized_sha256"] = b.text_sha(b.whitespace_norm(row["text"]))
        assert len(picked) == 64
        assert dict(Counter(row["label"] for row in picked)) == {
            label: count for label, count in QUOTAS[dataset].items() if count
        }
        inventory[dataset] = {
            "source_candidates": len(candidates),
            "eligible_after_union_exclusion": len(eligible),
            "excluded_union": len(candidates) - len(eligible),
            "eligible_by_label": dict(Counter(row["label"] for row in eligible)),
            "exclusions_by_reason_not_disjoint": {
                name: sum(reason[name] for reason in reasons.values()) for name in overlap(candidates[0])
            },
            "selected_by_label": dict(Counter(row["label"] for row in picked)),
            "selected_source_ids_ordered": [row["source_id"] for row in picked],
        }
        selected.extend(picked)
    assert len(selected) == len({row["id"] for row in selected}) == 128
    assert not old_ids.intersection(row["id"] for row in selected)
    assert not any(any(overlap(row).values()) for row in selected)
    assert len({row["word_normalized_sha256"] for row in selected}) == 128
    assert len({row["whitespace_normalized_sha256"] for row in selected}) == 128
    public = {
        "schema": "helper-generalization-public-v1",
        "contains_gold": False,
        "records": [
            {key: row[key] for key in ("id", "dataset", "source_id", "text")} for row in selected
        ],
    }
    gold = {
        "schema": "helper-generalization-host-gold-v1",
        "never_include_in_model_prompt": True,
        "labels": {row["id"]: row["label"] for row in selected},
    }
    b.write_x(ROOT / "PUBLIC.json", public)
    b.write_x(ROOT / "HOST_GOLD.json", gold)
    b.write_x(ROOT / "SELECTED_PROVENANCE.json", selected)
    trec_receipt_path = b.TREC_CACHE / "PROVENANCE.json"
    ag_receipt_path = b.AG_CACHE / "ACQUISITION.json"
    trec_receipt, ag_receipt = b.read(trec_receipt_path), b.read(ag_receipt_path)
    trec_source = trec_receipt["files"][0]
    assert b.sha(trec_source["path"]) == trec_source["sha256"]
    for artifact in ag_receipt["artifacts"]:
        assert b.sha(artifact["path"]) == artifact["sha256"]
    pins = [
        Path(__file__).resolve(), BUILDER, old_path, root_path, b.NEW32, b.EXPOSURE,
        b.C32_STATE, b.TREC_SFT / "prepared-v1/data.json", b.TREC_SPLIT,
        trec_receipt_path, Path(trec_source["path"]), ag_receipt_path,
        *[Path(row["path"]) for row in ag_receipt["artifacts"]],
        ROOT / "PUBLIC.json", ROOT / "HOST_GOLD.json", ROOT / "SELECTED_PROVENANCE.json",
    ]
    manifest = {
        "schema": "helper-adaptive-fresh-panel-acquisition-v1",
        "status": "CPU_SELECTED_UNSCORED_NOT_A_RUNNABLE_READY",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "namespace": NAMESPACE,
        "selection": "Within-class SHA256(namespace|dataset|source_id), then label-free SHA256(namespace|dataset|panel|source_id); split resulting order into four groups of 16 per dataset.",
        "quota_basis": "Prospective near-balanced five-observed-class TREC and balanced four-class AG News; no model outcomes used.",
        "quotas": QUOTAS,
        "inventory": inventory,
        "overlap_selected_all_checks_zero": True,
        "exclusion_normalization": "Both NFKC/casefold word-token normalization and NFKC/casefold whitespace collapse; source IDs and known root group hashes also excluded.",
        "actual_optimizer_exposure": {
            "unique_c32_questions": len(training),
            "consumptions_per_question": sorted(set(consumed.values())),
            "training_path": str(b.TREC_SFT / "prepared-v1/data.json"),
            "training_key": "train[epoch][batch].records[].group_id/question",
            "consumed_key": "checkpoint-0128/state.json: step_metrics[].group_ids[]",
            "current_rl_unique_questions": len(new),
            "additional_root_sft_catalog_ids_excluded": len(root_ids),
            "scope": "Verified helper-optimization exposure plus this known root catalog; not a complete audit of all root runs or base pretraining.",
            "main_receipt": str(b.EXPOSURE),
        },
        "public_sources": {
            "trec": {
                **trec_source,
                "split": "TREC_10.label test; 489 deduplicated question groups",
                "retrieved_utc_date": trec_receipt["retrieved_utc_date"],
                "normalization_note": "Pinned parser replaces source 0xf0 byte with a space; downloaded loader not executed.",
            },
            "ag_news": ag_receipt,
        },
        "acquisition": "Reused checksum-verified external cache; no new download, installation, remote-code execution, model call, or GPU allocation.",
        "limitations": [
            "All seven TREC abbreviation groups were used by the old panel and are excluded. This panel has five observed gold classes, while model schema remains six labels. Not a replication of the old six-class distribution.",
            "TREC data license remains unspecified and AG News pinned card says unknown/research non-commercial; no permission to redistribute is inferred. Selected texts remain external research artifacts.",
            "Base-model pretraining exposure unknown; fresh means absent from verified local helper optimization and the old evaluation panel, not guaranteed novel to the pretrained model.",
            "64 records and four original request clusters per dataset are exploratory, not confirmatory or a statistical-power claim.",
        ],
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "source_and_artifact_sha256": {str(path): b.sha(path) for path in pins},
    }
    manifest["identity"] = b.digest(manifest)
    b.write_x(ROOT / "MANIFEST.json", manifest)
    print({"status": manifest["status"], "identity": manifest["identity"], "inventory": inventory})


if __name__ == "__main__":
    main()
