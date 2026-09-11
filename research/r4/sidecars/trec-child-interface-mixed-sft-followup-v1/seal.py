"""Validate and seal the prospective CPU-only closure."""

import time

import study as s


def main():
    if s.ATTEMPT.exists() or (s.ROOT / "READY.json").exists():
        raise ValueError("unused science output and READY required")
    recipe = s.recipe()
    train = s.read(s.PREPARED / "TRAIN.json")
    plan = s.read(s.PREPARED / "EVAL_PLAN.json")
    bodies = s.read(s.PREPARED / "REQUESTS.json")
    provenance = s.read(s.PREPARED / "PROVENANCE.json")
    if [len(train[arm]) for arm in recipe["arms"]] != [96]:
        raise ValueError("training arms")
    if [sum(row["target_tokens"] for row in train[arm]) for arm in recipe["arms"]] != [23214]:
        raise ValueError("training token closure")
    if len(plan) != 192 or len(bodies) != 192 or {row["id"] for row in plan} != set(bodies):
        raise ValueError("readout closure")
    if (
        provenance["development_clean_split_eligible"] != 125
        or len(provenance["development_split_ineligible"]) != 3
    ):
        raise ValueError("development provenance")
    for row in plan:
        if bodies[row["id"]]["model"] != s.ALIASES[row["model_policy"]]:
            raise ValueError("model alias body")
    sources = [
        s.ROOT / name
        for name in (
            "DESIGN.md",
            "IMPLEMENTATION_REPORT.md",
            "RECIPE.json",
            "study.py",
            "prepare.py",
            "protocol.py",
            "train.py",
            "collect.py",
            "owner.py",
            "seal.py",
            "tests/test_contract.py",
            "tests/test_native.py",
            "CPU_TESTS.json",
            "CPU_INPUT_AUDIT.json",
        )
    ]
    inherited = [
        s.SFT / "source/data.py",
        s.SFT / "source/experiment.py",
        s.START / "adapter_model.safetensors",
        s.START / "adapter_config.json",
        s.START / "state.json",
        s.QUERY / "prepare.py",
        s.QUERY / "study.py",
        s.QUERY / "inputs/PUBLIC.json",
        s.QUERY / "inputs/REQUESTS.json",
        s.QUERY / "outputs/attempt-001/SUMMARY.json",
        s.TEST500 / "inputs/PUBLIC.json",
        s.TEST500 / "inputs/HOST_GOLD.json",
        s.SPLIT / "PROPOSED_SPLIT.json",
        s.SPLIT / "INVENTORY.json",
        s.SUITE / "suite.py",
        s.SIDE / "runtime-an27-5780-v1/service_wrapper_v2.py",
        s.SIDE / "runtime-an27-5780-v1/lifecycle_adapter.py",
        s.SIDE / "runtime-an27-5780-v1/study_wrapper.py",
        s.SIDE / "runtime-an27-5780-v1/credential_preflight.py",
        s.SIDE / "root-rlvr-campaign-v1/campaign_lifecycle_v2.py",
    ]
    inputs = [
        s.PREPARED / name
        for name in (
            "TRAIN.json",
            "PUBLIC.json",
            "HOST_GOLD.json",
            "EVAL_PLAN.json",
            "REQUESTS.json",
            "PROVENANCE.json",
        )
    ]
    ready = {
        "schema": "trec-child-interface-mixed-sft-followup-ready-v1",
        "created_epoch": time.time(),
        "question": (
            "Can balanced mixed-contract continuation gain compact skill without losing full6?"
        ),
        "start_adapter_sha256": s.C32_SHA,
        "arms": recipe["arms"],
        "updates_per_arm": 24,
        "checkpoint_steps": recipe["checkpoint_steps"],
        "selection": recipe["selection"],
        "planned_readout_calls": 192,
        "primary_calls": 96,
        "development_calls": 96,
        "hard_cap_seconds": 3600,
        "gpu_calls_during_preparation": 0,
        "launch_command": f"{s.NATIVE_PYTHON} {s.ROOT / 'owner.py'} run",
        "source_sha256": {str(path): s.sha(path) for path in sources + inherited},
        "input_sha256": {str(path): s.sha(path) for path in inputs},
    }
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__":
    main()
