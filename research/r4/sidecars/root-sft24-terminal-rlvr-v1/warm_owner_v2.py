"""Additive V2 owner: real replay entry and collection-scoped alarms."""
import argparse
from pathlib import Path
import time

import warm_collect_v2 as collect
import warm_export_v2 as export
import warm_owner as v1
import warm_study as study
import warm_verify_v2 as verification

verification.install()

ATTEMPT_V2 = study.ROOT / "outputs/attempt-002"


def check_output(output):
    output = Path(output)
    if output.resolve() != ATTEMPT_V2.resolve():
        raise ValueError("exact additive attempt-002 namespace only")
    if output.exists():
        raise FileExistsError("attempt-002 retained; no implicit retry or overwrite")


def collector_argv(stage, deadline):
    return [str(study.NATIVE), str(study.ROOT / "warm_collect_v2.py"), "--spec",
            str(stage / "CAPTURE_SPEC.json"), "--output", str(stage / "rollout"),
            "--deadline", str(float(deadline))]


def trainer_argv(stage, deadline):
    return [str(study.TRAIN), str(study.ROOT / "warm_train_v2.py"), "--group",
            str(stage / "collection/export/GROUP.json"), "--generation",
            str(stage / "GENERATION.json"), "--output", str(stage / "training"),
            "--deadline", str(float(deadline))]


def collection_stage(suite, service, stage, phase, deadline, generation=None, cap=600):
    stage.mkdir(parents=True, exist_ok=False)
    end = time.time() + v1.remaining(deadline, cap)
    collect.prepare_spec(phase, service / "BINDING.json", service / "service/endpoint-original.json",
                         stage / "CAPTURE_SPEC.json", v1.remaining(end, cap), generation)
    error = None
    try:
        v1.alarm(end)
        suite.command(service, "collect-" + phase, collector_argv(stage, end),
                      v1.remaining(end, cap), end)
    except Exception as caught:
        error = {"type": type(caught).__name__, "message": str(caught)}
    if not (stage / "rollout/SPEC.json").exists():
        study.write(stage / "COLLECTION_FAILURE.json",
                    {"error": error, "reason": "collector produced no spec"})
        raise RuntimeError("collector returned no native attempt")
    v1.alarm(end)
    result = export.export_attempt(stage / "rollout", stage / "export")
    study.write(stage / "COLLECTION_RESULT.json", {
        "command_error": error,
        "manifest_sha256": study.sha(stage / "export/MANIFEST.json"),
        "collection_alarm_deadline_epoch": end,
    })
    return result


def execute(output):
    verify()
    v1.export = export
    v1.collect = collect
    v1.collection_stage = collection_stage
    v1.check_output = check_output
    v1.collector_argv = collector_argv
    v1.trainer_argv = trainer_argv
    return v1.execute(output)


def verify():
    campaign = verification.verify()
    ready = study.read(study.ROOT / "READY_v2.json")
    if study.digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("V2 READY identity changed")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        study.check(path, pin)
    if ready["qualification_sha256"] != study.sha(study.ROOT / "V2_QUALIFICATION.json"):
        raise ValueError("READY does not bind V2 qualification")
    return campaign


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ATTEMPT_V2)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(verify()["campaign_id"])
    else:
        result = execute(args.output)
        print({"complete": result["complete"], "step": result["selection"]["actual_optimizer_step"],
               "elapsed_seconds": result["elapsed_seconds"]})
        raise SystemExit(0 if result["complete"] else 1)
