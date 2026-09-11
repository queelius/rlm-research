"""Fixed inventory and authored query truth, independent of hidden gold."""
import copy
import importlib
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/'root-query-sensitive-rl-v1/inputs'

def inputs():return {name:json.loads((SOURCE/name).read_text()) for name in ('PUBLIC.json','QUERIES.json','PLANS.json','GROUPS.json','HOST_GOLD.json')}

def test_full_inventory_no_overlap_and_no_gold_selection():
    p=importlib.import_module('od_protocol');original=inputs();result=p.build(original);train=result['TRAIN_PLAN.json'];free=result['FREE_PLAN.json']
    assert len(train)==72 and len(free)==24 and len({r['id'] for r in train+free})==96
    assert sum(16//r['width'] for r in train)==180
    assert sum(16//r['width']+2 for r in train)==324
    assert {r['context_id'] for r in train}=={f'training-{i:02}' for i in range(12)}
    assert {r['context_id'] for r in free}=={f'readout-{i:02}' for i in range(4,12)}
    mutated=copy.deepcopy(original);mutated['HOST_GOLD.json']={'arbitrary':'unusable sentinel'}
    other=p.build(mutated)
    for key in ('TRAIN_PLAN.json','FREE_PLAN.json','PUBLIC.json','QUERIES.json','GATE_PLAN.json'):assert result[key]==other[key]
    gate=result['GATE_PLAN.json'];assert len(gate)==6 and {(r['operator'],r['width']) for r in gate}=={(o,w) for o in ('count','distinct','weight') for w in (4,16)}

def test_reduction_uses_actual_live_labels_and_operator_scope():
    p=importlib.import_module('od_protocol')
    records=[{'id':'q111111111111','user':'u1','text':'a','weight':3},{'id':'q222222222222','user':'u2','text':'b','weight':7},{'id':'q333333333333','user':'u1','text':'c','weight':2}]
    labels={'q111111111111':'human being','q222222222222':'human being','q333333333333':'entity'}
    for operator,want in [('count',2),('distinct',2),('weight',10)]:
        row={'operator':operator,'users':['u1','u2'],'target':'human being','names':{'records':'rows','labels':'observed','selected':'chosen','result':'answer'}}
        code=p.reduction(row);assert 'q111111111111' not in code
        state={'rows':records,'observed':labels};exec(code,state)
        assert state['answer']==want
    row['users']=['u1'];state={'rows':records,'observed':labels};exec(p.reduction(row),state);assert state['answer']==3

def test_templates_describe_each_operator_and_scope_without_algorithm():
    p=importlib.import_module('od_protocol')
    q={'operator':'weight','scope':'all','users':['u0','u1','u2','u3'],'target':'entity'}
    texts=[p.question(q,i) for i in range(4)]
    assert len(set(texts))==4
    for text in texts:assert 'entity' in text and 'weight' in text and 'all records' in text and 'Answer: N' in text
    assert all('sum(' not in text and 'labels[' not in text for text in texts)
