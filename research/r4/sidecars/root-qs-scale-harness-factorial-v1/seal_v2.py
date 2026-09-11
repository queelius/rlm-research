"""Additive post-review source seal; immutable inputs and native prompts are unchanged."""

import study as s


def main():
    target = s.ROOT / "READY_v2.json"
    if target.exists():
        raise FileExistsError("V2 seal already exists")
    prior = s.read(s.ROOT / "READY.json")
    for path, expected in prior["input_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("V1 immutable input changed: " + path)
    source_paths = set(prior["source_sha256"])
    source_paths.update(
        str(s.ROOT / name)
        for name in (
            "AMENDMENT_V2.md",
            "seal_v2.py",
            "study.py",
            "owner.py",
            "test_inputs.py",
            "test_runtime.py",
        )
    )
    value = {
        **{key: item for key, item in prior.items() if key not in {"identity", "source_sha256"}},
        "schema": "root-qs-scale-harness-factorial-ready-v2",
        "supersedes_identity": prior["identity"],
        "amendment": "correct OWNER_RUN deadline metadata keys; scientific inputs unchanged",
        "source_sha256": {path: s.sha(path) for path in sorted(source_paths)},
    }
    value["identity"] = s.digest(value)
    s.write(target, value)
    print({"identity": value["identity"], "supersedes": prior["identity"]})


if __name__ == "__main__":
    main()

