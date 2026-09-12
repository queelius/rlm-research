"""Bounded owner for the two six-task qualifier blocks."""

import argparse
import functools
import importlib
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback

import collect
import score
import study


_RECOVERY_IMPORT_NAMES = (
    "owner_v7",
    "study_v7",
    "study_v6",
    "study_v5",
    "study_v4",
    "study_v3",
    "study_v2",
    "study",
    "protocol",
)


@functools.lru_cache(maxsize=1)
def dependencies():
    saved_modules = {name: sys.modules.get(name) for name in _RECOVERY_IMPORT_NAMES}
    saved_path = list(sys.path)
    try:
        for name in _RECOVERY_IMPORT_NAMES:
            sys.modules.pop(name, None)
        sys.path.insert(0, str(study.RECOVERY))
        importlib.invalidate_caches()
        recovery_owner = importlib.import_module("owner_v7")
        if Path(recovery_owner.__file__).resolve() != (study.RECOVERY / "owner_v7.py").resolve():
            raise ValueError("recovery owner resolved outside frozen recovery sidecar")
        recovery_owner.s.bind_runtime(recovery_owner.qualified)
        suite = recovery_owner.qualified.dependencies()
        if not all(
            callable(getattr(suite, name, None))
            for name in ("start_service", "release_service", "command")
        ):
            raise ValueError("qualified dependency interface differs")
        return suite
    finally:
        sys.path[:] = saved_path
        for name, module in saved_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def request_count(output):
    return sum(
        1
        for _ in Path(output).glob(
            "blocks/*/collection/rollout/typed-audit/*-request.json"
        )
    )


def semantic_request_audit(rollout):
    rollout = Path(rollout)
    typed_paths = list((rollout / "typed-audit").glob("*-request.json"))
    role_paths = list((rollout / "role-audit").glob("*-request.json"))
    typed = [path.name.removesuffix("-request.json") for path in typed_paths]
    role = [json.loads(path.read_text()).get("request_id") for path in role_paths]
    parity = (
        len(typed) == len(set(typed))
        and len(role) == len(set(role))
        and set(typed) == set(role)
    )
    return {
        "parity": parity,
        "typed_requests": len(typed),
        "role_requests": len(role),
        "unique_typed_request_ids": len(set(typed)),
        "unique_role_request_ids": len(set(role)),
        "typed_only": sorted(set(typed) - set(role)),
        "role_only": sorted(set(role) - set(typed)),
    }


def execute(output, outer_seconds):
    started = time.time()
    output = Path(output)
    if outer_seconds != study.OUTER_SECONDS:
        raise ValueError("exact 700-second external cap required")
    if output.resolve() != study.ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused attempt-001 required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one exclusive GPU and private provider credential required")
    ready = study.verify()
    owned = started + study.OWNED_SECONDS
    work = owned - 90
    output.mkdir(parents=True)
    study.write(
        output / "OWNER_RUN.json",
        {
            "ready_identity": ready["identity"],
            "started_epoch": started,
            "outer_seconds": outer_seconds,
            "owned_seconds": study.OWNED_SECONDS,
            "planned_episodes": 12,
            "blocks": list(study.BLOCK_MODES),
            "block_order": "two blocks because one native CAPTURE_SPEC has one environment depth",
            "gpu": gpu,
            "physical_request_admission_stop_trigger": study.ADMISSION_TRIGGER,
            "trigger_is_not_hard_request_cap": True,
            "updates": 0,
        },
    )
    service = output / "service"
    service.mkdir()
    suite = None
    active = True
    errors = []
    terminals = []
    exported_rows = []
    protocol = {
        "episodes": 0,
        "bad_import_attempts": 0,
        "max_consecutive_identical_code_calls": 1,
        "episodes_with_repeated_identical_action_loop": 0,
    }
    semantic_blocks = []

    def stop(_sig, _frame):
        raise TimeoutError("recursion-interface qualifier ownership deadline")

    prior = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    try:
        signal.setitimer(signal.ITIMER_REAL, max(0.001, owned - time.time()))
        suite = dependencies()
        suite.start_service(service, collect.binding(), min(started + 180, work - 60))
        for block_index, mode in enumerate(study.BLOCK_MODES):
            before = request_count(output)
            if before >= study.ADMISSION_TRIGGER:
                errors.append(
                    {
                        "stage": "admission-stop",
                        "block_index": block_index,
                        "physical_requests_before_block": before,
                    }
                )
                break
            block_started = time.time()
            block = output / "blocks" / f"{block_index:02}-{mode}"
            block.mkdir(parents=True)
            plan = study.make_blocks()[block_index]
            study.write(
                block / "PLANNED_NULL_ENDPOINTS.json",
                [
                    {
                        "coordinate": row,
                        "reward": None,
                        "available": False,
                        "reason": "planned before service",
                    }
                    for row in plan
                ],
            )
            capture = block / "collection"
            capture.mkdir()
            end = min(work, time.time() + 240)
            collect.prepare_spec(
                collect.phase(block_index, mode),
                service / "BINDING.json",
                service / "service/endpoint-original.json",
                capture / "CAPTURE_SPEC.json",
                max(0.001, end - time.time()),
                None,
            )
            argv = [
                str(study.NATIVE),
                str(study.ROOT / "collect.py"),
                "--spec",
                str(capture / "CAPTURE_SPEC.json"),
                "--output",
                str(capture / "rollout"),
                "--deadline",
                str(float(end)),
            ]
            command_error = None
            try:
                suite.command(
                    service,
                    f"recursion-interface-{block_index}-{mode}",
                    argv,
                    max(0.001, end - time.time()),
                    end,
                )
            except Exception as error:
                command_error = {"type": type(error).__name__, "message": str(error)}
            manifest = None
            rows = []
            rollout = capture / "rollout"
            if (rollout / "SPEC.json").exists():
                manifest = collect.export_attempt(rollout, capture / "export")
                rows = study.read(capture / "export/EPISODES.json")
                exported_rows.extend(rows)
                part = score.raw_protocol(rollout)
                protocol["episodes"] += part["episodes"]
                protocol["bad_import_attempts"] += part["bad_import_attempts"]
                protocol["max_consecutive_identical_code_calls"] = max(
                    protocol["max_consecutive_identical_code_calls"],
                    part["max_consecutive_identical_code_calls"],
                )
                protocol["episodes_with_repeated_identical_action_loop"] += part[
                    "episodes_with_repeated_identical_action_loop"
                ]
                semantic_blocks.append({"mode": mode, **semantic_request_audit(rollout)})
            after = request_count(output)
            terminal = {
                "block_index": block_index,
                "mode": mode,
                "complete": command_error is None
                and manifest is not None
                and manifest["complete"]
                and not manifest["integrity_failures"]
                and len(rows) == 6,
                "command_error": command_error,
                "physical_requests_before": before,
                "physical_requests_after": after,
                "physical_requests_in_block": after - before,
                "elapsed_seconds": time.time() - block_started,
                "export_complete": manifest["complete"] if manifest else False,
                "integrity_failures": manifest["integrity_failures"] if manifest else None,
            }
            study.write(block / "BLOCK_TERMINAL.json", terminal)
            terminals.append(terminal)
            if not terminal["complete"]:
                errors.append({"stage": "block", "terminal": terminal})
                break
        semantic = {
            "parity": len(semantic_blocks) == 2 and all(row["parity"] for row in semantic_blocks),
            "blocks": semantic_blocks,
            "typed_requests": sum(row["typed_requests"] for row in semantic_blocks),
            "role_requests": sum(row["role_requests"] for row in semantic_blocks),
        }
        result = score.compute(exported_rows, semantic, protocol)
        result["physical_requests"] = request_count(output)
        result["admission_stop_trigger"] = study.ADMISSION_TRIGGER
        result["measured_trigger_overshoot"] = max(
            0, result["physical_requests"] - study.ADMISSION_TRIGGER
        )
        study.write(output / "RESULT.json", result)
    except BaseException as error:
        errors.append(
            {
                "stage": "owner",
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        remaining = owned - time.time()
        if remaining > 0:
            signal.setitimer(signal.ITIMER_REAL, min(90.0, remaining))
        else:
            errors.append(
                {"stage": "ownership-deadline", "message": "owned deadline expired before release"}
            )
            signal.setitimer(signal.ITIMER_REAL, 0)
        if suite is not None:
            try:
                suite.release_service(service)
                active = False
            except BaseException as error:
                errors.append(
                    {"stage": "release", "type": type(error).__name__, "message": str(error)}
                )
        else:
            active = False
        complete = not errors and len(terminals) == 2 and all(row["complete"] for row in terminals)
        result_path = output / "RESULT.json"
        terminal = {
            "complete": complete,
            "science_gate_pass": study.read(result_path)["gate"]["pass"]
            if result_path.exists()
            else False,
            "released": not active,
            "errors": errors or None,
            "block_terminals": terminals,
            "physical_requests": request_count(output),
            "admission_stop_trigger": study.ADMISSION_TRIGGER,
            "measured_trigger_overshoot": max(
                0, request_count(output) - study.ADMISSION_TRIGGER
            ),
            "elapsed_seconds": time.time() - started,
            "updates": 0,
        }
        study.write(output / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in prior.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=study.OUTER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds)
        print(result)
        raise SystemExit(0 if result["complete"] else 1)
