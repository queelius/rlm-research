"""MAIN-only two-service owner with a fixed1800-second cap and clean release."""

import argparse
import os
import signal
import time

import metrics
import study


def records(output):
    episodes, roots, helpers = [], [], []
    for arm in study.ARMS:
        directory = output / arm
        episodes.extend(study.read(path) for path in sorted((directory / "episodes").glob("*.json")))
        roots.extend(study.read(path) for path in sorted((directory / "root-native").glob("*-result.json")))
        helpers.extend(study.read(path) for path in sorted((directory / "helper-calls").glob("*.json")))
    return episodes, roots, helpers


def execute(cap):
    started = time.time()
    ready = study.verify()
    if cap != study.CAP or study.ATTEMPT.exists():
        raise ValueError("exact1800 cap and unused immutable output required")
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN sole launcher: one GPU and inherited private credential required")
    for arm in ("c32", "rl_step8"):
        if study.binding(arm) != study.read(study.INPUTS / ("BINDING_" + arm + ".json")):
            raise ValueError("fixed original endpoints no longer authenticate")
    output = study.ATTEMPT
    output.mkdir(parents=True)
    deadline = started + cap - 90
    study.write_x(output / "OWNER_RUN.json", {"ready_sha256": study.sha(study.ROOT / "READY.json"),
        "ready_identity": ready["identity"], "started_epoch": started, "cap_seconds": cap,
        "planned_episodes": 48, "planned_contexts": 8, "root_logical_turn_cap": 6,
        "max_physical_root_calls": 288, "max_physical_helper_calls": 128,
        "maximum_physical_calls": 416, "helper_wrapper_is_model_sample": False,
        "service_phases": [["no_child_python", "c32"], ["rl_step8"]],
        "root_training": False, "helper_training": False, "automatic_retries": False})
    lifecycle, suite = study.sources()[2].lifecycle()
    errors, phases, active = [], [], None
    def stop(sig, _frame):
        raise TimeoutError("owner signal " + str(sig))
    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, max(1, started + cap - 30 - time.time()))
    try:
        for phase_index, (helper_arm, arms) in enumerate((("c32", ("no_child_python", "c32")), ("rl_step8", ("rl_step8",)))):
            service = output / ("service-" + str(phase_index))
            service.mkdir()
            active = service
            phase_started = time.time()
            binding = study.read(study.INPUTS / ("BINDING_" + helper_arm + ".json"))
            attestation = None
            released = False
            try:
                suite.start_service(service, binding, min(time.time() + 240, deadline))
                config = study.read(service / "service/inference.json")
                if config["vllm"]["max_model_len"] != 8192:
                    raise ValueError("actual context cap differs from fixed8192")
                study.write_x(service / "SANITIZED_RUNTIME.json", study.sources()[2].sanitized_runtime(config))
                pid = study.read(service / "service/SERVER_START.json")["pid"]
                attestation = lifecycle.attest_engine(service, pid)
                for arm in arms:
                    end = min(deadline, time.time() + 400)
                    if end <= time.time():
                        raise TimeoutError("fixed unattempted tail; no retries")
                    argv = [str(study.NATIVE), str(study.ROOT / "collect.py"), "--arm", arm,
                        "--endpoint", str(service / "service/endpoint-original.json"),
                        "--binding", str(service / "BINDING.json"), "--output", str(output / arm),
                        "--deadline", str(end)]
                    suite.command(service, "ag-live-" + arm, argv, max(.001, end - time.time()), end)
                    _episodes, roots, _helpers = records(output)
                    own = [row for row in roots if row.get("coordinate_id") in {x["id"] for x in study.plan(arm)}]
                    if not any(row.get("status") == "returned" for row in own):
                        raise RuntimeError("no root model response in completed phase; stop runtime failure")
            finally:
                suite.release_service(service)
                stopped = study.read(service / "SERVICE_STOPPED.json")
                released = bool(stopped.get("all_owned_process_identities_exited") and stopped.get("ports_free"))
                if not released:
                    raise RuntimeError("service did not cleanly release")
                active = None
                evidence = lifecycle.finalize_kernel_attestation(service, attestation, released) if attestation is not None else None
                phase = {"helper_arm": helper_arm, "arms": list(arms), "released": released,
                    "runtime_qualified": evidence is not None, "elapsed_seconds": time.time() - phase_started,
                    "kernel_attestation": evidence}
                study.write_x(service / "PHASE_TERMINAL.json", phase)
                phases.append(phase)
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error)})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 60)
        if active is not None:
            try:
                suite.release_service(active)
                active = None
            except BaseException as error:
                errors.append({"stage": "release", "type": type(error).__name__, "message": str(error)})
        result = metrics.summarize(*records(output))
        result.update(runtime_qualified=len(phases) == 2 and all(p["runtime_qualified"] for p in phases),
                      phase_costs=phases, owner_seconds=time.time() - started,
                      cost_boundary="all live root/helper requests; no reused predictions; model training costs separate")
        result["complete"] = result["complete"] and result["runtime_qualified"] and active is None and not errors
        study.write_x(output / "RESULT.json", result)
        terminal = {"complete": result["complete"], "released": active is None, "errors": errors,
                    "elapsed_seconds": time.time() - started, "result_sha256": study.sha(output / "RESULT.json")}
        study.write_x(output / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--owner-seconds", type=int, default=study.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        terminal = execute(args.owner_seconds)
        print(terminal)
        raise SystemExit(0 if terminal["complete"] else 1)
