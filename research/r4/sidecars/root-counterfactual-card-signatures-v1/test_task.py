"""Independent integer edges and real composed task/collector contracts."""
import asyncio
from pathlib import Path
from unittest.mock import patch

def test_threshold_is_actual_question_parameter_and_conditional_counts_once():
    assert Path(__file__).with_name('cf_problem.py').exists(),'counterfactual task oracle missing'
    import cf_problem as p
    rr=[dict(id='a',user='u0',weight=2),dict(id='b',user='u0',weight=2),dict(id='c',user='u1',weight=6),dict(id='d',user='u0',weight=7),dict(id='e',user='u2',weight=3)]
    labels={'a':'A','b':'A','c':'A','d':'B','e':'B'};row=dict(target='A',target_b='B',users=['u0','u1','u2','u3'])
    assert p.answer(rr,labels,{**row,'operator':'threshold_users','threshold':3})==2
    assert p.answer(rr,labels,{**row,'operator':'threshold_users','threshold':5})==1
    assert p.answer(rr,labels,{**row,'operator':'maximum_weight','threshold':5})==6
    assert p.answer(rr,labels,{**row,'operator':'conditional_weight','threshold':5})==7
    assert p.answer(rr,{k:'C' for k in labels},{**row,'operator':'maximum_weight','threshold':5})==0

def test_original_templates_and_private_gold_do_not_change_public_task():
    assert Path(__file__).with_name('cf_study.py').exists(),'counterfactual study missing'
    import cf_study as s
    public={c['id']:c for c in s.read(s.CT/'inputs/PUBLIC.json')};rows=[r for r in s.read(s.CT/'inputs/FREE_PLAN.json') if r['panel']=='composition']
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,data):self.files[name]=data
    async def files(task):
        m=Memory();await task.setup(None,m);return m.files
    for old in rows:assert s.problem.question({**old,'threshold':5})==old['question']
    row={**rows[0],'threshold':5,'card_arm':'U','variant':'original'};ctx=public[row['context_id']]
    task=s.make_task(ctx,row,0);changed=s.make_task(ctx,{**row,'labels':{'fake':'oracle'}},99999)
    assert task.data.prompt==changed.data.prompt and asyncio.run(files(task))==asyncio.run(files(changed))
    assert set(asyncio.run(files(task)))=={'records.json','context.txt','query.txt','batch_contract.py'}

def test_collector_actual_main_composes_exact96_argv():
    assert Path(__file__).with_name('cf_collect.py').exists(),'collector alias missing'
    import cf_study as s
    import cf_collect as c
    m=c.implementation();captured=[]
    async def run(args):captured.append((args.mode,args.plan,args.start,args.stop))
    with patch('sys.argv',['cf_collect.py','--mode','free','--plan','FREE_PLAN.json','--start','0','--stop','96','--binding','binding','--endpoint','endpoint','--output','output','--deadline','2000000000']),patch.object(m,'run',run):c.main()
    assert captured==[('free','FREE_PLAN.json',0,96)]
