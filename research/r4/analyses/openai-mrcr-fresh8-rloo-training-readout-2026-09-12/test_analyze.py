"""Actual original raw native control, not a fabricated episode schema."""
from pathlib import Path
import importlib

def test_original32_native_control_and_fixed8vectors():
    assert (Path(__file__).parent/'analyze.py').exists(), 'auditor not implemented'
    a=importlib.import_module('analyze');old=a.stage('cp32')
    assert old['qualified'] and not old['integrity_errors']
    assert old['available']==old['planned']==32 and old['correct']==7
    assert old['physical']['returned']==66 and old['physical']['orphan_returned']==0
    assert old['physical']['start_only']==0 and old['initial_prefix_verified']==32
    groups=a.grouped(a.bindings().study.schedule('train'),old['rows'],old['rows'])
    assert [g['old_G4'] for g in groups]==['0000','0100','0000','0000','1111','0001','0010','0000']
    assert all(g['old_G4']==g['new_G4'] and g['paired_net_correct']==0 for g in groups)
