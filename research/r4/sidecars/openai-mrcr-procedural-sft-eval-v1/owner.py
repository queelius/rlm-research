"""One bounded owned service for a fixed procedural-SFT readout stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import time
import traceback

import checkpoint
import study


STAGES = {
    "train": {"phase": "train", "arm": "checkpoint4", "output": study.ROOT / "outputs/train-readout-001"},
    "held-base": {"phase": "held", "arm": "base", "output": study.ROOT / "outputs/held-base-001"},
    "held-checkpoint4": {"phase": "held", "arm": "checkpoint4", "output": study.ROOT / "outputs/held-checkpoint4-001"},
}


def held_gate() -> dict:
    attempt = STAGES["train"]["output"]
    terminal_path = attempt / "OWNER_TERMINAL.json"
    result_path = attempt / "science/RESULT.json"
    if not terminal_path.exists() or not result_path.exists():
        return {"eligible": False, "reason": "train readout is absent"}
    terminal, result = study.read(terminal_path), study.read(result_path)
    gate = result.get("manipulation_gate") or {}
    eligible = bool(
        terminal.get("complete") is True
        and terminal.get("released") is True
        and not terminal.get("errors")
        and result.get("complete") is True
        and gate.get("eligible") is True
        and gate.get("raw_exact", 0) >= 8
        and gate.get("exact_contexts", 0) >= 4
    )
    return {
        "eligible": eligible,
        "reason": None if eligible else "fixed train-only manipulation criterion failed",
        "train_terminal_sha256": study.sha(terminal_path),
        "train_result_sha256": study.sha(result_path),
        "gate": gate,
    }


def verify(stage: str) -> dict:
    if stage not in STAGES:
        raise ValueError("unknown fixed stage")
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("evaluation READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("evaluation source/input changed: " + raw)
    checkpoint.verify_checkpoint()
    if stage != "train" and not held_gate()["eligible"]:
        raise ValueError("heldout remains closed: " + str(held_gate()))
    return ready


def preflight(service: Path, binding: dict) -> None:
    import httpx

    endpoint = study.read(service / "endpoint-original.json")
    if endpoint.get("role_binding_sha256") != study.sha(service.parent / "BINDING.json"):
        raise ValueError("live descriptor role binding changed")
    key = os.environ[endpoint["api_key_env"]]
    with httpx.Client(
        headers={"Authorization": "Bearer " + key}, trust_env=False, timeout=30
    ) as client:
        version = client.get(f"http://{endpoint['host']}:{endpoint['port']}/version")
        models = client.get(f"http://{endpoint['host']}:{endpoint['port']}/v1/models")
        version.raise_for_status()
        models.raise_for_status()
    cards = {row["id"]: row for row in models.json()["data"]}
    for alias, model in binding["models"].items():
        if (
            cards.get(alias, {}).get("root") != model["path"]
            or cards[alias].get("parent") != str(study.BASE)
        ):
            raise ValueError("live model alias/path/base differs")
    study.write_x(
        service.parent / "PREFLIGHT.json",
        {"version": version.json(), "models": models.json(), "binding_sha256": study.digest(binding)},
    )


def execute(stage: str, output: Path, outer_seconds: int) -> dict:
    spec = STAGES[stage]
    expected = spec["output"]
    if output.resolve() != expected.resolve() or output.exists():
        raise ValueError("exact unused fixed stage output required")
    if outer_seconds != study.OWNER_SECONDS:
        raise ValueError("exact 900-second owner cap required")
    ready = verify(stage)
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN must assign one exclusive GPU and private credential")
    started = time.time()
    deadline = started + outer_seconds
    work = deadline - 60
    output.mkdir(parents=True)
    service = output / "owned-service"
    service.mkdir()
    binding = checkpoint.binding(spec["arm"])
    study.write_x(
        output / "OWNER_RUN.json",
        {
            "stage": stage,
            "phase": spec["phase"],
            "arm": spec["arm"],
            "started_epoch": started,
            "owner_seconds": outer_seconds,
            "science_seconds": study.SCIENCE_SECONDS,
            "planned": len(study.schedule(spec["phase"])),
            "ready_identity": ready["identity"],
            "checkpoint_receipt_sha256": study.sha(checkpoint.RECEIPT),
            "held_gate": held_gate() if stage != "train" else "not consulted",
            "optimizer_steps": 0,
        },
    )
    errors, suite, released = [], None, False

    def stop(*_):
        raise TimeoutError("evaluation owner signal")

    handlers = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, outer_seconds - 15)
    try:
        suite = study.dependencies()
        suite.preflight = preflight
        suite.start_service(service, binding, min(started + 240, work))
        endpoint = service / "service/endpoint-original.json"
        science_deadline = min(work, time.time() + study.SCIENCE_SECONDS)
        argv = [
            str(study.NATIVE),
            str(study.ROOT / "collect.py"),
            "--phase",
            spec["phase"],
            "--arm",
            spec["arm"],
            "--endpoint",
            str(endpoint),
            "--output",
            str(output / "science"),
            "--deadline",
            str(science_deadline),
        ]
        suite.command(
            service,
            "procedural-sft-" + stage,
            argv,
            min(study.SCIENCE_SECONDS, max(1, science_deadline - time.time())),
            science_deadline,
        )
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL, max(1, deadline - time.time()))
        if suite is not None:
            try:
                suite.release_service(service)
                released = True
            except BaseException as error:
                errors.append({"stage": "release", "type": type(error).__name__, "message": str(error)})
        else:
            released = True
        result_path = output / "science/RESULT.json"
        result = study.read(result_path) if result_path.exists() else None
        complete = bool(
            not errors
            and released
            and result
            and result.get("complete") is True
            and result.get("all_causal_mappings_complete") is True
            and result.get("all_initial_root_prefixes_verified") is True
            and result.get("all_action_caps_respected") is True
        )
        terminal = {
            "complete": complete,
            "stage": stage,
            "released": released,
            "errors": errors or None,
            "result": str(result_path) if result else None,
            "recorded": result.get("recorded") if result else None,
            "scientifically_available": result.get("scientifically_available") if result else None,
            "manipulation_gate": result.get("manipulation_gate") if result else None,
            "elapsed_seconds": time.time() - started,
            "optimizer_steps": 0,
            "no_retry": True,
        }
        temporary = output / "OWNER_TERMINAL.tmp"
        temporary.write_text(json.dumps(terminal, indent=2, sort_keys=True) + "\n")
        temporary.replace(output / "OWNER_TERMINAL.json")
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--stage", choices=tuple(STAGES), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(verify(args.stage)["identity"])
    else:
        output = args.output or STAGES[args.stage]["output"]
        value = execute(args.stage, output, args.outer_seconds)
        print(json.dumps(value, sort_keys=True))
        raise SystemExit(0 if value["complete"] else 1)
