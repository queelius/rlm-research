"""Real LR1e-5 control exercises the non-cp32 explicit binding and raw path helper."""
from pathlib import Path
import importlib

def test_actual_lr1e5_training_control_not_cp32_or_new_endpoint():
    assert (Path(__file__).parent/'analyze.py').exists(), 'dose auditor not implemented'
    a=importlib.import_module('analyze');r=a.stage('train','LR1e5')
    assert r['qualified'] and not r['integrity_errors'] and r['correct']==17
    assert r['available']==32 and r['physical']['returned']==65
    assert r['physical']['start_only']==r['physical']['orphan_returned']==0
    row=next(iter(r['rows'].values()));item,trace,native=a.paths.load_episode(row)
    assert item['coordinate']==row['coordinate'] and len(native)==len(row['native_actions'])
    assert a.detail(row)['final']['final_sha256']==row['final_sha256']
