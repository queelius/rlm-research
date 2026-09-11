"""Exact factor endpoints and96 paired trajectories; no implementation import before test."""
import collections
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def protocol():
    path=ROOT/'protocol.py'
    assert path.exists(), 'clarity protocol missing'
    spec=importlib.util.spec_from_file_location('clarity_protocol_test',path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def anchors():
    old=ROOT.parent/'root-supplied-map-reducer-v1/inputs'
    new=ROOT.parent/'root-example-map-visibility-v1/inputs'
    oldp={r['id']:r['prompt'] for r in json.loads((old/'PROMPTS.json').read_text())}
    newp={r['id']:r['prompt'] for r in json.loads((new/'PROMPTS.json').read_text())}
    a={(r['context_id'],r['family']):oldp[r['id']] for r in json.loads((old/'PLAN.json').read_text()) if r['map_source']=='native_c32' and not r['reducer']}
    b={(r['context_id'],r['family']):newp[r['id']] for r in json.loads((new/'PLAN.json').read_text()) if r['example'] and not r['inline']}
    return a,b

def test_three_seed_pairs_per_block_and_balanced96_treatments():
    p=protocol()
    contexts=json.loads((ROOT.parent/'root-example-map-visibility-v1/inputs/PUBLIC.json').read_text())
    rows=p.plan_for(contexts)
    assert len(rows)==len({r['id'] for r in rows})==96
    assert len({r['seed'] for r in rows})==24
    byblock=collections.defaultdict(list)
    for r in rows:byblock[r['block_id']].append(r)
    assert len(byblock)==8
    for block in byblock.values():
        assert len(block)==12
        assert len({r['seed'] for r in block})==3
        assert collections.Counter((r['schema'],r['map_contract']) for r in block)=={(False,False):3,(False,True):3,(True,False):3,(True,True):3}
        for seed in {r['seed'] for r in block}:
            assert len({(r['schema'],r['map_contract']) for r in block if r['seed']==seed})==4
    for cell in ((False,False),(False,True),(True,False),(True,True)):
        assert collections.Counter(r['treatment_order'] for r in rows if (r['schema'],r['map_contract'])==cell)=={0:6,1:6,2:6,3:6}

def test_both_endpoints_are_exact_historical_prompt_bytes_for_all8_blocks():
    p=protocol();old,new=anchors()
    assert old.keys()==new.keys() and len(old)==8
    for key,text in old.items():
        assert p.prompt(text,dict(schema=False,map_contract=False)).encode()==text.encode()
        assert p.prompt(text,dict(schema=True,map_contract=True)).encode()==new[key].encode()

def test_crossed_factors_keep_their_own_changes_and_no_inline_or_helper():
    p=protocol();old,_=anchors();base=next(iter(old.values()))
    fields=p.prompt(base,dict(schema=True,map_contract=False))
    contract=p.prompt(base,dict(schema=False,map_contract=True))
    assert 'id, user, and text fields' in fields and 'using the user field in records.json' in fields
    assert 'No source semantic labels are present.' in fields and 'Supplied-map diagnostic treatment:' in fields
    assert 'id, synthetic user metadata, and original question text' in contract and 'using their public user metadata' in contract
    assert 'records.json and context.txt contain no category labels.' in contract and 'or additional child calls' in contract
    for text in (fields,contract):
        assert 'Optional API example (first four records only, NOT the final answer)' in text
        assert '<supplied_labels_json>' not in text and 'count_labels' not in text
