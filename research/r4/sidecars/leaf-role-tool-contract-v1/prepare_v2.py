"""Seal the additive native-admission and timestamped-provenance correction."""

import os
import subprocess
import sys

import driver_v2
import study as s


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("V2 preparation must hide GPUs")
    for name in ("CPU_TESTS_V2.json", "AMENDMENT_V2.json", "READY_V2.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("V2 preparation requires absent " + name)
    v1 = s.read(s.ROOT / "READY.json")
    if s.sha(s.ROOT / "READY.json") != "7ceb8d719d807fc6f74a53077df542de0319fff804081546cef691d8826e3ec1":
        raise ValueError("preserved V1 READY changed")
    spec = s.read(s.ROOT / "SPEC.json")
    if s.sha(s.ROOT / "SPEC.json") != "6aacecb51ecd046361f714fe666f2e1e72c73d2651fb4116552eb7f001572d6c":
        raise ValueError("frozen V1 science changed")
    expected_budget = {"real_calls": 96, "workers": 4, "max_tokens_per_call": 3072,
        "collector_seconds": 1500, "shared_work_seconds": 1680,
        "owned_seconds": 1770, "outer_seconds": 1800}
    if spec["budget"] != expected_budget or spec["design"]["wall_time_cap_seconds"] != 1500:
        raise ValueError("shared clock budget differs")
    seed = s.read(s.ROOT / "SEED_AUDIT.json")
    if seed["returncode"] != 1 or seed["master"] != s.MASTER_SEED or seed["sampling"] != s.SAMPLE_SEED:
        raise ValueError("frozen seed noncollision audit differs")
    rescan = s.read(s.ROOT / "EXPOSURE_RESCAN.json")
    if rescan["selected_external_overlap"] or not rescan["actual_scan_started_utc"] or \
            not rescan["actual_scan_ended_utc"]:
        raise ValueError("timestamped exposure rescan differs")

    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                            "test_contract.py", "test_amendment.py"], cwd=s.ROOT,
                           env={**os.environ, "CUDA_VISIBLE_DEVICES": "",
                                "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True,
                           text=True, timeout=180)
    s.write_once(s.ROOT / "CPU_TESTS_V2.json", {"argv": tests.args,
        "returncode": tests.returncode, "stdout": tests.stdout, "stderr": tests.stderr,
        "gpu_calls": 0, "model_calls": 0,
        "red": "V2 tests first failed with missing driver/scorer; owner integration then failed because driver_v2 lacked verify.",
        "compatibility": "All 96 completed free-ID attempt-003 raw responses authenticate; strict scores unchanged; parsed-tool, literal-wrapper and final-text routes present."})
    if tests.returncode:
        raise ValueError("focused V2 tests failed")

    old_calls = sorted((s.SOURCE / "outputs/attempt-003/rollout/calls").glob("*.json"))
    if len(old_calls) != 96:
        raise ValueError("free-ID compatibility fixture incomplete")
    fixture_hashes = {str(path): s.sha(path) for path in old_calls}
    sources = dict(v1["source_sha256"])
    for path in (s.ROOT / "READY.json", s.ROOT / "SPEC.json", s.ROOT / "driver_v2.py",
                 s.ROOT / "scoring_v2.py", s.ROOT / "owner_v2.py",
                 s.ROOT / "test_amendment.py", s.ROOT / "rescan_exposure.py",
                 s.ROOT / "EXPOSURE_RESCAN.json", s.ROOT / "CPU_TESTS_V2.json",
                 s.ROOT / "prepare_v2.py"):
        sources[str(path)] = s.sha(path)
    amendment = {"schema": "leaf-role-tool-contract-amendment-v2",
        "preserved_v1_ready_sha256": s.sha(s.ROOT / "READY.json"),
        "preserved_spec_sha256": s.sha(s.ROOT / "SPEC.json"),
        "preserved_data_sha256": s.sha(s.ROOT / "DATA.json"),
        "preserved_requests_sha256": s.sha(s.ROOT / "REQUESTS.json"),
        "preserved_prompt_ids_sha256": s.sha(s.ROOT / "PROMPT_IDS.json"),
        "corrections": [
            "Native prompt, completion tokens/text or tool envelope, unique choice/model, usage and finish branch authenticate before model_completed or scoring.",
            "Any HTTP, parse or native-envelope inconsistency retains raw evidence but resets to infrastructure NULL; authenticated returned tool/code/malformed output remains observed zero.",
            "Summary normalizes score=None and preserves every planned coordinate without finalization crashes.",
            "Timestamped named-catalog rescan replaces the misleading interpretation of 20:00 UTC as original execution time; membership is unchanged."],
        "budget": expected_budget,
        "dispatch_caveat": "V1 inputs and dispatch are frozen and unchanged, so role/tool order was not rotated post hoc. Decoder pairs alternate, but role order can remain confounded with time; require rotated new-context replication for a stronger claim.",
        "seed_audit": seed, "exposure_rescan_sha256": s.sha(s.ROOT / "EXPOSURE_RESCAN.json"),
        "compatibility_fixture_sha256": fixture_hashes,
        "compatibility_scope": "Read-only tokenizer/native-envelope compatibility against completed free-ID96; not new science and not source-prompt equivalence.",
        "source_sha256": sources, "gpu_calls": 0, "model_calls": 0}
    amendment["identity"] = s.digest(amendment)
    s.write_once(s.ROOT / "AMENDMENT_V2.json", amendment)
    sources[str(s.ROOT / "AMENDMENT_V2.json")] = s.sha(s.ROOT / "AMENDMENT_V2.json")
    driver_v2.verify(spec)

    import owner_v2
    owner_v2.module.load_suite()
    ready = {"status": "CPU_READY_V2_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-role-tool-contract-ready-v2",
        "preserved_v1_ready_sha256": s.sha(s.ROOT / "READY.json"),
        "spec_sha256": s.sha(s.ROOT / "SPEC.json"),
        "amendment_sha256": s.sha(s.ROOT / "AMENDMENT_V2.json"),
        "source_sha256": sources, "output": str(s.ROOT / "outputs/attempt-001"),
        "launch_argv": [str(owner_v2.module.NATIVE), str(s.ROOT / "owner_v2.py"), "run",
                        "--output", str(s.ROOT / "outputs/attempt-001")],
        "verify_argv": [str(owner_v2.module.NATIVE), str(s.ROOT / "owner_v2.py"), "verify"],
        "budget": expected_budget,
        "credential": "MAIN privately exports nonempty STRICT_RLM_CALIBRATION_API_KEY before verify/run; value is never serialized.",
        "gpu_calls": 0, "model_calls": 0, "main_owns_gpu_lock_acceptance_and_launch": True}
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY_V2.json", ready)
    print(s.serialize({"ready_v2_sha256": s.sha(s.ROOT / "READY_V2.json"),
                       "identity": ready["identity"], "tests": tests.stdout.strip()}))


if __name__ == "__main__":
    main()
