"""Regression at the real executable seam, not merely the inner composer."""
import ast
import os
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PY='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'


def test_actual_corrected_entrypoints_import():
    for name in ('readout_v2.py','launch_v2.py'):
        result=subprocess.run([PY,str(ROOT/name),'--help'],capture_output=True,text=True,timeout=30,
          env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
        assert result.returncode==0,result.stderr


def test_flat_readout_preserves_collect_except_paths_and_ready_authentication():
    source=(ROOT.parent/'root-success-trajectory-sft-v1/readout.py').read_text()
    assert source.count("'prepared/PLAN.json'")==2 and source.count("'prepared/PROMPTS.json'")==1
    expected=source.replace("'prepared/PLAN.json'","'prepared-v2/PLAN.json'").replace("'prepared/PROMPTS.json'","'prepared-v2/PROMPTS.json'").replace('ready = s.verify()','ready = verify_corrected()')
    function=lambda text:next(n for n in ast.parse(text).body if isinstance(n,ast.AsyncFunctionDef) and n.name=='collect')
    assert ast.dump(function((ROOT/'readout_v2.py').read_text()))==ast.dump(function(expected))


def test_flat_launch_selects_corrected_executable_and_preserves_workflow():
    source=(ROOT/'launch.py').read_text().replace('ready=s.verify()','ready=r.verify_corrected()').replace("s.ROOT/'READY.json'","s.ROOT/'READY_V2.json'").replace("s.ROOT/'readout.py'","s.ROOT/'readout_v2.py'")
    function=lambda text:next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='execute')
    assert ast.dump(function((ROOT/'launch_v2.py').read_text()))==ast.dump(function(source))


def test_actual_corrected_launcher_two_training_three_readout_flow(tmp_path,monkeypatch):
    import study as s
    import readout_v2 as r
    import test_runtime
    original=s.load
    def corrected(name,path,pin):
        if name=='plan_test_actual_launch':path=ROOT/'launch_v2.py';pin=s.sha(path)
        return original(name,path,pin)
    monkeypatch.setattr(s,'load',corrected)
    monkeypatch.setattr(r,'verify_corrected',lambda:{'identity':'fixture'})
    test_runtime.test_owned_execute_runs_two_training_three_phases48_and_shared_caps(tmp_path,monkeypatch)
