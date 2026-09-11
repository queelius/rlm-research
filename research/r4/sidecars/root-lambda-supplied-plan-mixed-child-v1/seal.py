"""Seal the exact mixed-child supplied-plan40 closure."""

import time

import study as s


def main():
    if s.ATTEMPT.exists() or (s.ROOT / "READY.json").exists():
        raise ValueError("unused output and READY required")
    plan = s.read(s.ROOT / "inputs/PLAN.json")
    requests = s.read(s.ROOT / "inputs/REQUESTS.json")
    prior = s.PRIOR_CEILING / "inputs"
    old_plan = s.read(prior / "PLAN.json")
    if len(plan) != len(requests) or len(plan) != len(old_plan) or len(plan) != 40:
        raise ValueError("exact supplied plan40")
    old_requests = s.read(prior / "REQUESTS.json")
    for row, old_row in zip(plan, old_plan, strict=True):
        if row["model_policy"] != "mixed_sft24":
            raise ValueError("mixed policy coordinate")
        if ({key: value for key, value in row.items() if key not in ("id", "model_policy")}
                != {key: value for key, value in old_row.items()
                    if key not in ("id", "model_policy")}):
            raise ValueError("science coordinate changed")
        body = requests[row["id"]]
        old = old_requests[old_row["id"]]
        if body["model"] != s.MIXED_ALIAS:
            raise ValueError("mixed alias")
        if {**body, "model": None} != {**old, "model": None}:
            raise ValueError("science request changed")
    if s.sha(s.MIXED / "adapter_model.safetensors") != s.MIXED_SHA:
        raise ValueError("mixed checkpoint")
    sources = [s.ROOT / name for name in (
        "DESIGN.md", "PLAN.md", "IMPLEMENTATION_REPORT.md", "study.py", "prepare.py",
        "protocol.py", "collect.py", "owner.py", "analysis.py", "seal.py",
        "test_bridge.py", "test_protocol.py", "test_runtime.py", "CPU_TESTS.json")]
    inherited = [s.PRIOR_CEILING / "READY.json",
                 s.PRIOR_CEILING / "outputs/attempt-001/OWNER_TERMINAL.json",
                 s.MIXED_ROOT / "READY.json",
                 s.MIXED_ROOT / "outputs/attempt-001/OWNER_TERMINAL.json",
                 s.MIXED.parent / "SELECTION.json"]
    for step in (6, 12, 18, 24):
        checkpoint = s.MIXED.parent / f"checkpoint-{step:04d}"
        inherited.extend([checkpoint / "state.json", checkpoint / "adapter_model.safetensors",
                          checkpoint / "optimizer.pt", checkpoint / "rng_state.pt"])
    inputs = sorted((s.ROOT / "inputs").glob("*.json"))
    ready = {
        "schema": "root-lambda-supplied-plan-mixed-child-ready-v1",
        "created_epoch": time.time(),
        "question": "Does mixed child training improve six-class labels and downstream public J1?",
        "mixed_adapter_sha256": s.MIXED_SHA,
        "planned_child_calls": 40, "planned_episodes": 8, "clusters": 4,
        "sizes": [64, 256], "root_model_calls": 0, "no_retry": True, "no_repair": True,
        "outer_seconds": 1200, "work_seconds": 1080, "owned_seconds": 1170,
        "gate": {"cluster_sum_absolute_error_improves": 3,
                 "exact_episode_gain": 2, "availability_loss_allowed": 0},
        "source_sha256": {str(path): s.sha(path) for path in sources + inherited},
        "input_sha256": {str(path): s.sha(path) for path in inputs},
        "launch_command": f"{s.NATIVE} {s.ROOT / 'owner.py'} run",
        "no_gpu_launch": True,
    }
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__": main()
