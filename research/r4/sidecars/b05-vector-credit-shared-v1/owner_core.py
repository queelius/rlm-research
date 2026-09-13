"""Finite subprocess owner shared by the two fixed credit assignments."""

import os
import signal
import subprocess
import time
import traceback


def run(study):
    ready = study.verify(); assert os.environ.get("CUDA_VISIBLE_DEVICES"), "MAIN must assign the leased GPU"
    assert not study.OUTPUT.exists(); study.OUTPUT.mkdir(parents=True)
    command = [str(study.PYTHON), str(study.ROOT / "train.py"), "--output", str(study.OUTPUT),
               "--seconds", str(study.SCIENCE_SECONDS)]
    study.write_x(study.OUTPUT / "OWNER_START.json", {"command": command,
        "ready_identity": ready["identity"], "ready_sha256": study.sha(study.READY),
        "owner_pid": os.getpid(), "owner_cap_seconds": study.OWNER_SECONDS,
        "external_cap_required_seconds": study.EXTERNAL_SECONDS})
    started = time.monotonic(); process = None; error = None; code = None
    def stop(signum, _frame): raise RuntimeError(f"Owner received signal {signum}")
    old = {sig: signal.signal(sig, stop) for sig in (signal.SIGTERM, signal.SIGINT)}
    try:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TOKENIZERS_PARALLELISM="false")
        with (study.OUTPUT / "train.stdout").open("x") as stdout, (study.OUTPUT / "train.stderr").open("x") as stderr:
            process = subprocess.Popen(command, env=env, cwd=study.ROOT, stdout=stdout, stderr=stderr,
                                       start_new_session=True)
            code = process.wait(timeout=study.OWNER_SECONDS)
    except BaseException as caught:
        error = {"type": type(caught).__name__, "message": str(caught), "traceback": traceback.format_exc()}
    finally:
        for sig, handler in old.items(): signal.signal(sig, handler)
        if process is not None and process.poll() is None:
            try: os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=10)
        result = study.read(study.OUTPUT / "RESULT.json") if (study.OUTPUT / "RESULT.json").exists() else None
        complete = code == 0 and result is not None and result["status"] == "UPDATED"
        study.write_x(study.OUTPUT / "OWNER_TERMINAL.json", {"complete": complete,
            "owned_process_reaped": process is not None and process.poll() is not None,
            "subprocess_exit_code": None if process is None else process.returncode,
            "elapsed_seconds": time.monotonic() - started, "error": error,
            "result_sha256": study.sha(study.OUTPUT / "RESULT.json") if result else None,
            "ready_sha256": study.sha(study.READY), "ready_identity": ready["identity"]})
    return 0 if complete else 1
