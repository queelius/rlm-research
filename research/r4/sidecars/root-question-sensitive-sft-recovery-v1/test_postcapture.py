def test_training_only_owner_skips_capture_and_uses_service_local_clock(tmp_path, monkeypatch):
    import postcapture_owner as p
    o = p.implementation
    now = [1000.0]
    calls = []

    class Suite:
        def start_service(self, stage, binding, deadline):
            calls.append(('service', stage.name))
            now[0] += 30

        def release_service(self, stage):
            calls.append(('release', stage.name))

        def command(self, stage, label, argv, cap, deadline):
            calls.append((label, deadline, argv))
            if label == 'six-updates':
                now[0] += 500
            elif label == 'dev8':
                now[0] += 40
                raise RuntimeError('retain dev failure')

    output = tmp_path / 'attempt-002'
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', 'CPU_INTERCEPT_ONLY')
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY', 'CPU')
    monkeypatch.setattr(o, 'POSTCAPTURE_OUTPUT', output)
    monkeypatch.setattr(o, 'admit_complete_capture', lambda: True)
    monkeypatch.setattr(o.time, 'time', lambda: now[0])
    monkeypatch.setattr(o, 'alarm', lambda deadline: None)
    monkeypatch.setattr(o.s, 'runtime', lambda: None)
    monkeypatch.setattr(o.s, 'verify', lambda: {'identity': 'CPU'})
    monkeypatch.setattr(o.s, 'baseline_reference', lambda: {'planned': 80})
    monkeypatch.setattr(o.s, 'capture_boundary', lambda: [])
    monkeypatch.setattr(o, 'dependencies', lambda: Suite())
    monkeypatch.setattr(o.b, 'selected', lambda arm: {'step': 6})
    monkeypatch.setattr(o.b, 'binding', lambda arm: {})
    monkeypatch.setattr(o, 'harvest', lambda output, rows: rows)
    monkeypatch.setattr(o, 'cost_ledger', lambda output: {})
    result = o.execute(output)
    assert [x[0] for x in calls] == ['six-updates', 'service', 'dev8', 'protected72', 'release']
    protected = next(x for x in calls if x[0] == 'protected72')
    assert protected[1] == 1500 + 1950 + 40 - 90
    assert protected[2][1].endswith('/postcapture_readout.py')
    assert any(x['stage'] == 'sft6-dev' for x in result['error'])
    run = o.s.read(output / 'OWNER_RUN.json')
    assert (run['outer_seconds'], run['owned_seconds'], run['work_seconds']) == (4800, 4770, 4620)


def test_binding_rejects_partial_checkpoint(tmp_path, monkeypatch):
    import postcapture_binding as b
    monkeypatch.setattr(b, 'OUTPUT', tmp_path)
    b.s.write(tmp_path / 'training/SELECTION.json', {'step': 5})
    import pytest
    with pytest.raises(ValueError, match='fixed6'):
        b.selected('sft6')
