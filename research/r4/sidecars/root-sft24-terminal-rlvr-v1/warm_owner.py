"""MAIN-only fixed8 warm-start RLVR owner with protected composition96 readout."""
import argparse
import functools
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback

import warm_collect as collect
import warm_common as common
import warm_export as export
import warm_native as native
import warm_study as study


class MainTermination(BaseException):
    pass


def budget(started):
    return {"started": started, "training_end": started + 5400, "work": started + 10500,
            "owned": started + 10680, "outer": started + 10800, "final_total": 5100}


def cleanup_deadline(now, stage_end, owned):
    return min(now + 30, stage_end, owned)


def learning_window_allowed(cutoff, now=None):
    return cutoff - (time.time() if now is None else now) >= 1320


def remaining(deadline, cap):
    value = min(cap, deadline - time.time())
    if value <= 0:
        raise TimeoutError("shared stage deadline")
    return value


def alarm(deadline):
    signal.setitimer(signal.ITIMER_REAL, max(.001, deadline - time.time()))


@functools.lru_cache(maxsize=1)
def dependencies():
    source = study.QSR / "owner.py"
    pin = "bcb3fdc0fa73321cb8268736cae1790268afe9b79d8c83fa04207f2fa74f3c8b"
    with study.aliases({"qsr_study": study, "qsr_common": common, "qsr_collect": collect,
                        "qsr_export": export, "qsr_native": native}):
        qualified = study.load("warm_qualified_qsr_owner_dependencies", source, pin)
        return qualified.dependencies()


def check_output(output):
    if Path(output).resolve() != study.ATTEMPT.resolve():
        raise ValueError("exact attempt-001 namespace only")
    if Path(output).exists():
        raise FileExistsError("no implicit retry or overwrite")


def collector_argv(stage, deadline):
    return [str(study.NATIVE), str(study.ROOT / "warm_collect.py"), "--spec",
            str(stage / "CAPTURE_SPEC.json"), "--output", str(stage / "rollout"),
            "--deadline", str(float(deadline))]


def trainer_argv(stage, deadline):
    return [str(study.TRAIN), str(study.ROOT / "warm_train.py"), "--group",
            str(stage / "collection/export/GROUP.json"), "--generation",
            str(stage / "GENERATION.json"), "--output", str(stage / "training"),
            "--deadline", str(float(deadline))]


def planned_inventory(output):
    plans = study.read(study.ROOT / "inputs/PLANS.json")
    rows = []
    for window, coordinates in plans["training"].items():
        rows.extend({"phase": "training", "window": int(window), "coordinate": row,
                     "export": str(Path(output) / f"window-{int(window):02d}/collection/export/EPISODES.json"),
                     "reward": None, "available": False, "reason": "planned before service"}
                    for row in coordinates)
    for arm in ("unchanged", "trained"):
        rows.extend({"phase": "readout", "arm": arm, "coordinate": row,
                     "export": str(Path(output) / f"readout-{arm}/export/EPISODES.json"),
                     "reward": None, "available": False, "reason": "planned before service"}
                    for row in plans["readout"])
    return rows


def _usage(records):
    known = {name: 0 for name in ("input", "output", "cached")}
    unknown = {name: 0 for name in known}
    for record in records:
        usage = (record.get("response") or {}).get("usage") or record.get("usage") or {}
        fields = {"input": usage.get("prompt_tokens"), "output": usage.get("completion_tokens"),
                  "cached": (usage.get("prompt_tokens_details") or {}).get("cached_tokens")}
        for name, value in fields.items():
            if type(value) is int and value >= 0:
                known[name] += value
            else:
                unknown[name] += 1
    return {"known": known, "unknown": unknown}


def cost_ledger(output):
    output = Path(output)
    physical_paths = sorted(output.glob("**/physical/*.json"))
    physical = [study.read(path) for path in physical_paths]
    request_paths = sorted(output.glob("**/REQUEST.json"))
    response_paths = sorted(output.glob("**/RESPONSE.json"))
    result_paths = sorted(output.glob("**/RESULT.json"))
    failure_paths = sorted(output.glob("**/FAILURE.json"))
    prepared_unknown = sum(not (path.parent / "RESPONSE.json").exists()
                           and not (path.parent / "RESULT.json").exists() for path in request_paths)
    return {
        "physical_records": sum(bool(row.get("physical_request_attempt")) for row in physical),
        "raw_http_responses": len(response_paths),
        "raw_success_choice_payloads": sum(row.get("status") in range(200, 300)
                                           and bool((row.get("response") or {}).get("choices"))
                                           for row in physical),
        "prepared_attempt_unknown": prepared_unknown,
        "usage": _usage(physical),
        "record_sha256": {str(path): study.sha(path) for path in
                          physical_paths + request_paths + response_paths + result_paths + failure_paths},
        "billing": "not measured", "missing_usage_not_synthesized": True,
    }


def collection_stage(suite, service, stage, phase, deadline, generation=None, cap=600):
    stage.mkdir(parents=True, exist_ok=False)
    end = time.time() + remaining(deadline, cap)
    collect.prepare_spec(phase, service / "BINDING.json", service / "service/endpoint-original.json",
                         stage / "CAPTURE_SPEC.json", remaining(end, cap), generation)
    error = None
    try:
        suite.command(service, "collect-" + phase, collector_argv(stage, end),
                      remaining(end, cap), end)
    except Exception as caught:
        error = {"type": type(caught).__name__, "message": str(caught)}
    if not (stage / "rollout/SPEC.json").exists():
        study.write(stage / "COLLECTION_FAILURE.json", {"error": error,
                    "reason": "collector produced no spec"})
        raise RuntimeError("collector returned no native attempt")
    result = export.export_attempt(stage / "rollout", stage / "export")
    study.write(stage / "COLLECTION_RESULT.json", {"command_error": error,
                "manifest_sha256": study.sha(stage / "export/MANIFEST.json")})
    return result


def train_window(suite, stage, cutoff, generation):
    cap = remaining(cutoff - 60, 480)
    deadline = time.time() + min(240, cap)
    argv = trainer_argv(stage, deadline)
    study.write(stage / "TRAIN_COMMAND.json", {"argv": argv, "process_cap_seconds": cap,
                "started_epoch": time.time(), "all_authentication_math_checkpoint_charged": True})
    with (stage / "training.log").open("x") as log:
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True,
                                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        observed = suite.life.observe(process.pid)
        if observed is None:
            process.wait(timeout=5)
            raise RuntimeError("trainer exited before owned observation")
        owner = suite.life.safe_observation(observed)
        study.write(stage / "TRAIN_OWNER.json", owner)
        try:
            if process.wait(timeout=cap) != 0:
                raise RuntimeError("training nonzero; no retry")
        finally:
            suite.stop_child(process, owner)
            study.write(stage / "TRAIN_EXIT.json", {"returncode": process.returncode,
                        "ended_epoch": time.time()})
    return common.c.checkpoint_policy(stage / "training", generation)


def recover_commit_on_stop(stage, generation, state):
    """Record a trainer-written checkpoint exactly once after an abnormal exit."""
    policy = common.c.checkpoint_policy(stage / "training", generation)
    cursor = common.transition(state["completed_windows"], state["policy"],
                               generation["candidate_window"], policy)
    state.update(policy=policy, completed_windows=cursor["completed_windows"])
    study.write(stage / "COMMIT_RECOVERED_ON_STOP.json", {
        **cursor, "generation": generation, "no_second_update": True,
        "semantics": "a committed update consumes this complete window; no retry",
    })


def execute(output):
    started = time.time()
    limits = budget(started)
    check_output(output)
    study.runtime()
    manifest = study.verify_prepared()
    initial = study.fixed_start()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN must assign exactly one GPU")
    suite = dependencies()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    inventory = planned_inventory(output)
    study.write(output / "PLANNED_NULL_ENDPOINTS.json", inventory)
    study.write(output / "OWNER_RUN.json", {"campaign_id": manifest["campaign_id"], **limits,
                "gpu": gpu, "credential_value_logged": False, "automatic_resume": False,
                "fixed_windows": 8, "planned_training": 192, "planned_final": 96})

    def expired(sig, _frame):
        if sig in (signal.SIGINT, signal.SIGTERM):
            raise MainTermination("MAIN termination")
        raise TimeoutError("owned/shared deadline")

    previous = {sig: signal.signal(sig, expired)
                for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    alarm(limits["owned"])
    state = {"policy": initial, "completed_windows": 0}
    errors, training_stop, readouts, active = [], None, {}, None
    try:
        try:
            for window in range(1, 9):
                if not learning_window_allowed(limits["training_end"]):
                    break
                stage = output / f"window-{window:02d}"
                stage.mkdir()
                generation = common.generation(window, state["policy"])
                study.write(stage / "GENERATION.json", generation)
                service = stage / "service-stage"
                service.mkdir()
                active = service
                try:
                    startup = min(limits["training_end"], time.time() + 180)
                    alarm(startup)
                    suite.start_service(service, collect.binding_for(state["policy"]), startup)
                    result = collection_stage(suite, service, stage / "collection",
                                              f"window-{window}", limits["training_end"] - 540,
                                              generation, 600)
                finally:
                    end = cleanup_deadline(time.time(), limits["training_end"], limits["owned"])
                    alarm(end)
                    suite.release_service(service)
                    active = None
                if not result["complete"] or result["integrity_failures"]:
                    raise RuntimeError("incomplete/integrity-failed window; no partial update")
                new = None
                if result["training_group_episodes"]:
                    alarm(limits["training_end"])
                    try:
                        new = train_window(suite, stage, limits["training_end"], generation)
                    except Exception:
                        checkpoint = stage / "training" / f"checkpoint-{generation['round']}" / "state.json"
                        if checkpoint.exists():
                            recover_commit_on_stop(stage, generation, state)
                        raise
                cursor = common.transition(state["completed_windows"], state["policy"], window, new)
                state.update(policy=cursor["policy"], completed_windows=window)
                study.write(stage / "WINDOW_RESULT.json", {**cursor, "generation": generation,
                            "export_manifest_sha256": study.sha(stage / "collection/export/MANIFEST.json"),
                            "ended_epoch": time.time()})
        except Exception as caught:
            training_stop = {"type": type(caught).__name__, "message": str(caught),
                             "traceback": traceback.format_exc()}
            study.write(output / "TRAINING_STOP.json", training_stop)
        selection = {"rule": "last actually committed RL checkpoint; no outcome selection",
                     "policy": state["policy"], "completed_windows": state["completed_windows"],
                     "actual_optimizer_step": state["policy"]["step"]}
        study.write(output / "SELECTION.json", selection)
        policies = {"unchanged": initial, "trained": state["policy"]}
        for arm in ("unchanged", "trained"):
            block_end = min(limits["work"], time.time() + 2550)
            service = output / f"final-{arm}"
            service.mkdir()
            active = service
            try:
                startup = min(block_end - 30, time.time() + 180)
                alarm(startup)
                suite.start_service(service, collect.binding_for(policies[arm]), startup)
                readouts[arm] = collection_stage(suite, service, output / f"readout-{arm}",
                                                 f"readout-{arm}", block_end - 30, None,
                                                 remaining(block_end - 30, 2340))
            except Exception as caught:
                errors.append({"arm": arm, "type": type(caught).__name__, "message": str(caught)})
                study.write(output / f"READOUT_FAILURE-{arm}.json", errors[-1])
            finally:
                end = cleanup_deadline(time.time(), block_end, limits["owned"])
                alarm(end)
                try:
                    suite.release_service(service)
                    active = None
                except BaseException as caught:
                    errors.append({"arm": arm, "type": type(caught).__name__,
                                   "message": str(caught), "release_failed": True})
                    break
    except (MainTermination, Exception) as caught:
        errors.append({"type": type(caught).__name__, "message": str(caught)})
    finally:
        if active is not None:
            try:
                end = cleanup_deadline(time.time(), limits["owned"], limits["owned"])
                alarm(end)
                suite.release_service(active)
                active = None
            except BaseException as caught:
                errors.append({"type": type(caught).__name__, "message": str(caught),
                               "release_failed": True})
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    cache = {}
    for row in inventory:
        path = Path(row["export"])
        if path.exists():
            if str(path) not in cache:
                cache[str(path)] = {item["episode_id"]: item for item in study.read(path)}
            result = cache[str(path)][row["coordinate"]["id"]]
            row.update(available=result["terminal_observable"], reward=result["endpoint_reward"],
                       training_reward=result["reward"], reason=result["invalid_reason"],
                       export_sha256=study.sha(path))
        else:
            row["reason"] = "unreturned/unrun; partial raw artifacts retained"
    outcome = {"complete": set(readouts) == {"unchanged", "trained"} and not errors
               and all(value["complete"] for value in readouts.values()),
               "selection": {"policy": state["policy"],
                             "completed_windows": state["completed_windows"],
                             "actual_optimizer_step": state["policy"]["step"]},
               "weak_instantiation": state["policy"]["step"] < 3,
               "weak_instantiation_is_not_rerun_authority": True,
               "training_stop": training_stop, "readouts": readouts, "errors": errors,
               "inventory": inventory, "planned_training": 192, "planned_final": 96,
               "elapsed_seconds": time.time() - started, "released": active is None,
               "active_unreleased_service": str(active) if active else None}
    study.write(output / "COST_LEDGER.json", cost_ledger(output))
    study.write(output / "OWNER_TERMINAL.json", outcome)
    return outcome


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(study.verify_prepared()["campaign_id"])
    else:
        result = execute(args.output)
        print({"complete": result["complete"], "step": result["selection"]["actual_optimizer_step"],
               "elapsed_seconds": result["elapsed_seconds"]})
        raise SystemExit(0 if result["complete"] else 1)
