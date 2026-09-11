import json
from pathlib import Path

import pytest

import readout_study as study
import readout_owner as owner
import readout_seal as seal


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def test_checkpoint2_gate_skips_without_complete_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(study, "SPARSE_ATTEMPT", tmp_path / "missing")
    decision = study.checkpoint2_decision()
    assert decision["run"] is False
    assert decision["reason"] == "sparse owner terminal absent"


def test_checkpoint2_gate_authenticates_committed_step(tmp_path, monkeypatch):
    attempt = tmp_path / "sparse"
    checkpoint = attempt / "training/checkpoint-2"
    for name, content in {"adapter_model.safetensors": "weights", "adapter_config.json": "{}",
                          "optimizer.pt": "opt", "rng_state.pt": "rng"}.items():
        (checkpoint / name).parent.mkdir(parents=True, exist_ok=True)
        (checkpoint / name).write_text(content)
    files = {name: study.sha(checkpoint / name) for name in
             ("adapter_model.safetensors", "adapter_config.json", "optimizer.pt", "rng_state.pt")}
    state = {"optimizer_steps": 2, "generation": {"generation_id": "g"},
             "files_sha256": files, "metrics": {"episodes": 11, "root_turns": 154,
             "root_action_tokens": 18517}}
    write_json(checkpoint / "state.json", state)
    policy = {"path": str(checkpoint), "step": 2, "adapter_sha256": files["adapter_model.safetensors"],
              "config_sha256": files["adapter_config.json"], "state_sha256": study.sha(checkpoint / "state.json")}
    write_json(attempt / "training/RESULT.json", {"optimizer_steps": 2, "policy": policy})
    write_json(attempt / "OWNER_TERMINAL.json", {"complete": True, "released": True, "policy": policy})
    monkeypatch.setattr(study, "SPARSE_ATTEMPT", attempt)
    decision = study.checkpoint2_decision()
    assert decision["run"] is True
    assert decision["policy"]["step"] == 2


def test_inventory_is_exact_fixed72():
    rows = owner.planned_inventory(Path("/tmp/readout"))
    assert len(rows) == 72
    assert len({row["coordinate"]["id"] for row in rows}) == 72
    assert {row["arm"] for row in rows} == {"checkpoint2"}


def test_budget_and_collector_contract():
    limits = owner.budget(100.0)
    assert limits == {"started": 100.0, "work": 2500.0, "owned": 2770.0, "outer": 2800.0}
    argv = owner.collector_argv(Path("/x"), 123.0)
    assert argv[-2:] == ["--deadline", "123.0"]
    assert "readout_collect.py" in argv[1]


def test_actual_owner_service_and_nonempty_collector_chain(tmp_path, monkeypatch):
    attempt = tmp_path / "attempt"
    monkeypatch.setattr(study, "ATTEMPT", attempt)
    monkeypatch.setattr(study, "verify_prepared", lambda: {"identity": "fixture"})
    policy = {"path": "/checkpoint-2", "step": 2}
    monkeypatch.setattr(study, "checkpoint2_decision",
                        lambda: {"run": True, "reason": None, "policy": policy})
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU-INTERCEPT")
    events = []
    timers = []
    monkeypatch.setattr(owner.signal, "setitimer", lambda _kind, seconds: timers.append(seconds))

    class Suite:
        def start_service(self, path, binding, _deadline):
            events.append(("start", binding))
            write_json(path / "BINDING.json", {"binding": True})
            write_json(path / "service/endpoint-original.json", {"endpoint": "fixture"})
        def command(self, _service, name, argv, _cap, _deadline):
            events.append((name, argv))
        def release_service(self, _path): events.append(("release", None))

    monkeypatch.setattr(owner, "dependencies", lambda: Suite())
    monkeypatch.setattr(owner.collect, "binding_for", lambda value: {"policy": value})
    monkeypatch.setattr(owner.collect, "prepare_spec",
                        lambda phase, *_args: events.append(("prepare", phase)))
    monkeypatch.setattr(owner.export, "export_attempt",
                        lambda *_args: {"complete": True, "episodes": 72})
    result = owner.execute(attempt)
    assert result["complete"] is True and result["released"] is True
    assert events[0] == ("start", {"policy": policy})
    assert ("prepare", "readout-checkpoint2") in events
    command = next(event for event in events if event[0] == "collect-checkpoint2")
    assert command[1][1] == str(study.ROOT / "readout_collect.py")
    assert events[-1] == ("release", None)
    assert timers[1] > timers[0] and timers[-2] <= 90.0 and timers[-1] == 0


def test_ready_binds_authenticated_checkpoint2(monkeypatch):
    monkeypatch.setattr(study, "checkpoint2_decision", lambda: {
        "run": True, "policy": {"step": 2, "path": "/exact/checkpoint-2"},
        "owner_terminal_sha256": "owner", "state_sha256": "state"})
    monkeypatch.setattr(study, "read", lambda _path: {"identity": "campaign"})
    monkeypatch.setattr(study, "sha", lambda _path: "campaign-sha")
    value=seal.build_ready(created_epoch=123.0)
    assert value["checkpoint2"] == {"policy": {"step": 2, "path": "/exact/checkpoint-2"},
                                    "owner_terminal_sha256": "owner", "state_sha256": "state"}


def test_cost_ledger_reads_actual_role_audit_layout(tmp_path):
    audit=tmp_path/"readout/rollout/role-audit";audit.mkdir(parents=True)
    write_json(audit/"r1-request.json",{"request_id":"r1","status":"routed"})
    write_json(audit/"r1-result.json",{"request_id":"r1","status":"returned",
        "native_wire_response":{"http_status":200,"body":json.dumps({"choices":[{}],"usage":{
            "prompt_tokens":10,"completion_tokens":3,"prompt_tokens_details":{"cached_tokens":4}}})}})
    write_json(audit/"r2-request.json",{"request_id":"r2","status":"routed"})
    value=owner.cost_ledger(tmp_path)
    assert value["role_requests"]==2 and value["response_proven_attempts"]==1
    assert value["prepared_attempt_unknown"]==1 and value["http_2xx_choice_payloads"]==1
    assert value["usage"]=={"known":{"input":10,"output":3,"cached":4},"unknown":{"input":0,"output":0,"cached":0}}
