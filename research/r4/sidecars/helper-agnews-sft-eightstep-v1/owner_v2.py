"""V2 owner binding the unchanged trainer to corrected diagnostic spans."""

import argparse
import json
import signal
import time
import traceback

import sft_study_v2 as study
import train_sft_v2 as train_sft


def execute(outer_seconds):
    if outer_seconds != study.CAP or study.ATTEMPT.exists():
        raise ValueError("exact900 cap and unused attempt required")
    started = time.monotonic()

    def timeout(_signum, _frame):
        raise TimeoutError("bounded AG SFT owner deadline")

    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, outer_seconds)
    errors, result = [], None
    try:
        result = train_sft.run()
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
        if study.ATTEMPT.exists() and not (study.ATTEMPT / "FAILURE.json").exists():
            study.write_x(study.ATTEMPT / "FAILURE.json", errors[0])
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    terminal = {
        "schema": "agnews-eightstep-answer-only-sft-owner-terminal-v2",
        "complete": bool(result and result.get("status") == "UPDATED_STEP8" and not errors),
        "errors": errors,
        "elapsed_seconds": time.monotonic() - started,
        "result_sha256": study.sha(study.ATTEMPT / "RESULT.json") if (study.ATTEMPT / "RESULT.json").exists() else None,
        "optimizer_steps": result.get("optimizer_steps") if result else None,
        "no_native_service_or_child_calls": True,
        "gpu_release_occurs_at_owner_process_exit": True,
    }
    if study.ATTEMPT.exists():
        study.write_x(study.ATTEMPT / "OWNER_TERMINAL.json", terminal)
    print(json.dumps(terminal, sort_keys=True), flush=True)
    return terminal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        terminal = execute(args.outer_seconds)
        raise SystemExit(0 if terminal["complete"] else 1)


if __name__ == "__main__":
    main()
