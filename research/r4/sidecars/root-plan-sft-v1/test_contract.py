import ast
import importlib
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))


def test_public_plan_difference_only_filter_assignment():
    s=importlib.import_module('study')
    c={'query_users':['u07'],'target':'NUM'}
    canonical=s.program(c,'single_user','canonical');adaptive=s.program(c,'single_user','filter_first')
    assert adaptive==canonical.replace('selected = records','selected = relevant')
    assert s.program(c,'global','canonical')==s.program(c,'global','filter_first')
    assert 'u07' in adaptive and 'numeric value' in adaptive and 'labels.update' in adaptive
    assert len([n for n in ast.walk(ast.parse(adaptive)) if isinstance(n,ast.Await)])==1
    assert 'Answer:' not in adaptive and 'gold' not in adaptive
    assert 'from rlm.api import run as rlm' in adaptive
    assert 'json.load(open("records.json"))' in adaptive and 'records.jsonl' not in adaptive
    assert 'strict_map(child.answer, [row["id"] for row in batch])' in adaptive


def test_authored_masks_do_not_admit_fake_behavior_fields():
    s=importlib.import_module('study')
    row=s.authored_row('row','canonical','train-00','single_user',[1,2],[3,151645],'code')
    assert row['labels']==[-100,-100,3,151645] and row['loss_mask']==[0,0,1,1]
    assert s.validate_authored(row)==2
    with pytest.raises(ValueError):s.validate_authored({**row,'old_logprobs':[-.5,-.5]})
    with pytest.raises(ValueError):s.validate_authored({**row,'reward':1})
    with pytest.raises(ValueError):s.validate_authored({**row,'labels':[1,2,3,151645]})


def test_readout_keeps_only16_transferred_coordinates():
    s=importlib.import_module('study');original=s.read(s.PRIOR/'prepared-v2/EVAL_PLAN_FINAL.json')
    plan=s.build_plan(original)
    assert len(plan)==16 and len({r['id'] for r in plan})==16
    assert {r['stratum'] for r in plan}=={'query_transfer','length_transfer'}
    assert sorted(r['seed'] for r in plan)==list(range(981320201,981320209))+list(range(981320301,981320309))
    assert [r['source_coordinate_id'] for r in plan]==[r['id'] for r in original if r['stratum']!='validation']
