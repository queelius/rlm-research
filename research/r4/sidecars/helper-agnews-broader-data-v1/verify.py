"""Source-to-row and exact schedule audit; no inference or training imports."""

import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import prepare

ROOT = Path(__file__).resolve().parent
old = prepare.old


def verify():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("verification is CPU only")
    started = time.monotonic()
    manifest = old.read(ROOT / "inputs/MANIFEST.json")
    assert (
        old.digest({key: value for key, value in manifest.items() if key != "identity"})
        == manifest["identity"]
    )
    for field in ("source_closure_sha256", "artifacts_sha256"):
        for path, expected in manifest[field].items():
            assert old.sha(Path(path)) == expected, path
    rows = old.source_rows()
    by_id = {row["source_id"]: row for row in rows}
    word_counts = Counter(old.word_norm(row["text"]) for row in rows)
    ws_counts = Counter(old.whitespace_norm(row["text"]) for row in rows)
    provenance = old.read(ROOT / "inputs/SELECTED_PROVENANCE.json")
    selected = [row for step in provenance["training_steps"] for row in step] + provenance[
        "heldout"
    ]
    assert len(selected) == 1536
    excluded, receipt = old.exclusion_inventory()
    excluded_ids = receipt["root_ids"]
    exposure = old.read(ROOT / "inputs/EXCLUSIONS.json")
    for entry in exposure["broader_inventory"]:
        texts, ids = set(), set()
        prepare.extract_public(old.read(Path(entry["path"])), texts, ids)
        excluded.update(old.whitespace_norm(text) for text in texts)
        excluded.update(old.word_norm(text) for text in texts)
        excluded_ids.update(ids)
    for row in selected:
        actual = by_id[row["source_id"]]
        for field in (
            "source_row_0based",
            "text",
            "label",
            "label_id",
            "normalized_text_sha256",
            "word_normalized_sha256",
        ):
            assert row[field] == actual[field], field
        ws, word = old.whitespace_norm(row["text"]), old.word_norm(row["text"])
        assert ws_counts[ws] == 1 and word_counts[word] == 1
        assert ws not in excluded and word not in excluded
        assert row["source_id"] not in excluded_ids
        assert old.text_sha(ws) not in excluded_ids and old.text_sha(word) not in excluded_ids
    assert len({old.word_norm(row["text"]) for row in selected}) == 1536
    assert len({row["source_id"] for row in selected}) == 1536
    replay_steps, replay_heldout, _ = prepare.freeze_selection(rows, excluded, excluded_ids)
    assert replay_steps == provenance["training_steps"]
    assert replay_heldout == provenance["heldout"]
    all_coordinates, all_seeds = set(), set()
    for step in range(1, 9):
        folder = ROOT / f"inputs/step-{step:03d}"
        public = old.read(folder / "PUBLIC.json")
        gold = old.read(folder / "HOST_GOLD.json")["labels"]
        public_ids = [row["id"] for row in public["records"]]
        assert set(public_ids) == set(gold) and len(public_ids) == 128
        assert Counter(gold.values()) == Counter({label: 32 for label in old.AG_LABELS.values()})
        schedule = old.read(folder / "REQUESTS.json")
        assert len(schedule) == 128
        for position, request in enumerate(schedule):
            repeat, group = divmod(position, 32)
            expected_ids = public_ids[group * 4 : group * 4 + 4]
            expected_seed = 202609123000 + 128 * (step - 1) + 4 * group + repeat
            assert request["requested_ids"] == expected_ids
            assert request["repeat"] == repeat and request["seed"] == expected_seed
            assert request["body"]["sampling_params"]["seed"] == expected_seed
            assert request["body"]["sampling_params"]["temperature"] == 0.5
            schema = json.loads(request["schema_ordered_json"])
            assert list(schema["properties"]) == schema["required"] == expected_ids
            assert request["schema_ordered_sha256"] == old.text_sha(request["schema_ordered_json"])
            assert len(request["body"]["token_ids"]) + 1024 <= 8192
            all_coordinates.add(request["coordinate_id"])
            all_seeds.add(request["seed"])
    assert len(all_coordinates) == len(all_seeds) == 1024
    heldout = old.read(ROOT / "inputs/HELDOUT_PUBLIC.json")
    heldout_ids = [row["id"] for row in heldout["records"]]
    heldout_requests = old.read(ROOT / "inputs/HELDOUT_REQUESTS.json")
    assert len(heldout_ids) == 512 and len(heldout_requests) == 128
    for index, request in enumerate(heldout_requests):
        assert request["requested_ids"] == heldout_ids[index * 4 : index * 4 + 4]
        assert request["seed"] == 202609126000 + index
        assert request["body"]["sampling_params"]["temperature"] == 0.0
        assert json.loads(request["schema_ordered_json"])["required"] == request["requested_ids"]
    prior_rows = sum(
        (
            old.read(prepare.FROZEN / name)["records"]
            for name in ("TRAIN_PUBLIC.json", "HELDOUT_PUBLIC.json")
        ),
        [],
    )
    prior_word_duplicate_count = sum(
        word_counts[old.word_norm(row["text"])] > 1 for row in prior_rows
    )
    command = [sys.executable, "-m", "pytest", "-q", str(ROOT / "test_freeze.py")]
    test = subprocess.run(command, capture_output=True, text=True, check=True)
    result = {
        "status": "VERIFIED_DATA_ONLY",
        "manifest_identity": manifest["identity"],
        "manifest_sha256": old.sha(ROOT / "inputs/MANIFEST.json"),
        "source_files_verified": len(manifest["source_closure_sha256"]),
        "artifact_files_verified": len(manifest["artifacts_sha256"]),
        "source_rows_rederived": 1536,
        "selection_reproduced": True,
        "source_id_and_both_normalization_exclusion_overlaps": 0,
        "train_heldout_id_and_both_normalization_overlaps": 0,
        "training_schedules_verified": 8,
        "training_coordinates_verified": 1024,
        "heldout_coordinates_verified": 128,
        "current_train128_plus_heldout256_word_duplicate_rows": prior_word_duplicate_count,
        "model_inference_calls": 0,
        "heldout_records_model_inspected": 0,
        "cpu_test_command": command,
        "cpu_test_returncode": test.returncode,
        "cpu_test_stdout": test.stdout,
        "cpu_test_stderr": test.stderr,
        "elapsed_seconds": time.monotonic() - started,
        "verifier_sha256": old.sha(Path(__file__)),
        "limitations": [
            "base pretraining unknown",
            "license unspecified",
            "schema_ordered_json must restore grammar property order on load",
            "data freeze does not admit a trainer or GPU job",
        ],
    }
    old.write_x(ROOT / "VERIFIED.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    verify()
