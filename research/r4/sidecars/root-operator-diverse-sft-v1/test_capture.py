import importlib

def test_actual_collector_composition_and_operator_scoring():
    s=importlib.import_module('od_study');c=importlib.import_module('od_collect')
    module=c.implementation()
    assert module.s is s and module.p.__name__=='od_protocol'
    row=s.read(s.ROOT/'inputs/TRAIN_PLAN.json')[0]
    context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id'])
    task=s.stack().native.task(context,s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['prompt'],0,row['id'])
    assert task.plain_query==row['question']
    assert s.qnative().first_prefix(task)==s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['token_ids']
    records=[dict(id='q000000000001',user='u1',weight=3),dict(id='q000000000002',user='u1',weight=5),dict(id='q000000000003',user='u2',weight=7)]
    labels={r['id']:'human being' for r in records}
    for operator,expected in [('count',2),('distinct',1),('weight',8)]:
        assert s.answer(records,labels,dict(operator=operator,scope='single',users=['u1'],target='human being'))==expected
    assert c.EDIT_COUNTS and all(v==1 for v in c.EDIT_COUNTS.values())
