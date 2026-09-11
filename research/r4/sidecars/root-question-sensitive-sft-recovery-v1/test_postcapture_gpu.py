import os
from types import SimpleNamespace


def test_training_popen_keeps_gpu_but_evaluation_uses_existing_command(tmp_path, monkeypatch):
    import postcapture_gpu as g
    calls = []
    class Process:
        pid = 123456789
        returncode = 0
        def wait(self, timeout=None): return 0
    base = SimpleNamespace(
        life=SimpleNamespace(observe=lambda pid: dict(pid=pid, pgid=pid, uid=os.getuid()),
                             safe_observation=lambda value: value),
        stop_child=lambda process, observation: calls.append(('stop', process.pid)),
        command=lambda *args: calls.append(('evaluation', args[1], args[2][1])))
    def popen(argv, **kw):
        calls.append(('training', kw['env']['CUDA_VISIBLE_DEVICES']))
        return Process()
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', 'MIG-ACTUAL-ASSIGNED-FIXTURE')
    monkeypatch.setattr(g.subprocess, 'Popen', popen)
    runner = g.TrainingSuite(base)
    runner.command(tmp_path, 'six-updates', ['python', 'qualified_train.py'], 10, g.time.time()+10)
    runner.command(tmp_path, 'dev8', ['python', str(g.p.s.SOURCE_ROOT / 'postcapture_readout.py')], 10, g.time.time()+10)
    assert calls == [('training', 'MIG-ACTUAL-ASSIGNED-FIXTURE'), ('stop', 123456789), ('evaluation', 'dev8', str(g.p.s.SOURCE_ROOT / 'postcapture_readout_gpu.py'))]
    assert g.p.s.read(tmp_path / 'six-updates-COMMAND.json')['gpu_visible_to_command'] is True


def test_readout_subprocess_namespace_matches_training():
    import postcapture_gpu as g
    import postcapture_readout_gpu as reader
    assert reader.b.OUTPUT == g.OUTPUT
