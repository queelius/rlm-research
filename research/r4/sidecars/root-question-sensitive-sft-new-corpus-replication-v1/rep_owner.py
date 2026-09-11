"""4500s capture, six-update training, and metadata72 readout owner."""
import argparse
import os
from pathlib import Path
import signal
import time
import traceback
import rep_study as s
import rep_binding as b
import qs_owner as qualified

BUDGET = {"outer": 4500, "owned": 4470, "work": 4320, "capture": 1500,
          "training": 1200, "readout": 1500, "finalize": 120, "cleanup": 150, "margin": 30}


def inventory(output):
    return [{"policy": "new_corpus_sft6", "coordinate": row,
             "path": str(Path(output) / "new_corpus_sft6/free" / row["id"] / "RESULT.json"),
             "recorded": False, "available": False, "reward": None,
             "cause": "not_started_no_artifacts"}
            for row in s.read(s.METADATA / "inputs/FREE_PLAN.json")]


def remaining(deadline):
    value = deadline - time.time()
    if value <= 0: raise TimeoutError("replication shared/stage cap")
    return value


def alarm(deadline): signal.setitimer(signal.ITIMER_REAL, max(.001, deadline - time.time()))
def error(caught): return {"type": type(caught).__name__, "message": str(caught), "traceback": traceback.format_exc()}


def cost_ledger(output):
    paths = sorted((output / "capture").glob("*/physical/*.json")) + sorted((output / "new_corpus_sft6/free").glob("*/physical/*.json"))
    def tally(selected):
        rows = [s.read(p) for p in selected]; actual = [r for r in rows if r.get("physical_request_attempt")]
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "unknown_records": 0}
        for row in actual:
            value = row.get("response", {}).get("usage") if isinstance(row.get("response"), dict) else None
            if not isinstance(value, dict): usage["unknown_records"] += 1
            else:
                for key in ("prompt_tokens", "completion_tokens"):
                    if key in value: usage[key] += int(value[key])
                    else: usage["unknown_records"] += 1
        return {"transport_records": len(rows), "physical_requests_attempted": len(actual),
                "choice_bearing_responses": sum(bool(r.get("response", {}).get("choices")) for r in actual if isinstance(r.get("response"), dict)),
                "usage": usage, "files_sha256": {str(p): s.sha(p) for p in selected}}
    capture = [p for p in paths if "/capture/" in str(p)]
    readout = [p for p in paths if p not in capture]
    return {"capture": tally(capture), "metadata_readout": tally(readout),
            "baseline_and_original_qs6_reused_not_rerun": True, "billing": "unknown/not measured"}


def harvest(rows):
    for row in rows:
        path = Path(row["path"]); directory = path.parent
        if path.exists():
            value = s.read(path); row.update(recorded=True, available=value["available"], reward=value["reward"],
                                             result_sha256=s.sha(path), cause="native_final" if value["available"] else "observed_invalid")
        elif (directory / "FAILURE.json").exists() or list((directory / "physical").glob("*.json")):
            row["cause"] = "attempted_unavailable_no_result"
        elif directory.exists(): row["cause"] = "started_no_physical_receipt"
    return rows


def execute(output):
    output = Path(output); started = time.time(); work = started + BUDGET["work"]; owned = started + BUDGET["owned"]
    if output.resolve() != s.ATTEMPT.resolve() or output.exists(): raise ValueError("exact unused attempt")
    ready = s.verify(); s.runtime()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one MAIN GPU/private credential preflight")
    output.mkdir(parents=True); rows = inventory(output); s.write(output / "PLANNED_EVALUATION.json", rows)
    s.write(output / "OWNER_RUN.json", {"identity": ready["identity"], "started_epoch": started,
        "budget": BUDGET, "planned_capture": 72, "planned_readout": 72, "updates": 6,
        "fixed24_start": True, "fresh_optimizer": True, "baseline_reused_not_rerun": True,
        "original_qs6_reused_not_rerun": True, "no_retry_or_replacement": True})
    suite = qualified.dependencies(); active = None; errors = []; stages = []
    handlers = {}
    class MainTermination(BaseException): pass
    def expired(sig, frame):
        if sig in (signal.SIGINT, signal.SIGTERM): raise MainTermination("MAIN termination")
        raise TimeoutError("replication cap")
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM): handlers[sig] = signal.signal(sig, expired)
    def service(name, binding, end, body):
        nonlocal active
        stage = output / name; stage.mkdir(); active = stage; status = {"stage": name, "started_epoch": time.time(), "deadline_epoch": end}
        try:
            startup = min(time.time() + 180, end - 90); alarm(startup); suite.start_service(stage, binding, startup)
            deadline = end - 90; alarm(deadline); body(stage, deadline); status["work_complete"] = True
        except BaseException as caught:
            status["error"] = error(caught); errors.append({"stage": name, **status["error"]})
        finally:
            alarm(min(owned, end, time.time() + BUDGET["cleanup"]))
            try: suite.release_service(stage); active = None
            except BaseException as caught:
                status["release_error"] = error(caught); errors.append({"stage": name, **status["release_error"]})
            status["ended_epoch"] = time.time(); s.write(stage / "PHASE_TERMINAL.json", status); stages.append(status); alarm(owned)
        return status.get("work_complete", False) and active is None
    try:
        capture_end = min(time.time() + BUDGET["capture"], work - 2820)
        def capture(stage, deadline):
            argv = [str(s.NATIVE), str(s.ROOT / "rep_collect.py"), "--mode", "capture", "--plan", "TRAIN_PLAN.json",
                    "--start", "0", "--stop", "72", "--binding", str(stage / "BINDING.json"),
                    "--endpoint", str(stage / "service/endpoint-original.json"), "--output", str(output / "capture"),
                    "--deadline", str(float(deadline))]
            suite.command(stage, "capture72", argv, remaining(deadline), deadline); s.corpus()
        if service("teacher-service", b.binding("unchanged"), capture_end, capture):
            train_end = min(time.time() + BUDGET["training"], work - 1620)
            stage = output / "training-stage"; stage.mkdir(); status = {"stage": "training", "started_epoch": time.time(), "deadline_epoch": train_end}
            try:
                alarm(train_end); argv = [str(s.TRAIN), str(s.ROOT / "rep_train.py"), "--mode", "train", "--output", str(output / "training"), "--deadline", str(float(train_end))]
                suite.command(stage, "six-full72-updates", argv, remaining(train_end), train_end); b.selected("new_corpus_sft6"); status["work_complete"] = True
            except BaseException as caught:
                status["error"] = error(caught); errors.append({"stage": "training", **status["error"]})
            finally:
                status["ended_epoch"] = time.time(); s.write(stage / "PHASE_TERMINAL.json", status); stages.append(status); alarm(owned)
            if status.get("work_complete"):
                read_end = min(time.time() + BUDGET["readout"], work - BUDGET["finalize"])
                def readout(stage, deadline):
                    argv = [str(s.NATIVE), str(s.ROOT / "rep_readout.py"), "--mode", "free", "--plan", "FREE_PLAN.json",
                            "--start", "0", "--stop", "72", "--binding", str(stage / "BINDING.json"),
                            "--endpoint", str(stage / "service/endpoint-original.json"),
                            "--output", str(output / "new_corpus_sft6/free"), "--deadline", str(float(deadline))]
                    suite.command(stage, "metadata72", argv, remaining(deadline), deadline)
                service("readout-service", b.binding("new_corpus_sft6"), read_end, readout)
    finally:
        alarm(min(owned, time.time() + BUDGET["finalize"])); rows = harvest(rows)
        s.write(output / "COST_LEDGER.json", cost_ledger(output))
        result = {"identity": ready["identity"], "complete": not errors and all(r["recorded"] for r in rows),
                  "error": errors or None, "capture_complete": (output / "capture/CORPUS_READY.json").exists(),
                  "readout_inventory": rows, "planned_capture": 72, "planned_readout": 72,
                  "stages": stages, "released": active is None, "active_unreleased_service": str(active) if active else None,
                  "elapsed_seconds": time.time() - started, "no_retry": True}
        s.write(output / "OWNER_TERMINAL.json", result); signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items(): signal.signal(sig, handler)
    return result


def parse_args():
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run")); parser.add_argument("--output", type=Path, default=s.ATTEMPT); return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify": print(s.verify()["identity"])
    else:
        result = execute(args.output); print({"complete": result["complete"], "error": result["error"]}); raise SystemExit(0 if result["complete"] else 1)
