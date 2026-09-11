import asyncio
import json
from copy import deepcopy
from pathlib import Path
import pytest

def module():
    assert (Path(__file__).parent/'study.py').exists(),'shifted study absent'
    import study
    return study

def test_exact72_grid_prompt_equality_and_permuted_source_ids():
    s=module();d=s.build_design(s.build_data())
    assert len(d['plan'])==len({r['id'] for r in d['plan']})==72
    for i in range(0,72,3):
        rows=d['plan'][i:i+3];bodies=[s.make_request(d,r) for r in rows]
        assert len({s.serialize({k:v for k,v in b.items() if k!='structured_outputs'}) for b in bodies})==1
        context=d['contexts'][rows[0]['context_index']]
        tagged={r['arm']:[p['properties']['tag']['const'] for p in b['structured_outputs']['json']['prefixItems']] for r,b in zip(rows,bodies)}
        original=[r['id'] for r in context['records']]
        assert tagged['matching']==original and tagged['shifted']==original[17:]+original[:17]
        assert tagged['constant']==['p0000']*64
        assert sorted(tagged['matching'])==sorted(tagged['shifted']) and tagged['matching']!=tagged['shifted']

def test_named_alignment_never_repairs_primary_and_constant_has_no_named_target():
    s=module();records=[{'id':f'q{1000+i}','gold_label':['a','b'][i%2]} for i in range(64)]
    gold={'records':records,'labels':['a','b'],'arm':'shifted'}
    output=[{'tag':records[(i+17)%64]['id'],'label':records[(i+17)%64]['gold_label']} for i in range(64)]
    score=s.score_labels(json.dumps(output),gold)
    assert score['schema_valid'] and score['strict_correct']==0
    assert score['named_record_correct']==64 and score['named_minus_displayed']==64
    for item in output:item['tag']='p0000'
    score=s.score_labels(json.dumps(output),{**gold,'arm':'constant'})
    assert score['schema_valid'] and score['named_record_correct'] is None

def test_strict_late_wrong_tag_duplicate_key_order_cardinality():
    s=module();gold={'records':[{'id':f'q{1000+i}','gold_label':'a'} for i in range(64)],'labels':['a'],'arm':'matching'}
    good=[{'tag':r['id'],'label':'a'} for r in gold['records']]
    cases=[good[:-1],good+[good[0]],good[:-1]+[{'tag':'q9999','label':'a'}],good[:-1]+[{'label':'a','tag':'q1063'}]]
    for case in cases:
        result=s.score_labels(json.dumps(case),gold);assert not result['schema_valid'] and result['strict_correct']==0 and result['named_record_correct'] is None
    raw=json.dumps(good).replace('"tag": "q1000"','"tag": "q1000", "tag": "q1000"')
    assert not s.score_labels(raw,gold)['schema_valid']

def test_owned_deadline_and_actual_qualified_launcher_path():
    assert (Path(__file__).parent/'owned.py').exists(),'owned wrapper absent'
    import owned
    assert owned.work_deadline(100)==850 and owned.collection_command_cap(100,200)==630
    with pytest.raises(TimeoutError):owned.collection_command_cap(100,850)
    suite=owned.load_suite()
    assert suite.SERVE==Path('/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-role-routing-v1/source/serve.py')
    assert suite.c.ROLE==suite.SERVE.parent.parent
