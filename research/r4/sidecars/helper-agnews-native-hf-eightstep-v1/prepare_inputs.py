"""Build host-only contextual reward maps; all public prompts remain frozen."""

import os

import core


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (core.ROOT / "inputs").exists():
        raise ValueError("CPU-only fresh input preparation required")
    manifest = core.read(core.DATA / "inputs/MANIFEST.json")
    for field in ("source_closure_sha256", "artifacts_sha256"):
        for path, expected in manifest[field].items():
            if core.sha(path) != expected:
                raise ValueError("broader frozen data changed: " + path)
    for step in range(1, 9):
        gold = core.read(core.DATA / f"inputs/step-{step:03d}/HOST_GOLD.json")["labels"]
        rows = core.read(core.DATA / f"inputs/step-{step:03d}/REQUESTS.json")
        host = {
            row["context_id"]: {"labels": {key: gold[key] for key in row["requested_ids"]}}
            for row in rows
        }
        if len(host) != 32:
            raise ValueError("exact32 four-record reward groups required")
        core.write_x(core.ROOT / f"inputs/step-{step:03d}/HOST_GOLD.json", host)
    bounds = core.read(core.DATA / "inputs/TOKEN_BOUNDS.json")
    maximum = max(bounds[f"step-{step:03d}"]["max_prompt_plus_completion"] for step in range(1, 9))
    if maximum > 8192:
        raise ValueError("8192 context bound exceeded")
    core.write_x(
        core.ROOT / "inputs/BUILD_AUDIT.json",
        {
            "max_prompt_plus_completion": maximum,
            "required_context_cap": 8192,
            "data_manifest_sha256": core.sha(core.DATA / "inputs/MANIFEST.json"),
            "training_unique_records": 1024,
            "heldout_used_in_training_or_selection": False,
        },
    )


if __name__ == "__main__":
    main()
