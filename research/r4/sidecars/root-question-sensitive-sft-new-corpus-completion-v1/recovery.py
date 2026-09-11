"""Additive train/readout completion over the immutable new-corpus capture."""
import functools
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "root-question-sensitive-sft-new-corpus-replication-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
SOURCE_ATTEMPT = SOURCE / "outputs/attempt-001"

_spec = importlib.util.spec_from_file_location("new_corpus_completion_source_study", SOURCE / "rep_study.py")
s = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = s
sys.path.insert(0, str(SOURCE))
_spec.loader.exec_module(s)

BUDGET = {"outer": 3000, "owned": 2970, "work": 2850,
          "training": 1200, "readout": 1500,
          "finalize": 150, "cleanup": 120, "margin": 30}


def verify():
    ready = s.read(ROOT / "READY.json")
    if s.digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("recovery READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if s.sha(path) != pin:
            raise ValueError("recovery closure changed: " + path)
    source_corpus_receipt()
    return ready


def source_corpus_receipt():
    ready = s.read(SOURCE_ATTEMPT / "capture/CORPUS_READY.json")
    if ready["examples"] != 72 or ready["identity"] != s.verify()["identity"]:
        raise ValueError("immutable complete72 source corpus required")
    s.corpus()
    return {"examples": 72, "source_attempt": str(SOURCE_ATTEMPT),
            "corpus_ready_sha256": s.sha(SOURCE_ATTEMPT / "capture/CORPUS_READY.json"),
            "capture_rerun": False}


@functools.lru_cache(maxsize=1)
def binding_module():
    path = SOURCE / "rep_binding.py"
    ready = s.read(SOURCE / "READY.json")
    if s.sha(path) != ready["source_sha256"][str(path)]:
        raise ValueError("source binding changed")
    source = path.read_text()
    before = 'directory = s.ATTEMPT / "training"'
    if source.count(before) != 1:
        raise ValueError("exact training-directory adaptation")
    module = types.ModuleType("new_corpus_completion_binding")
    module.__file__ = str(path)
    module.RECOVERY_TRAINING = ATTEMPT / "training"
    sys.modules[module.__name__] = module
    with s.aliases({"rep_study": s}):
        exec(compile(source.replace(before, "directory = RECOVERY_TRAINING"),
                     str(path) + "::recovery-training-only", "exec"), module.__dict__)
    return module


def selected():
    return binding_module().selected("new_corpus_sft6")


@functools.lru_cache(maxsize=1)
def readout_study():
    path = SOURCE / "rep_readout_study.py"
    ready = s.read(SOURCE / "READY.json")
    module = s.load("new_corpus_completion_readout_study", path,
                    ready["source_sha256"][str(path)],
                    {"rep_study": s, "rep_binding": binding_module()})
    module.ATTEMPT = ATTEMPT
    return module


@functools.lru_cache(maxsize=1)
def dependencies():
    ready = s.read(SOURCE / "READY.json")
    path = SOURCE / "rep_owner.py"
    owner = s.load("new_corpus_completion_source_owner", path,
                   ready["source_sha256"][str(path)],
                   {"rep_study": s, "rep_binding": binding_module()})
    return owner.qualified.dependencies()


def remaining(deadline):
    value = deadline - time.time()
    if value <= 0:
        raise TimeoutError("completion stage/shared cap")
    return value


def gpu_command(suite, stage, argv, deadline):
    """Run training with MAIN's assigned GPU visible; no inherited CPU-only launcher."""
    stage.mkdir()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu:
        raise ValueError("MAIN assigns exactly one GPU")
    cap = remaining(deadline)
    s.write(stage / "COMMAND.json", {"argv": argv, "deadline_epoch": deadline,
            "cap_seconds": cap, "started_epoch": time.time(), "gpu": gpu,
            "gpu_visible_to_command": True})
    with (stage / "process.log").open("x") as log:
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        observed = suite.life.observe(process.pid)
        if observed is None:
            process.wait(timeout=5)
            raise RuntimeError("training exited before owner observation")
        owner = suite.life.safe_observation(observed)
        s.write(stage / "PROCESS.json", owner)
        try:
            if process.wait(timeout=cap):
                raise RuntimeError("training nonzero; no partial checkpoint selection")
        finally:
            suite.stop_child(process, owner)
            s.write(stage / "EXIT.json", {"returncode": process.returncode,
                    "ended_epoch": time.time()})


def training_argv(output, deadline):
    return [str(s.TRAIN), str(SOURCE / "rep_train.py"), "--mode", "train",
            "--output", str(Path(output) / "training"), "--deadline", str(float(deadline))]


def collector_argv(stage, output, deadline):
    return [str(s.NATIVE), str(ROOT / "collect.py"), "--mode", "free",
            "--plan", "FREE_PLAN.json", "--start", "0", "--stop", "72",
            "--binding", str(stage / "BINDING.json"), "--endpoint",
            str(stage / "service/endpoint-original.json"), "--output", str(output),
            "--deadline", str(float(deadline))]
