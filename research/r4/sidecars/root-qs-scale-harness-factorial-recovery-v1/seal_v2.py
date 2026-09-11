"""Additive seal for the nonempty free-mode transport qualification."""

import study as s


def main():
    target = s.ROOT / "READY_v2.json"
    if target.exists() or s.ATTEMPT.exists():
        raise FileExistsError("unused attempt-002 and unused V2 seal required")
    prior = s.read(s.ROOT / "READY.json")
    for path, expected in prior["input_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("immutable scientific input changed: " + path)
    qualification = s.ROOT / "qualification-transport-attempt-001"
    result = s.read(qualification / "RESULT.json")
    required = {
        "status": "PASS",
        "mode": "free",
        "prepared_size": 256,
        "root_calls": 2,
        "child_calls": 1,
        "actual_model_calls": 0,
        "gpu_calls": 0,
        "strict_scalar_correct": True,
        "view_cap_bytes": 4096,
        "bounded_view_clipped": True,
        "second_root_saw_clip_marker": True,
    }
    if any(result.get(key) != expected for key, expected in required.items()):
        raise ValueError("nonempty free qualification result changed")
    if result["bounded_view_raw_bytes"] <= 4096:
        raise ValueError("qualification did not exercise head/tail clipping")
    source_paths = set(prior["source_sha256"])
    source_paths.update(
        str(s.ROOT / name)
        for name in (
            "AMENDMENT_V2.md",
            "FAILURE_CAUSE.md",
            "seal_v2.py",
            "study.py",
            "qualify_transport.py",
            "test_collector_entry.py",
            "test_recovery.py",
            "test_transport_qualification.py",
        )
    )
    qualification_hashes = {
        str(path): s.sha(path) for path in sorted(qualification.rglob("*")) if path.is_file()
    }
    value = {
        **{key: item for key, item in prior.items() if key not in {"identity", "source_sha256"}},
        "schema": "root-qs-scale-harness-factorial-recovery-ready-v2",
        "status": "GPU_READY_ATTEMPT002_NONEMPTY_QUALIFIED",
        "supersedes_identity": prior["identity"],
        "amendment": "task hook keyword fix plus real prepared free-mode env.run_slot qualification",
        "source_sha256": {path: s.sha(path) for path in sorted(source_paths)},
        "qualification": {
            "path": str(qualification),
            "result_sha256": s.sha(qualification / "RESULT.json"),
            "files_sha256": qualification_hashes,
            "result": result,
        },
    }
    value["identity"] = s.digest(value)
    s.write(target, value)
    print(value["identity"])


if __name__ == "__main__":
    main()

