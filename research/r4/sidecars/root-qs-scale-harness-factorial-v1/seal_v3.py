"""Additive seal for recursive qualified-QS authentication."""

import study as s


def main():
    target = s.ROOT / "READY_v3.json"
    if target.exists():
        raise FileExistsError("V3 seal already exists")
    prior = s.read(s.ROOT / "READY_v2.json")
    for path, expected in prior["input_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("immutable input changed: " + path)
    source_paths = set(prior["source_sha256"])
    source_paths.update(
        str(s.ROOT / name)
        for name in (
            "AMENDMENT_V3.md",
            "seal_v3.py",
            "study.py",
            "test_inputs.py",
            "test_runtime.py",
        )
    )
    value = {
        **{key: item for key, item in prior.items() if key not in {"identity", "source_sha256"}},
        "schema": "root-qs-scale-harness-factorial-ready-v3",
        "supersedes_identity": prior["identity"],
        "amendment": "recursively invoke qualified QS replication verification",
        "source_sha256": {path: s.sha(path) for path in sorted(source_paths)},
    }
    value["identity"] = s.digest(value)
    s.write(target, value)
    print({"identity": value["identity"], "supersedes": prior["identity"]})


if __name__ == "__main__":
    main()

