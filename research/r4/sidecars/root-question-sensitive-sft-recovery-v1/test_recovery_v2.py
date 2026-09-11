from pathlib import Path


def test_recovered_binding_exposes_real_validator(monkeypatch, tmp_path):
    import recovery_binding_v2 as b
    assert callable(b.validate)
    monkeypatch.setattr(b, "binding", lambda arm: {"question_sensitive": {"arm": "sft6"}})
    seen = []
    class Validator:
        def validate_descriptor(self, value, descriptor, pin): seen.append((value, descriptor, pin))
    monkeypatch.setattr(b.s, "load", lambda *args, **kwargs: Validator())
    monkeypatch.setattr(b.s, "sha", lambda path: "binding-pin")
    value = {"question_sensitive": {"arm": "sft6"}}
    b.validate(value, {"model": "x"}, tmp_path / "BINDING.json")
    assert seen == [(value, {"model": "x"}, "binding-pin")]


def test_v2_owner_routes_only_readout_to_v2(monkeypatch, tmp_path):
    import recovery_owner_v2 as o
    seen = []
    monkeypatch.setattr(o, "verify_v2", lambda: {"identity": "V2"})
    monkeypatch.setattr(o.v1, "execute", lambda output: {
        "capture": o.v1._command_argv("recovery_collect.py", output, 1, []),
        "readout": o.v1._command_argv("recovery_readout.py", output, 1, []),
    })
    result = o.execute(tmp_path)
    assert Path(result["capture"][1]).name == "recovery_collect.py"
    assert Path(result["readout"][1]).name == "recovery_readout_v2.py"

