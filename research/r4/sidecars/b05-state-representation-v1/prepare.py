"""Seal the outcome-blind 72-call public-state representation screen."""

from datetime import datetime, timezone
import json
import subprocess

import owner
import study as s


DIMENSIONS = [(1,6,0),(1,6,1),(1,12,2),(1,12,0),(1,20,1),(1,20,2),
              (3,6,0),(3,6,1),(3,6,2),(3,12,0),(3,12,1),(3,12,2)]


def main():
    assert not s.READY_RUN.exists() and not s.ATTEMPT.exists()
    assert s.sha(s.PRIOR / "CPU_READY.json") == (
        "109f3f0e1ea54bc53dbb0dd52a9544cd97e8292d15c0851f04e5e6c43992f5c0")
    prior_terminal = s.read(s.PRIOR / "outputs/attempt-001/OWNER_TERMINAL.json")
    assert all(prior_terminal[key] for key in ("complete", "released", "runtime_qualified"))
    data = s.read(s.ROOT / "DATA_READY.json")
    assert data["tasks"] == 12 and data["planned_calls"] == 72
    assert data["generation_seed_range"] == [202609400000, 202609400011]
    assert data["decode_seed_range"] == [202609410000, 202609410023]

    command = [str(s.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider",
               str(s.ROOT / "test_screen.py")]
    result = subprocess.run(command, cwd=s.ROOT, capture_output=True, text=True)
    s.write_x(s.ROOT / "CPU_TESTS_V2.json", {
        "schema": "b05-state-representation-cpu-tests-v1", "command": command,
        "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
        "real_public_transform_fixture": True, "actual_three_view_native_http_path": True,
        "GPU_calls": 0, "model_calls": 0})
    assert result.returncode == 0, result.stdout + result.stderr
    owner.implementation()

    closure = dict(s.read(s.PRIOR / "CPU_READY.json")["closure_sha256"])
    explicit = [
        s.PRIOR / "CPU_READY.json",
        s.PRIOR / "outputs/attempt-001/OWNER_TERMINAL.json",
        s.PRIOR / "outputs/attempt-001/RESULT.json",
        s.prior.PRIOR / "normalize.py",
        s.ROOT.parents[1] / "questions/public-state-and-decision-accounting.md",
        s.SOURCE / "inputs/PUBLIC.json",
        s.ROOT.parents[1] / "ideas/b05-helper-width-feasibility-2026-09-12/public/PUBLIC.json",
        s.TRAIN / "HELD_PUBLIC.json",
        s.PRIOR / "PUBLIC_ROOTS.json",
        s.ROOT.parent / "b05-eligible-ids-interface-v1/interface.py",
    ]
    local = list(s.ROOT.glob("*.py")) + list(s.ROOT.glob("*.json")) + [
        s.ROOT / "QUESTION.md", s.ROOT / "RUNBOOK.md"]
    for path in local + explicit:
        closure[str(path)] = s.sha(path)

    audit = s.read(s.ROOT / "TOKEN_PREFLIGHT.json")["rows"]
    ready = {
        "schema": "b05-state-representation-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "argv": [str(s.NATIVE), str(s.ROOT / "owner.py"), "run", "--outer-seconds", "1000"],
        "launch_authority": "MAIN only",
        "question": "Does candidate-local grouping help beyond raw tables before host resolution?",
        "context_units": 12,
        "paired_seed_units": 24,
        "planned_physical_calls": 72,
        "arms": ["raw", "unresolved", "resolved"],
        "dimensions": DIMENSIONS,
        "generation_seed_range": [202609400000, 202609400011],
        "decode_seed_range": [202609410000, 202609410023],
        "same_decode_seed_across_three_views": True,
        "model": str(s.MODEL), "model_alias": s.MODEL_ALIAS, "adapter": None,
        "temperature": 0.5, "top_p": 1.0, "top_k": -1, "max_tokens": 384,
        "input_cap": 8192, "concurrency": 4,
        "science_seconds": 900, "owner_seconds": 1000, "external_seconds": 1100,
        "input_tokens_by_arm": {
            arm: {"min": min(row["input_tokens"] for row in audit if row["arm"] == arm),
                  "max": max(row["input_tokens"] for row in audit if row["arm"] == arm)}
            for arm in ("raw", "unresolved", "resolved")},
        "unresolved_contract": {
            "candidate_local_grouping": True,
            "all_base_implementation_rows_retained": True,
            "all_applicable_public_change_rows_retained": True,
            "all_applicable_public_check_rows_retained": True,
            "applies_deltas": False, "selects_latest_check": False,
            "computes_eligibility": False, "filters_candidates": False,
            "reads_host_gold": False},
        "resolved_contract": "identical pinned normalizer used by the qualified fresh12 screen",
        "primary": "unordered known unique-ID exact; BA and precision/recall use explicit valid-set denominators",
        "strict_sorted_format_separate": True, "unknown_is_not_wrong": True,
        "all_candidates_retained": True, "no_annotation_or_outcome_filter": True,
        "no_prior_root_or_candidate_id_overlap": True,
        "natural_model_calls_per_answer": 1,
        "input_wording_and_token_lengths_not_matched": True,
        "representation_change_not_pure_resolution_causal_effect": True,
        "fresh_same_generator_family_not_new_dataset": True,
        "not_learned_decomposition": True,
        "response_sha256_semantics": "canonical parsed JSON digest; physical response JSON retained",
        "cpu_tests": "CPU_TESTS_V2.json; CPU_TESTS.json is the preserved pre-seal receipt",
        "closure_sha256": dict(sorted(closure.items())),
    }
    ready["identity"] = s.digest(ready)
    s.write_x(s.READY_RUN, ready)
    s.verify()
    print(json.dumps({"ready": str(s.READY_RUN), "sha256": s.sha(s.READY_RUN),
                      "identity": ready["identity"], "closure_files": len(closure),
                      "input_tokens_by_arm": ready["input_tokens_by_arm"]}, indent=2))


if __name__ == "__main__":
    main()
