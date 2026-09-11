import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
def modules():
    for name in ('study','protocol'):
        spec=importlib.util.spec_from_file_location('warm_test_'+name,ROOT/(name+'.py'))
        value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    return sys.modules['study'],sys.modules['protocol']
def test_exact_twenty_four_paired_blocks_and_unambiguous_all_scope():
    s,p=modules();data=p.build();rows=data['PLAN.json']
    assert len(rows)==24 and len({r['block_id'] for r in rows})==8
    assert {r['root'] for r in rows}=={'released_reference','interface4','success8'}
    assert {r['context_id'] for r in rows}=={'readout-00','readout-01','readout-02','readout-03'}
    for block in {r['block_id'] for r in rows}:
        paired=[r for r in rows if r['block_id']==block]
        assert len(paired)==3 and len({r['seed'] for r in paired})==1
    for task in data['QUERIES.json'].values():
        if task['query']['scope']=='all':
            assert task['question'].startswith('Across all records, regardless of which of u0, u1, u2, or u3 owns the record,')
            assert task['original_question']!=task['question']
        else:assert task['original_question']==task['question']
def test_fixed_roots_and_child_not_campaign_generations():
    s,p=modules()
    for arm,start in [('released_reference','857a7ce6'),('interface4','efab2913'),('success8','66cce400')]:
        b=s.binding(arm);assert len(b['models'])==2
        assert b['models'][b['role_map']['root']]['adapter_sha256'].startswith(start)
        assert b['models'][b['fixed_child']]['adapter_sha256'].startswith('c32de129')
        assert b['fixed_root']['arm']==arm and 'campaign_policy' not in b
def test_oracle_and_strict_final_no_rescue():
    _,p=modules();records=[dict(id='a',user='u0',weight=2),dict(id='b',user='u0',weight=3),dict(id='c',user='u1',weight=5)];labels={'a':'x','b':'x','c':'x'}
    assert p.answer(records,labels,dict(users=['u0'],target='x',operator='count'))==2
    assert p.answer(records,labels,dict(users=['u0'],target='x',operator='distinct'))==1
    assert p.answer(records,labels,dict(users=['u0'],target='x',operator='weight'))==5
    assert p.score('The answer is Answer: 5',5,True)['reward']==0
    assert p.score('Answer: 5',5,False)['reward'] is None
    assert p.score('Answer: 5',5,True)['reward']==1
