"""CPU-qualify and seal the fresh paired syntax-only interface screen."""

import json
import os
import subprocess
import time

import collect
import study


def run(argv, timeout):
    started = time.time()
    result = subprocess.run(
        argv,
        cwd=study.ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={
            **os.environ,
            "CUDA_VISIBLE_DEVICES": "",
            "PYTHONDONTWRITEBYTECODE": "1",
            "STRICT_RLM_CALIBRATION_API_KEY": "cpu-structure-only",
        },
    )
    return {
        "argv": argv,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "elapsed_seconds": time.time() - started,
    }


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU preparation requires CUDA hidden")

    plans = {condition: study.make_plan(condition) for condition in study.ARMS}
    study.write(study.ROOT / "PLANS.json", plans)
    study.write(study.PREFIX_INPUT, study.build_prefixes())
    study.prefixes.cache_clear()
    study.write(study.TASK_INPUT, collect.build_task_tables())

    pytest_argv = [
        str(study.NATIVE),
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "test_syntax_screen.py",
    ]
    tests = run(pytest_argv, 300)
    dependency_argv = [
        str(study.NATIVE),
        "-c",
        (
            "import owner,study; suite=owner.dependencies(); "
            "assert suite.SERVE == study.ALLOCATION_RUNTIME/'service_wrapper_v2.py'; "
            "print('dependency-boundary-ok')"
        ),
    ]
    dependency = run(dependency_argv, 120)
    receipt = {
        "schema": "root-qs6-budgeted-evidence-syntax-cpu-tests-v1",
        "pytest": tests,
        "dependency_preflight": dependency,
        "tests": 3,
        "actual_collector_loop_container_fixtures": 2,
        "actual_first_prefix_checks": 2,
        "finite_host_grade_checks": 2,
        "gpu_calls": 0,
        "service_calls": 0,
    }
    study.write(study.ROOT / "CPU_TESTS.json", receipt)
    if tests["returncode"] or dependency["returncode"]:
        raise SystemExit(tests["stdout"] + tests["stderr"] + dependency["stdout"] + dependency["stderr"])

    prompt_inventory = {}
    prefixes = study.prefixes()
    for condition in study.ARMS:
        prompt_inventory[condition] = {
            row["id"]: {
                "prompt_sha256": prefixes[row["id"]]["prompt_sha256"],
                "token_sha256": prefixes[row["id"]]["token_sha256"],
                "token_count": prefixes[row["id"]]["token_count"],
            }
            for row in plans[condition]
        }
    manifest = {
        "schema": "root-qs6-budgeted-evidence-syntax-launch-v1",
        "question": "Does one syntax-only example repair synchronous interface cold start?",
        "arms": list(study.ARMS),
        "planned_root_episodes_per_arm": 24,
        "planned_root_episodes": 48,
        "fresh_paired_root_seeds": list(range(study.SEED_BASE, study.SEED_BASE + 24)),
        "same_task_map_root_policy_generation_and_limits_per_pair": True,
        "only_request_change": "one generic syntax-only illustration in budgeted_syntax_example",
        "syntax_example_excludes": [
            "actual record IDs",
            "labels",
            "subset decision",
            "task operator or algorithm",
            "answer",
            "stopping rule",
            "host gold",
        ],
        "primary_metrics": ["finish_consistent_strict_final", "rejected_api_actions"],
        "secondary_metrics": [
            "strict_final_correct_incorrect_unknown",
            "logical_distinct_ids_requested",
            "root_calls_and_tokens",
            "unknown_usage",
            "information_access_flags",
        ],
        "wrong_finals_retained": True,
        "actual_child_model_calls": 0,
        "updates": 0,
        "claim_boundary": (
            "Two research-exposed training contexts and replayed saved helper maps; interface "
            "competence only, not fresh generalization, helper speedup, or architecture promotion."
        ),
        "prompt_inventory": prompt_inventory,
        "owner_seconds": 1000,
        "outer_seconds": study.OUTER_SECONDS,
        "per_arm_seconds": study.ARM_SECONDS,
        "checkpoint_policy": "write each raw row, episode, evidence receipt, and owner terminal; no retry",
        "output": str(study.ATTEMPT),
    }
    study.write(study.ROOT / "LAUNCH_MANIFEST.json", manifest)

    previous = study.read(study.SOURCE / "READY_V2.json")
    for path, expected in previous["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("accepted V2 source closure changed: " + path)
    local_sources = [
        study.ROOT / name
        for name in (
            "study.py",
            "collect.py",
            "owner.py",
            "prepare.py",
            "test_syntax_screen.py",
            "QUESTION.md",
            "RUNBOOK.md",
            "PLANS.json",
            "PREFIXES.json",
            "TASKS.json",
            "LAUNCH_MANIFEST.json",
            "CPU_TESTS.json",
        )
    ]
    closure = dict(previous["closure_sha256"])
    closure[str((study.SOURCE / "READY_V2.json").resolve())] = study.sha(
        study.SOURCE / "READY_V2.json"
    )
    closure.update({str(path.resolve()): study.sha(path) for path in local_sources})
    environment = collect.environment_config()
    ready = {
        "schema": "root-qs6-budgeted-evidence-syntax-ready-v1",
        "status": "CPU_READY_FOR_MAIN_OWNER_LAUNCH",
        "identity": None,
        "arms": list(study.ARMS),
        "plan_ids": {
            condition: [row["id"] for row in plans[condition]] for condition in study.ARMS
        },
        "pair_ids": [row["pair_id"] for row in plans[study.ARMS[0]]],
        "fresh_paired_root_seeds": list(range(study.SEED_BASE, study.SEED_BASE + 24)),
        "prompt_condition_sha256": {
            condition: study.digest(prompt_inventory[condition]) for condition in study.ARMS
        },
        "planned_root_episodes": 48,
        "actual_child_model_calls": 0,
        "updates": 0,
        "root_max_depth": environment["agent"]["harness"]["max_depth"],
        "root_timeout": environment["agent"]["timeout"],
        "owner_seconds": 1000,
        "outer_seconds": study.OUTER_SECONDS,
        "per_arm_seconds": study.ARM_SECONDS,
        "output": str(study.ATTEMPT),
        "closure_sha256": closure,
        "argv": [
            str(study.NATIVE),
            str(study.ROOT / "owner.py"),
            "run",
            "--output",
            str(study.ATTEMPT),
            "--outer-seconds",
            str(study.OUTER_SECONDS),
        ],
        "prepared_epoch": time.time(),
        "gpu_calls": 0,
        "service_calls": 0,
    }
    ready["identity"] = study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    )
    study.write(study.ROOT / "READY.json", ready)
    print(
        json.dumps(
            {
                "identity": ready["identity"],
                "ready_sha256": study.sha(study.ROOT / "READY.json"),
                "argv": ready["argv"],
            }
        )
    )


if __name__ == "__main__":
    main()

