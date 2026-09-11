import os
from pathlib import Path

import pytest

import campaign_lifecycle_v2 as v2


def observation(argv):
    return {"pid": 1234, "uid": os.getuid(), "pgid": 1234, "start_ticks": 100,
            "started_epoch": 999.9, "argv": argv}


def test_known_prime_title_change_keeps_exact_process_identity():
    command = ["/qualified/bin/inference", "@", "/owned/service/inference.json"]
    before = observation(["/qualified/bin/python", *command])
    after = observation(["PRL::Inference"])
    start = {"pid": 1234, "started": 1000.0}
    assert v2.validate_start_observation(before, start, command)
    assert v2.validate_start_observation(after, start, command)
    assert v2.same_process(before, after)
    assert not v2.same_process(before, {**after, "start_ticks": 101})
    with pytest.raises(ValueError, match="title|command"):
        v2.validate_start_observation(observation(["unrelated-worker"]), start, command)


def test_initial_claim_rejects_wrong_uid_group_or_start_time():
    good = observation(["PRL::Inference"])
    start = {"pid": 1234, "started": 1000.0}
    for changed in ({**good, "uid": good["uid"] + 1}, {**good, "pgid": 3333},
                    {**good, "started_epoch": 900.0}):
        with pytest.raises(ValueError):
            v2.validate_start_observation(changed, start, ["/inference", "@", "/owned/config"])


def test_parent_exit_does_not_hide_still_running_owned_worker():
    parent = observation(["PRL::Inference"])
    child = {**observation(["VLLM::EngineCore"]), "pid": 1235, "pgid": 1234, "start_ticks": 110}
    current = {1234: None, 1235: {**child, "argv": ["renamed-owned-worker"]}}
    assert v2.live_owned([parent, child], current.get) == [child]
    current[1235] = None
    assert v2.live_owned([parent, child], current.get) == []
    current[1235] = {**child, "start_ticks": 111}
    with pytest.raises(ValueError, match="identity"):
        v2.live_owned([parent, child], current.get)


def test_stop_waits_for_owned_worker_even_when_parent_and_ports_are_gone(tmp_path, monkeypatch):
    parent = v2.safe_observation(observation(["PRL::Inference"]))
    child = {**parent, "pid": 1235, "start_ticks": 110}
    current = {1234: None, 1235: child}
    amendment = tmp_path / "amendment.json"
    v2.c.write_once(amendment, {"CPU_fixture": True})
    monkeypatch.setattr(v2, "AMENDMENT", amendment)
    monkeypatch.setattr(v2, "claim_service", lambda path: {"process": parent})
    monkeypatch.setattr(v2, "owned_records", lambda service, owner: [parent, child])
    original_live = v2.live_owned
    monkeypatch.setattr(v2, "live_owned", lambda rows: original_live(rows, current.get))
    monkeypatch.setattr(v2, "snapshot_descendants", lambda *args: None)
    monkeypatch.setattr(v2.v1, "ports_free", lambda: True)
    ticks = iter(range(0, 1000, 40))
    monkeypatch.setattr(v2.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(v2.time, "sleep", lambda seconds: None)
    signaled = []
    def signal_child(pid, sig):
        signaled.append((pid, sig))
        current[pid] = None
    monkeypatch.setattr(v2.os, "kill", signal_child)
    monkeypatch.setattr(v2.os, "killpg", lambda *args: pytest.fail("exited parent group must not be signaled"))
    service = tmp_path / "service"
    v2.stop_service(service)
    assert signaled == [(1235, v2.signal.SIGTERM)]
    assert v2.c.read(tmp_path / "SERVICE_STOPPED.json")["all_owned_process_identities_exited"] is True


def test_actual_capture_manifest_keeps_v1_and_adds_executed_v2_source(tmp_path, monkeypatch):
    amendment_path = tmp_path / "amendment.json"
    v2.c.write_once(amendment_path, {"CPU_fixture": True})
    amendment = {"amendment_id": "cpu-fixture", "source_sha256": {str(Path(v2.__file__)): v2.c.file_hash(v2.__file__)}}
    monkeypatch.setattr(v2, "AMENDMENT", amendment_path)
    monkeypatch.setattr(v2, "verify_amendment", lambda: amendment)
    def prior_prepare(phase, binding, endpoint, destination, cap, generation):
        value = {"source_file_sha256": {"frozen-v1": "old-sha"}}
        v2.c.write_once(destination, value)
        return value
    monkeypatch.setattr(v2, "ORIGINAL_PREPARE", prior_prepare)
    result = v2.prepare_spec("round-1", None, None, tmp_path / "CAPTURE_SPEC.json", 1800, {})
    assert result["source_file_sha256"]["frozen-v1"] == "old-sha"
    assert result["source_file_sha256"][str(Path(v2.__file__))] == v2.c.file_hash(v2.__file__)
    assert result["source_file_sha256"][str(amendment_path)] == v2.c.file_hash(amendment_path)
    assert v2.c.read(tmp_path / "CAPTURE_SPEC_V1_BASE.json") == {"source_file_sha256": {"frozen-v1": "old-sha"}}
