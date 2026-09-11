import importlib
import json

def test_fixed48_pairs8sources_and_label_blind_plan():
    s=importlib.import_module('sm_study');p=importlib.import_module('sm_protocol');a=p.build()
    assert len(a['PLAN.json'])==48 and len(a['ACQUISITION_PLAN.json'])==8
    assert len({r['id'] for r in a['PLAN.json']})==48 and len({r['seed'] for r in a['PLAN.json']})==24
    assert [x['id'] for x in a['PUBLIC.json']]==[f'training-{i:02}' for i in range(8)]
    for block in range(24):
        pair=[r for r in a['PLAN.json'] if r['block']==block]
        assert {r['representation'] for r in pair}=={'INLINE','FILE'} and len({r['seed'] for r in pair})==1
    source=s.inputs();source['HOST_GOLD.json']={key:dict(answers={},labels={}) for key in source['HOST_GOLD.json']}
    b=p.build(source)
    for key in ('PLAN.json','ACQUISITION_PLAN.json','PUBLIC.json','QUERIES.json'):assert a[key]==b[key]

def test_map_bytes_only_inline_difference_and_strict_scores():
    p=importlib.import_module('sm_protocol');a=p.build();context=a['PUBLIC.json'][0];query=next(iter(a['QUERIES.json'].values()))['question'];raw=json.dumps({r['id']:'entity' for r in context['records']},indent=2)
    base=p.prompt(context,query,raw,'FILE');inline=p.prompt(context,query,raw,'INLINE')
    assert inline==base+'\n\n'+raw and raw not in base
    assert p.map_state(raw,[r['id'] for r in context['records']])['available']
    assert not p.map_state('{}',[r['id'] for r in context['records']])['available']
    assert p.score('Answer: 2',2,True)['reward']==1
    assert p.score('The answer is2',2,True)['reward']==0
    assert p.score(None,2,False)['reward'] is None
