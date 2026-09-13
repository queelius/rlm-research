"""Write additive test and cross-panel disjointness receipts without changing the seal."""

from datetime import datetime, timezone
import json
import subprocess

import study as s


VECTOR = s.ROOT.parent / "b05-decision-vector-v1/PUBLIC_ROOTS.json"


def safe_roots(path):
    return [row.get("safe_root", row) for row in s.read(path)["roots"]]


def identifiers(roots):
    root_ids = {root["root_id"] for root in roots}
    candidate_ids = {item["implementation_id"] for root in roots for stage in root["stages"]
                     for item in stage["tables"]["implementations"]}
    return root_ids, candidate_ids


def main():
    ready_sha_before = s.sha(s.READY_RUN)
    assert ready_sha_before == "e4d9bb044e40a71423bf3a2bb27a09a1cccc9405b8aed7bee8ca446fc402165a"
    command = [str(s.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider",
               str(s.ROOT / "test_transport_scoring_addendum.py")]
    result = subprocess.run(command, cwd=s.ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = {
        "schema": "b05-state-representation-transport-scoring-addendum-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "ready_path": str(s.READY_RUN), "ready_sha256": ready_sha_before,
        "ready_identity": s.read(s.READY_RUN)["identity"],
        "test_path": str(s.ROOT / "test_transport_scoring_addendum.py"),
        "test_sha256": s.sha(s.ROOT / "test_transport_scoring_addendum.py"),
        "command": command, "returncode": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
        "asserted_physical_records": 3,
        "asserted_transport_valid": 3,
        "asserted_available": 3, "asserted_unknown": 69,
        "asserted_semantic_valid_empty_set_per_arm": 1,
        "asserted_current_owner_import_bindings": True,
        "sealed_ready_unchanged": s.sha(s.READY_RUN) == ready_sha_before,
        "GPU_calls": 0, "model_calls": 0,
    }
    s.write_x(s.ROOT / "TRANSPORT_SCORING_ADDENDUM.json", receipt)

    current = safe_roots(s.ROOT / "PUBLIC_ROOTS.json")
    vector = safe_roots(VECTOR)
    current_roots, current_candidates = identifiers(current)
    vector_roots, vector_candidates = identifiers(vector)
    cross = {
        "schema": "b05-state-representation-cross-panel-disjointness-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "representation_public_roots": str(s.ROOT / "PUBLIC_ROOTS.json"),
        "representation_public_roots_sha256": s.sha(s.ROOT / "PUBLIC_ROOTS.json"),
        "vector_public_roots": str(VECTOR), "vector_public_roots_sha256": s.sha(VECTOR),
        "representation_root_count": len(current_roots),
        "vector_root_count": len(vector_roots),
        "representation_candidate_id_count": len(current_candidates),
        "vector_candidate_id_count": len(vector_candidates),
        "root_id_intersection": sorted(current_roots & vector_roots),
        "candidate_id_intersection": sorted(current_candidates & vector_candidates),
        "root_ids_disjoint": not current_roots & vector_roots,
        "candidate_ids_disjoint": not current_candidates & vector_candidates,
        "comparison_uses_sealed_public_manifests_only": True,
        "no_model_outputs_or_host_gold_used": True,
        "sealed_ready_sha256": ready_sha_before,
        "GPU_calls": 0, "model_calls": 0,
    }
    assert cross["root_ids_disjoint"] and cross["candidate_ids_disjoint"]
    s.write_x(s.ROOT / "CROSS_PANEL_AUDIT.json", cross)
    print(json.dumps({
        "transport_receipt": str(s.ROOT / "TRANSPORT_SCORING_ADDENDUM.json"),
        "transport_receipt_sha256": s.sha(s.ROOT / "TRANSPORT_SCORING_ADDENDUM.json"),
        "cross_panel_receipt": str(s.ROOT / "CROSS_PANEL_AUDIT.json"),
        "cross_panel_receipt_sha256": s.sha(s.ROOT / "CROSS_PANEL_AUDIT.json"),
        "sealed_ready_sha256": s.sha(s.READY_RUN),
    }, indent=2))


if __name__ == "__main__":
    main()
