"""MAIN-only training owner for exact remaining windows 4 through 8."""
import argparse
import json
import os
import signal
import subprocess
import time
import traceback
from pathlib import Path

import continuation_study as study

collect = study.collect
export = study.export


def budget(start):
    return {"started": start, "work": start + 11700, "owned": start + 11970,
            "outer": start + 12000}


def planned_inventory(output):
    rows = []
    for window in range(4, 9):
        rows.extend({"phase": "training", "window": window, "coordinate": row,
                     "export": str(Path(output) / f"window-{window:02d}/collection/export/EPISODES.json"),
                     "reward": None, "available": False, "reason": "planned before service"}
                    for row in study.source_study.candidate_plan(window))
    return rows


def collector_argv(stage, deadline):
    return [str(study.NATIVE), str(study.SOURCE / "terminal_collect.py"), "--spec",
            str(stage / "CAPTURE_SPEC.json"), "--output", str(stage / "rollout"),
            "--deadline", str(float(deadline))]


def trainer_argv(stage, generation, policy, deadline):
    return [str(study.TRAIN), str(study.ROOT / "continuation_train.py"), "--group",
            str(stage / "collection/export/GROUP.json"), "--generation",
            str(stage / "GENERATION.json"), "--checkpoint", str(policy["path"]),
            "--output", str(stage / "training"), "--deadline", str(float(deadline))]


def _stop(process):
    if process.poll() is not None:
        return
    for sig, wait in ((signal.SIGINT, 30), (signal.SIGTERM, 30), (signal.SIGKILL, 30)):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=wait)
            return
        except subprocess.TimeoutExpired:
            pass


def train_window(suite, stage, generation, policy, work_deadline):
    deadline = min(work_deadline, time.time() + 1800)
    argv = trainer_argv(stage, generation, policy, deadline)
    study.write(stage / "TRAIN_COMMAND.json", {"argv": argv, "started_epoch": time.time(),
                "deadline_epoch": deadline, "sparse_head": True})
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
            code = process.wait(timeout=max(.001, deadline - time.time()))
            if code:
                raise RuntimeError("sparse trainer failed")
        except BaseException:
            _stop(process)
            raise
        finally:
            suite.stop_child(process, owner)
            study.write(stage / "TRAIN_EXIT.json", {"returncode": process.returncode,
                        "ended_epoch": time.time(), "released": process.poll() is not None})
    return study.common.c.checkpoint_policy(stage / "training", generation)


def collect_window(suite, service, stage, window, generation, work_deadline):
    collection = stage / "collection"
    collection.mkdir()
    deadline = min(work_deadline, time.time() + 360)
    collect.prepare_spec(f"window-{window}", service / "BINDING.json",
                         service / "service/endpoint-original.json",
                         collection / "CAPTURE_SPEC.json", max(.001, deadline - time.time()),
                         generation)
    command_error = None
    try:
        suite.command(service, f"collect-window-{window}", collector_argv(collection, deadline),
                      max(.001, deadline - time.time()), deadline)
    except Exception as error:
        command_error = {"type": type(error).__name__, "message": str(error)}
    if not (collection / "rollout/SPEC.json").exists():
        study.write(collection / "COLLECTION_FAILURE.json", {"error": command_error,
                    "reason": "collector produced no spec"})
        raise RuntimeError("collector returned no native attempt")
    result = export.export_attempt(collection / "rollout", collection / "export")
    study.write(collection / "COLLECTION_RESULT.json", {"command_error": command_error,
                "manifest_sha256": study.sha(collection / "export/MANIFEST.json")})
    return result


def cost_ledger(output):
    output = Path(output)
    requests = sorted(output.glob("**/rollout/role-audit/*-request.json"))
    results = sorted(output.glob("**/rollout/role-audit/*-result.json"))
    result_rows = [study.read(path) for path in results]
    result_ids = {row.get("request_id") for row in result_rows}
    usage = {key: 0 for key in ("input", "output", "cached")}
    unknown = {key: 0 for key in usage}
    choices = responses = 0
    for row in result_rows:
        wire = row.get("native_wire_response") or {}
        if isinstance(wire.get("http_status"), int):
            responses += 1
        try:
            body = json.loads(wire.get("body")) if isinstance(wire.get("body"), str) else {}
        except json.JSONDecodeError:
            body = {}
        choices += bool(isinstance(wire.get("http_status"), int)
                        and 200 <= wire["http_status"] < 300 and body.get("choices"))
        raw = body.get("usage") or {}
        values = {"input": raw.get("prompt_tokens"), "output": raw.get("completion_tokens"),
                  "cached": (raw.get("prompt_tokens_details") or {}).get("cached_tokens")}
        for key, value in values.items():
            if type(value) is int and value >= 0:
                usage[key] += value
            else:
                unknown[key] += 1
    return {"physical_request_records": len(requests), "response_proven_attempts": len(results),
            "raw_http_responses": responses, "http_2xx_choice_payloads": choices,
            "prepared_attempt_unknown": sum(study.read(path).get("request_id") not in result_ids
                                            for path in requests),
            "usage_known": usage, "usage_unknown_records": unknown,
            "record_sha256": {str(path): study.sha(path) for path in requests + results},
            "billing": "not measured", "missing_usage_not_synthesized": True}


def execute(output):
    output = Path(output)
    if output.resolve() != study.ATTEMPT.resolve():
        raise ValueError("exact attempt-001 only")
    if output.exists():
        raise FileExistsError("attempt retained")
    campaign = study.verify_prepared()
    policy = study.checkpoint2_policy()
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("MAIN assigns exactly one GPU")
    suite = study.source_owner.dependencies()
    started = time.time()
    limits = budget(started)
    output.mkdir(parents=True)
    study.write(output / "PLANNED_NULL_ENDPOINTS.json", planned_inventory(output))
    study.write(output / "OWNER_RUN.json", {"identity": campaign["identity"], "budget": limits,
                "start_policy": policy, "completed_windows_start": 3,
                "planned_windows": [4, 5, 6, 7, 8], "planned_attempts": 120})
    previous = signal.signal(signal.SIGALRM,
                             lambda *_: (_ for _ in ()).throw(TimeoutError("owned deadline")))
    signal.setitimer(signal.ITIMER_REAL, max(.001, limits["owned"] - time.time()))
    state = {"policy": policy, "completed_windows": 3}
    error = None
    active = None
    try:
        for window in range(4, 9):
            if limits["work"] - time.time() < 600:
                raise TimeoutError("insufficient fixed-window allowance")
            stage = output / f"window-{window:02d}"
            stage.mkdir()
            generation = study.common.generation(window, state["policy"])
            study.write(stage / "GENERATION.json", generation)
            service = stage / "service-stage"
            service.mkdir()
            active = service
            try:
                startup = min(limits["work"], time.time() + 180)
                signal.setitimer(signal.ITIMER_REAL, max(.001, startup - time.time()))
                suite.start_service(service, collect.binding_for(state["policy"]), startup)
                signal.setitimer(signal.ITIMER_REAL, max(.001, limits["work"] - time.time()))
                result = collect_window(suite, service, stage, window, generation, limits["work"])
            finally:
                signal.setitimer(signal.ITIMER_REAL,
                                 max(.001, min(limits["owned"], time.time() + 90) - time.time()))
                suite.release_service(service)
                active = None
            if not result["complete"] or result["integrity_failures"]:
                raise RuntimeError("incomplete or integrity-failed fixed window")
            new_policy = None
            if result["training_group_episodes"]:
                signal.setitimer(signal.ITIMER_REAL, max(.001, limits["work"] - time.time()))
                try:
                    new_policy = train_window(suite, stage, generation, state["policy"], limits["work"])
                except BaseException:
                    checkpoint = stage / "training" / f"checkpoint-{generation['round']}" / "state.json"
                    if checkpoint.exists():
                        new_policy = study.common.c.checkpoint_policy(stage / "training", generation)
                        cursor = study.common.transition(state["completed_windows"], state["policy"],
                                                         window, new_policy)
                        state.update(policy=cursor["policy"], completed_windows=window)
                        study.write(stage / "COMMIT_RECOVERED_ON_STOP.json", {**cursor,
                                    "generation": generation, "no_retry": True})
                    raise
            cursor = study.common.transition(state["completed_windows"], state["policy"],
                                              window, new_policy)
            state.update(policy=cursor["policy"], completed_windows=window)
            study.write(stage / "WINDOW_RESULT.json", {**cursor, "generation": generation,
                        "export_manifest_sha256": study.sha(stage / "collection/export/MANIFEST.json"),
                        "ended_epoch": time.time()})
    except BaseException as caught:
        error = {"type": type(caught).__name__, "message": str(caught),
                 "traceback": traceback.format_exc()}
        study.write(output / "TRAINING_STOP.json", error)
    finally:
        if active is not None:
            try:
                signal.setitimer(signal.ITIMER_REAL,
                                 max(.001, min(limits["owned"], time.time() + 90) - time.time()))
                suite.release_service(active)
                active = None
            except BaseException as caught:
                if error is None:
                    error = {"type": type(caught).__name__, "message": str(caught),
                             "release_failed": True}
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    terminal = {"complete": error is None and state["completed_windows"] == 8,
                "error": error, "policy": state["policy"],
                "completed_windows": state["completed_windows"],
                "actual_optimizer_step": state["policy"]["step"],
                "released": active is None, "elapsed_seconds": time.time() - started}
    study.write(output / "COST_LEDGER.json", cost_ledger(output))
    study.write(output / "OWNER_TERMINAL.json", terminal)
    return terminal


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    value = study.verify_prepared() if args.command == "verify" else execute(args.output)
    print(json.dumps(value, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if args.command == "verify" or value["complete"] else 1)
