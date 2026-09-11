import pytest
from types import SimpleNamespace
def test_phase_limits_and_exact_collector_paths():
    import owner
    import study as s
    import collect
    limits=owner.phase_deadlines(100.,1750.)
    assert limits==dict(phase=580.,startup=280.)
    assert owner.collection_deadline(280.,580.,1750.)==580.
    assert owner.collection_deadline(1600.,2080.,1750.)==1750.
    for arm in s.ROOTS:
        argv=owner.collector_argv(s.ATTEMPT,arm,580.)
        args=collect.parse_args(argv[2:]);owner.validate_paths(args)
        assert args.root==arm and args.output==s.ATTEMPT/arm/'rollout'
    args.output=s.ATTEMPT/'wrong'
    with pytest.raises(ValueError):owner.validate_paths(args)
    rows=owner.inventory(s.ATTEMPT)
    assert len(rows)==24 and all(r['reward'] is None and r['operational_success']==0 for r in rows)
def test_main_termination_does_not_start_later_phases(tmp_path,monkeypatch):
    import owner,study as s,signal
    out=tmp_path/'attempt';started=[];released=[]
    suite=SimpleNamespace(start_service=lambda path,*args:started.append(path),release_service=lambda path:released.append(path),command=lambda *args:signal.getsignal(signal.SIGTERM)(signal.SIGTERM,None))
    monkeypatch.setattr(s,'ATTEMPT',out);monkeypatch.setattr(s,'runtime',lambda:None);monkeypatch.setattr(s,'verify',lambda:dict(identity='cpu'))
    real=s.sha;monkeypatch.setattr(s,'sha',lambda path:'0'*64 if path==s.ROOT/'READY.json' else real(path))
    monkeypatch.setattr(owner,'dependencies',lambda:suite);monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_INTERCEPT')
    result=owner.execute(out)
    assert not result['complete'] and len(started)==1 and released==started
    assert result['active_unreleased_service'] is None and result['planned']==24
    assert s.read(out/'COST_LEDGER.json')['total']['physical_request_attempts']==0
