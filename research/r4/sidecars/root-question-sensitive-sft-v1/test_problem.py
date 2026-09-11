"""Catches substituted operators/scopes/thresholds and accidental pair leakage."""
from pathlib import Path

def test_qualified_study_resolves_its_actual_start_without_path_shadowing():
    assert Path(__file__).with_name('qs_study.py').exists(),'qualified study absent'
    import qs_study as s
    assert s.starting_policy()['adapter_sha256']=='94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006'

def test_exact_specs_and_parameter_holdouts():
    assert Path(__file__).with_name('qs_problem.py').exists(),'new exact table not implemented'
    import qs_problem as p
    train=[r for j in range(8) for r in p.specs('train',j)];held=[r for j in range(8) for r in p.specs('protected',j)]
    assert len(train)==len(held)==72
    assert {r['threshold'] for r in train if r['operator']=='threshold_users'}=={2,6}
    assert {r['threshold'] for r in held if r['operator']=='threshold_users'}=={4,8}
    tr={(r['target'],r['target_b']) for r in train if r['operator']=='conditional_weight'}
    te={(r['target'],r['target_b']) for r in held if r['operator']=='conditional_weight'}
    assert not tr&te
    assert p.specs('train',0)[0]['users']==['u0','u1','u2','u3']
    assert p.specs('protected',0)[2]['users']==['u0','u1','u2','u3']
    assert p.specs('protected',0)[3]['users']==['u0','u2']

def test_requested_scope_strict_threshold_and_B_counted_once():
    assert Path(__file__).with_name('qs_problem.py').exists(),'scoped oracle absent'
    import qs_problem as p
    records=[dict(id='a',user='u0',weight=2),dict(id='b',user='u0',weight=2),dict(id='c',user='u1',weight=6),dict(id='d',user='u0',weight=7),dict(id='e',user='u2',weight=3)]
    labels={'a':'A','b':'A','c':'A','d':'B','e':'B'}
    row=dict(target='A',target_b='B',users=['u0','u2'],threshold=4)
    wanted={'count':2,'distinct_users':1,'weight_sum':4,'threshold_users':0,'maximum_weight':4,'conditional_weight':7}
    for op,want in wanted.items():
        rr={**row,'operator':op};assert p.answer(records,labels,rr)==want;assert p.enumerated_answer(records,labels,rr)==want
    assert p.answer(records,labels,{**row,'operator':'threshold_users','threshold':2})==1
    assert p.answer(records,labels,{**row,'operator':'conditional_weight','target':'B','target_b':'A'})==4
    assert p.answer(records,labels,{**row,'operator':'maximum_weight','target':'absent'})==0
