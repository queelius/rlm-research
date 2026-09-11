import importlib
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "root-question-sensitive-sft-new-corpus-replication-v1"
sys.path.insert(0, str(ROOT))


def test_source_failure_is_cuda_hiding_launcher():
    text = (SOURCE / "outputs/attempt-001/training-stage/six-full72-updates.log").read_text()
    command = __import__("json").loads(
        (SOURCE / "outputs/attempt-001/training-stage/six-full72-updates-COMMAND.json").read_text()
    )
    assert "MAIN must assign exactly one GPU" in text
    assert command["gpu_visible_to_command"] is False
    assert not (SOURCE / "outputs/attempt-001/training/RESULT.json").exists()


def test_recovery_reuses_exact_complete_corpus_and_new_training_path():
    recovery = importlib.import_module("recovery")
    receipt = recovery.source_corpus_receipt()
    assert receipt["examples"] == 72
    assert receipt["source_attempt"] == str(SOURCE / "outputs/attempt-001")
    assert receipt["capture_rerun"] is False
    binding = recovery.binding_module()
    assert str(binding.RECOVERY_TRAINING).startswith(str(ROOT))
    assert binding.RECOVERY_TRAINING != SOURCE / "outputs/attempt-001/training"


def test_gpu_command_preserves_assigned_device(tmp_path, monkeypatch):
    recovery = importlib.import_module("recovery")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "7")
    seen = {}

    class Process:
        pid = 123
        returncode = 0
        def wait(self, timeout):
            seen["timeout"] = timeout
            return 0

    def popen(argv, **kwargs):
        seen.update(argv=argv, env=kwargs["env"])
        return Process()

    class Life:
        def observe(self, pid): return {"pid": pid}
        def safe_observation(self, value): return value
    class Suite:
        life = Life()
        def stop_child(self, process, owner): seen["stopped"] = True

    monkeypatch.setattr(recovery.subprocess, "Popen", popen)
    recovery.gpu_command(Suite(), tmp_path / "stage", ["python", "train.py"], recovery.time.time() + 10)
    assert seen["env"]["CUDA_VISIBLE_DEVICES"] == "7"
    assert seen["stopped"] is True


def test_budget_is_no_capture_and_bounded():
    recovery = importlib.import_module("recovery")
    assert recovery.BUDGET == {
        "outer": 3000, "owned": 2970, "work": 2850,
        "training": 1200, "readout": 1500,
        "finalize": 150, "cleanup": 120, "margin": 30,
    }


def test_owner_uses_gpu_training_then_exact_metadata72(monkeypatch, tmp_path):
    owner = importlib.import_module("owner")
    calls = []
    monkeypatch.setattr(owner.r, "verify", lambda: {"identity": "test"})
    monkeypatch.setattr(owner.r, "source_corpus_receipt", lambda: {
        "examples": 72, "source_attempt": str(SOURCE / "outputs/attempt-001"),
        "corpus_ready_sha256": "0" * 64, "capture_rerun": False})
    monkeypatch.setattr(owner.r, "selected", lambda: {"adapter_sha256": "a" * 64})
    monkeypatch.setattr(owner.r, "binding_module", lambda: type("B", (), {
        "binding": staticmethod(lambda arm: {"arm": arm})})())
    monkeypatch.setattr(owner.r, "gpu_command", lambda suite, stage, argv, deadline: calls.append(("train", argv)))
    monkeypatch.setattr(owner, "alarm", lambda deadline: None)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "0")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "fixture")

    class Suite:
        def start_service(self, stage, binding, deadline): calls.append(("start", binding))
        def command(self, stage, label, argv, cap, deadline): calls.append(("collect", argv))
        def release_service(self, stage): calls.append(("release", str(stage)))
    monkeypatch.setattr(owner.r, "dependencies", lambda: Suite())
    output = tmp_path / "attempt"
    result = owner.execute(output, now=lambda: 1000.0)
    assert result["training_complete"] is True
    assert calls[0][0] == "train"
    assert calls[1] == ("start", {"arm": "new_corpus_sft6"})
    assert calls[2][0] == "collect" and calls[2][1][calls[2][1].index("--stop") + 1] == "72"
    assert calls[3][0] == "release"
