"""Exercise actual suite start/claim/release using the repaired claim function."""

import os
import time

import owner_v3
import study_v3 as study


def test_actual_start_claim_release_accepts_custom_service_and_exact_engine(tmp_path, monkeypatch):
    suite = study.source().base_owner().study.dependencies()
    owner_v3.configure_suite(suite)
    directory = tmp_path / "attempt/service"
    directory.mkdir(parents=True)
    service = directory / "service"
    service.mkdir()
    binding = {"fixture": "binding"}
    started = time.time()
    parent = {"pid": 910001, "pgid": 910001, "uid": os.getuid(), "start_ticks": 101,
              "started_epoch": started, "argv": [str(study.NATIVE), str(study.SERVICE)]}
    engine = {"pid": 910002, "pgid": 910002, "uid": os.getuid(), "start_ticks": 102,
              "started_epoch": started, "argv": ["PRL::Inference"]}
    active = {parent["pid"]: parent, engine["pid"]: engine}
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_FIXTURE")
    monkeypatch.setattr(suite.life, "observe", lambda pid: active.get(pid))
    monkeypatch.setattr(suite.life, "snapshot_descendants", lambda *_args: None)
    monkeypatch.setattr(suite.life, "live_owned", lambda rows: [x for x in rows if x["pid"] in active])
    monkeypatch.setattr(suite.life.v1, "ports_free", lambda: True)
    monkeypatch.setattr(suite, "preflight", lambda *_args: None)
    monkeypatch.setattr(suite.life.os, "killpg", lambda pgid, _sig: active.pop(pgid))

    class Launcher:
        pid, returncode = parent["pid"], 0

        def __init__(self, command, **_kwargs):
            assert command == [str(study.NATIVE), str(study.SERVICE), "--binding",
                               str(directory / "BINDING.json"), "--run-dir", str(service)]
            study.write_x(service / "BINDING.json", binding)
            study.write_x(service / "SERVER_START.json", {
                "command": [str(study.NATIVE), str(study.MUSIQUE / "engine_entry_v2.py"), "@",
                            str(service / "inference.json")],
                "gpu": "CPU_FIXTURE", "launcher_sha256": study.sha(study.SERVICE),
                "pid": engine["pid"], "started": started})
            study.write_x(service / "inference.json", {"fixture": True})
            (service / "inference.log").touch()
            study.write_x(service / "SERVER_READY.json", {"fixture": True})

        def poll(self):
            return 0

    monkeypatch.setattr(suite.subprocess, "Popen", Launcher)
    suite.start_service(directory, binding, time.time() + 20)
    receipt = study.read(directory / "SERVICE_OWNER_V2.json")
    assert receipt["process"]["pid"] == engine["pid"]
    assert receipt["command"][1] == str(study.MUSIQUE / "engine_entry_v2.py")
    suite.release_service(directory)
    assert study.read(directory / "SERVICE_STOPPED.json")["all_owned_process_identities_exited"]


def test_owner_and_collector_use_attempt003_namespace():
    assert owner_v3.source.study is study
    assert owner_v3.source.collect is owner_v3.collect
    assert owner_v3.collect.source.study is study
    assert study.ATTEMPT.name == "attempt-003"
