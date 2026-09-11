"""Seal the additive zero-outcome attempt-002 continuation."""

from pathlib import Path
import study as s


def main():
    target = s.ROOT / "READY.json"
    if target.exists() or s.ATTEMPT.exists():
        raise FileExistsError("unused immutable recovery namespace required")
    prior = s.read(s.ORIGINAL / "READY_v3.json")
    if (s.ROOT / "inputs").resolve() != (s.ORIGINAL / "inputs").resolve():
        raise ValueError("recovery inputs must resolve to the immutable original directory")
    for old_path, expected in prior["input_sha256"].items():
        name = Path(old_path).name
        if s.sha(s.ROOT / "inputs" / name) != expected:
            raise ValueError("scientific input changed: " + name)
    failed = s.ORIGINAL / "outputs/attempt-001"
    terminal = s.read(failed / "OWNER_TERMINAL.json")
    ledger = s.read(failed / "COST_LEDGER.json")
    if terminal["complete"] or not terminal["released"] or len(terminal["error"] or []) != 2:
        raise ValueError("attempt-001 terminal is not the released two-service failure")
    if ledger["full_native"]["physical_requests_attempted"] != 0:
        raise ValueError("attempt-001 was not zero-science")
    logs = [failed / f"service-{arm}/readout32.log" for arm in ("sft6", "unchanged")]
    for path in logs:
        if "AttributeError: module 'study' has no attribute 'JOINT'" not in path.read_text():
            raise ValueError("collector failure cause changed")
    sources = [
        s.ROOT / name
        for name in (
            "FAILURE_CAUSE.md",
            "prepare.py",
            "study.py",
            "protocol.py",
            "collect.py",
            "owner.py",
            "test_collector_entry.py",
            "test_recovery.py",
        )
    ]
    sources.extend(
        [
            s.ORIGINAL / "READY_v3.json",
            s.ORIGINAL / "study.py",
            s.ORIGINAL / "collect.py",
            s.ORIGINAL / "owner.py",
            failed / "OWNER_TERMINAL.json",
            failed / "COST_LEDGER.json",
            *logs,
        ]
    )
    input_hashes = {
        str(s.ROOT / "inputs" / Path(path).name): expected
        for path, expected in prior["input_sha256"].items()
    }
    value = {
        "schema": "root-qs-scale-harness-factorial-recovery-ready-v1",
        "status": "GPU_READY_ATTEMPT002",
        "scientific_inputs_identity": prior["identity"],
        "source_sha256": {str(path): s.sha(path) for path in sources},
        "input_sha256": input_hashes,
        "attempt001": {
            "path": str(failed),
            "owner_terminal_sha256": s.sha(failed / "OWNER_TERMINAL.json"),
            "cost_ledger_sha256": s.sha(failed / "COST_LEDGER.json"),
            "readout_log_sha256": {str(path): s.sha(path) for path in logs},
            "physical_requests": 0,
            "scientific_outcomes": 0,
            "released": True,
        },
        "attempt002": {
            "path": str(s.ATTEMPT),
            "planned": 64,
            "outer_seconds": 3600,
            "owned_seconds": 3570,
            "work_seconds": 3420,
            "no_retry": True,
            "gpu_launch_authority": "MAIN only",
        },
        "complete_study_surface": [
            "JOINT",
            "LABELS",
            "ATTEMPT",
            "ROOT",
            "corpus",
            "interface",
            "load",
            "read",
            "runtime",
            "sha",
            "stack",
            "verify",
            "write",
            "answer",
            "aliases",
            "validate",
        ],
        "complete_protocol_surface": [
            "correction",
            "error_probe",
            "layout",
            "null_row",
            "physical_cost",
            "producer",
            "row",
            "scalar",
            "target_spans",
            "verify_replay",
            "visible_maps",
        ],
        "change": "complete inherited collector interfaces only; scientific inputs unchanged",
        "scientific_gpu_calls_during_recovery_preparation": 0,
    }
    value["identity"] = s.digest(value)
    s.write(target, value)
    print(value["identity"])


if __name__ == "__main__":
    main()

