"""Catches lost old batches, aliasing, invalid partial deposit and provenance overclaim."""
import importlib.util
import json
from pathlib import Path
import pytest

def helper(tmp_path,arm):
    path=Path(__file__).with_name('ae_protocol.py')
    assert path.exists(),'isolated decoder package not implemented'
    import ae_protocol as p
    module_path=tmp_path/'batch_contract.py';module_path.write_bytes(p.helper_bytes(arm))
    spec=importlib.util.spec_from_file_location('fixture_contract_'+arm,module_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

@pytest.mark.parametrize('arm',['B','C'])
def test_reassignment_snapshot_and_latest_valid_conflict(tmp_path,monkeypatch,arm):
    monkeypatch.chdir(tmp_path);m=helper(tmp_path,arm)
    labels=m.strict_map('{"qa":"entity"}',['qa']);labels['qa']='location';labels['fabricated']='entity'
    labels=m.strict_map('{"qb":"location"}',['qb'])
    assert labels==({'qb':'location'} if arm=='B' else {'qa':'entity','qb':'location'})
    labels=m.strict_map('{"qa":"human being"}',['qa'])
    assert labels==({'qa':'human being'} if arm=='B' else {'qa':'human being','qb':'location'})
    ledger=[json.loads(line) for line in (tmp_path/'.decoder_calls.jsonl').read_text().splitlines()]
    assert len(ledger)==3 and ledger[0]['returned']=={'qa':'entity'}
    assert ledger[2]['conflicts']==[{'id':'qa','old':'entity','new':'human being'}]
    assert all(r['genuine_child_provenance']=='not_established_by_decoder' for r in ledger)

def test_invalid_atomic_and_fabricated_input_not_authenticated(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path);m=helper(tmp_path,'C')
    assert m.strict_map('{"qa":"entity"}',['qa'])=={'qa':'entity'}
    for raw,ids in [('{"qb":"entity","qb":"location"}',['qb']),('{"qb":"entity"}',['qc']),('{"qb":"not-category"}',['qb']),({'qb':'entity'},['qb']),('{"qb":',['qb'])]:
        with pytest.raises((ValueError,TypeError)):m.strict_map(raw,ids)
    # This literal never came from a model. Structural acceptance must not claim otherwise.
    assert m.strict_map('{"q_literal":"location"}',['q_literal'])=={'qa':'entity','q_literal':'location'}
    ledger=[json.loads(line) for line in (tmp_path/'.decoder_calls.jsonl').read_text().splitlines()]
    assert len(ledger)==7 and sum(r['ok'] for r in ledger)==2
    assert ledger[-1]['genuine_child_provenance']=='not_established_by_decoder'
    assert all('qb' not in r.get('returned',{}) for r in ledger)
