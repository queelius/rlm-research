from pathlib import Path
from types import SimpleNamespace
import pytest
def local_owner():
    import study as s
    import protocol as p
    with s.aliases({'study':s,'protocol':p}):return s.load('contract_evidence_test_owner',s.ROOT/'owner.py',s.sha(s.ROOT/'owner.py'))

def test_exact_attempt_boundaries_and_twenty_four_nulls(tmp_path):
    owner=local_owner()
    import study as s
    with pytest.raises(ValueError):owner.check_output(tmp_path/'wrong')
    args=SimpleNamespace(output=s.ATTEMPT/'rollout',binding=s.ATTEMPT/'service/BINDING.json',endpoint=s.ATTEMPT/'service/service/endpoint-original.json',deadline=2000000000.)
    owner.validate_paths(args)
    args.output=s.ATTEMPT/'wrong'
    with pytest.raises(ValueError):owner.validate_paths(args)
    rows=owner.inventory(s.ATTEMPT)
    assert len(rows)==24 and all(r['reward'] is None and r['operational_success']==0 for r in rows)

def test_termination_stops_after_single_service_and_preserves_nulls(tmp_path,monkeypatch):
    owner=local_owner()
    import study as s
    import signal
    output=tmp_path/'attempt';started=[];released=[]
    suite=SimpleNamespace(start_service=lambda p,*a:started.append(p),release_service=lambda p:released.append(p),command=lambda *a:signal.getsignal(signal.SIGTERM)(signal.SIGTERM,None))
    monkeypatch.setattr(s,'ATTEMPT',output);monkeypatch.setattr(s,'runtime',lambda:None);monkeypatch.setattr(s,'verify',lambda:dict(identity='cpu'))
    real_sha=s.sha;monkeypatch.setattr(s,'sha',lambda p:'0'*64 if p==s.ROOT/'READY.json' else real_sha(p));monkeypatch.setattr(s,'binding',lambda:{})
    monkeypatch.setattr(owner,'dependencies',lambda:suite);monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_INTERCEPT')
    result=owner.execute(output)
    assert not result['complete'] and started==released and len(started)==1
    assert result['planned']==24 and result['active_unreleased_service'] is None
    assert s.read(output/'COST_LEDGER.json')['total']['physical_request_attempts']==0
