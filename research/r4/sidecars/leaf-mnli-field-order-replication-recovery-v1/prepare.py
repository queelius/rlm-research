"""Seal the immutable attempt-002 continuation after the zero-science attempt-001 failure."""

from pathlib import Path
import study as s


SCIENTIFIC = (
    "ALIEN_DICTIONARIES.json",
    "CPU_NATIVE.json",
    "DATA.json",
    "DATASET_MANIFEST.json",
    "ORDERED_REQUESTS.json",
    "PLAN.json",
    "PLANNED_NULL_ENDPOINTS.json",
    "PROMPT_IDS.json",
    "PUBLIC.json",
    "REQUESTS.json",
    "SELECTION_AUDIT.json",
)


def main():
    target = s.ROOT / "READY.json"
    if target.exists() or s.ATTEMPT.exists():
        raise FileExistsError("unused immutable recovery namespace required")
    prior = s.read(s.ORIGINAL / "READY.json")
    for name in SCIENTIFIC:
        local = s.ROOT / name
        original = s.ORIGINAL / name
        expected = prior["input_sha256"][str(original)]
        if local.resolve() != original.resolve() or s.sha(local) != expected:
            raise ValueError("scientific input differs: " + name)
    failed = s.ORIGINAL / "outputs/attempt-001"
    terminal = s.read(failed / "OWNER_TERMINAL.json")
    if terminal["complete"] or not terminal["released"] or terminal["collector_status"] is not None:
        raise ValueError("attempt-001 was not the retained released prelaunch failure")
    if (failed / "rollout").exists():
        raise ValueError("attempt-001 unexpectedly contains scientific rollout artifacts")
    log = (failed / "owned-service/launcher.log").read_text()
    if "AttributeError: module 'study' has no attribute 'ALIEN'" not in log:
        raise ValueError("retained failure cause changed")
    sources = [
        s.ROOT / name
        for name in (
            "FAILURE_CAUSE.md",
            "prepare.py",
            "study.py",
            "protocol.py",
            "scoring.py",
            "owner.py",
            "collect.py",
            "service_wrapper.py",
            "test_service_entry.py",
            "test_recovery.py",
        )
    ]
    sources.extend(
        [
            s.ORIGINAL / "READY.json",
            s.ORIGINAL / "study.py",
            s.ORIGINAL / "protocol.py",
            s.ORIGINAL / "scoring.py",
            s.ORIGINAL / "owner.py",
            s.ORIGINAL / "collect.py",
            failed / "OWNER_TERMINAL.json",
            failed / "owned-service/launcher.log",
            failed / "owned-service/SERVICE_STOPPED.json",
        ]
    )
    value = {
        "schema": "leaf-mnli-field-order-replication-recovery-ready-v1",
        "status": "GPU_READY_ATTEMPT002",
        "scientific_inputs_identity": prior["identity"],
        "scientific_input_sha256": {
            name: prior["input_sha256"][str(s.ORIGINAL / name)] for name in SCIENTIFIC
        },
        "source_sha256": {str(path): s.sha(path) for path in sources},
        "input_sha256": {str(s.ROOT / name): s.sha(s.ROOT / name) for name in SCIENTIFIC},
        "attempt001": {
            "path": str(failed),
            "owner_terminal_sha256": s.sha(failed / "OWNER_TERMINAL.json"),
            "launcher_log_sha256": s.sha(failed / "owned-service/launcher.log"),
            "physical_requests": 0,
            "scientific_outcomes": 0,
            "released": True,
        },
        "attempt002": {
            "path": str(s.ATTEMPT),
            "planned": 96,
            "outer_seconds": 1800,
            "owned_seconds": 1770,
            "work_seconds": 1680,
            "no_retry": True,
            "gpu_launch_authority": "MAIN only",
        },
        "change": "service wrapper binds immediate qualified ancestral study; no scientific change",
        "scientific_gpu_calls_during_recovery_preparation": 0,
    }
    value["identity"] = s.digest(value)
    s.write(target, value)
    print(value["identity"])


if __name__ == "__main__":
    main()

