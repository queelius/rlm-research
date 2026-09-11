"""Metadata disclosure contract and exact composed collector entry."""
import asyncio
import json
from pathlib import Path
import sys

def test_spec_values_and_prose_equivalence():
    assert Path(__file__).with_name('ts_protocol.py').exists(),'task-spec serializer missing'
    import ts_protocol as p
    row=dict(operator='threshold_users',target='entity',target_b='location',gold=999)
    expected={'operator':'threshold_users','category_a':'entity','category_b':None,'scope':'all records and all users','threshold':5,'threshold_comparison':'strictly greater than'}
    assert p.spec(row)==expected
    assert p.prose(expected)=='Requested operator: threshold_users. Category A: entity. Category B: not applicable. Scope: all records and all users. Threshold: 5. Threshold comparison: strictly greater than.\n'
    assert p.spec({**row,'gold':0,'labels':{'secret':'human being'}})==expected
    assert p.spec({**row,'operator':'conditional_weight'})['category_b']=='location'
    assert p.spec({**row,'operator':'maximum_weight'})['threshold'] is None

def test_exact_owner_collector_main(monkeypatch):
    assert Path(__file__).with_name('ts_owner.py').exists(),'bounded72 owner missing'
    import ts_owner as o
    import ts_collect as c
    import ts_study as s
    argv=o.collector_argv(Path('/CPU/service-sft24'),Path('/CPU/sft24/free'),123.)
    module=c.implementation();args=module.parse_args(argv[2:])
    assert (args.mode,args.plan,args.start,args.stop)==('free','FREE_PLAN.json',0,72)
    async def run(args):
        import od_study,od_binding
        assert od_study is s and od_binding is s
        assert args.output==Path('/CPU/sft24/free')
    monkeypatch.setattr(module,'run',run);monkeypatch.setattr(sys,'argv',argv[1:]);c.main()

def test_original_files_unchanged_and_private_gold_invariant():
    import ts_study as s
    context=dict(id='CPU',size=1,index=0,stratum='root_new',native_context_id=982699001,records=[dict(id='q000000000001',user='u0',text='Who is the president?',weight=7)])
    context['text']=json.dumps(context['records'][0],sort_keys=True)+'\n'
    row=dict(id='CPU-task',operator='threshold_users',target='human being',target_b='entity',question='Across all records, how many users have total human being weight strictly greater than 5?')
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,content):self.files[name]=content
    async def files(task):
        memory=Memory();await task.setup(trace=None,runtime=memory);return memory.files
    seen={}
    for arm in ('U','P','J'):
        task=s.make_task(context,{**row,'interface_arm':arm},0);changed=s.make_task(context,{**row,'interface_arm':arm,'labels':{'secret':'location'}},999)
        seen[arm]=asyncio.run(files(task));assert seen[arm]==asyncio.run(files(changed))
        assert s.o.qnative().first_prefix(task)==s.o.qnative().first_prefix(changed)
    assert set(seen['U'])=={'records.json','context.txt','query.txt','batch_contract.py'}
    for arm,extra in [('P','task.txt'),('J','task.json')]:
        assert set(seen[arm])==set(seen['U'])|{extra}
        assert {k:seen[arm][k] for k in seen['U']}==seen['U']
    assert seen['U']['query.txt']==row['question'].encode()
    assert json.loads(seen['J']['task.json'])['threshold']==5
