"""Actual owner path preserves assigned MIG through TRAIN Popen and retains failed inventory."""
import importlib.util
from pathlib import Path
import os
import pytest

def module():
    path=Path(__file__).with_name('dose_owner.py');assert path.exists(),'training owner missing'
    spec=importlib.util.spec_from_file_location('dose_owner_test',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_actual_owner_training_entry_inherits_gpu(tmp_path,monkeypatch):
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    m=module();suite=m.s.dependencies();seen=[]
    class P:
        pid=987654;returncode=0
        def wait(self,timeout=None):return 0
        def poll(self):return 0
    def popen(argv,**kw):
        import dose_train
        parsed=dose_train.parse_args(argv[2:]);assert parsed.output==tmp_path/'attempt/training'
        seen.append((argv,kw['env']['CUDA_VISIBLE_DEVICES']));return P()
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','MIG-CPU-fixture-exact')
    monkeypatch.setattr(m.subprocess,'Popen',popen)
    monkeypatch.setattr(suite.life,'observe',lambda pid:dict(pid=pid,pgid=pid,uid=os.getuid()))
    monkeypatch.setattr(suite.life,'safe_observation',lambda value:value)
    monkeypatch.setattr(suite,'stop_child',lambda *a:None)
    monkeypatch.setattr(m.s,'ATTEMPT',tmp_path/'attempt')
    monkeypatch.setattr(m.s,'verify',lambda:dict(identity='CPU'))
    result=m.execute(tmp_path/'attempt')
    assert seen[0][0][:2]==[str(m.s.original().TRAIN),str(m.s.ROOT/'dose_train.py')]
    assert seen[0][1]=='MIG-CPU-fixture-exact'
    assert not result['complete'] and result['released'] and result['planned_full_endpoints']==96 and result['planned_first_actions']==24
    assert m.s.read(tmp_path/'attempt/PLANNED_EVALUATION.json')['full'][0]['available'] is False

def test_wrong_output_and_no_gpu_rejected_before_launch(tmp_path,monkeypatch):
    m=module()
    with pytest.raises(ValueError):m.check_output(tmp_path/'wrong')
    monkeypatch.setattr(m.s,'ATTEMPT',tmp_path/'attempt');monkeypatch.delenv('CUDA_VISIBLE_DEVICES',raising=False)
    with pytest.raises(ValueError,match='one assigned'):m.execute(tmp_path/'attempt')
    assert not (tmp_path/'attempt').exists()
