"""Catches accidental control edits, card-dependent gold leakage and wrong collector entry."""
import asyncio
import json
from pathlib import Path
import sys

def study():
    assert Path(__file__).with_name('ph_study.py').exists(),'procedural-card task not implemented'
    import ph_study as s
    return s

def test_original_control_and_only_shared_card_treatment():
    s=study()
    context=dict(id='CPU',size=1,index=0,stratum='root_new',native_context_id=983799001,records=[dict(id='q000000000001',user='u0',text='Who wrote it?',weight=3)])
    context['text']=json.dumps(context['records'][0],sort_keys=True)+'\n'
    row=dict(id='CPU-task',operator='threshold_users',target='human being',target_b='entity',question='Across all records, how many users have human being weight strictly greater than 5?')
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,data):self.files[name]=data
    async def files(task):
        memory=Memory();await task.setup(None,memory);return memory.files
    old=s.o.qnative().make_task(context,row['question'],0,row['id']);basefiles=asyncio.run(files(old));card=s.card()
    assert 0<len(s.o.qnative().stack().native.renderer()._tokenizer.encode(card,add_special_tokens=False))<=250
    for arm in ('U','P'):
        task=s.make_task(context,{**row,'card_arm':arm},0);changed=s.make_task(context,{**row,'card_arm':arm,'gold':999,'labels':{'secret':'entity'}},999)
        assert asyncio.run(files(task))==asyncio.run(files(changed))==basefiles
        assert task.data.prompt==old.data.prompt+('' if arm=='U' else '\n\n'+card)
        assert s.o.qnative().first_prefix(task)==s.o.qnative().first_prefix(changed)
        if arm=='U':assert s.o.qnative().first_prefix(task)==s.o.qnative().first_prefix(old)

def test_exact_owner_collector_main(monkeypatch):
    s=study()
    assert Path(__file__).with_name('ph_owner.py').exists(),'bounded48 owner missing'
    import ph_owner as o
    import ph_collect as c
    argv=o.collector_argv(Path('/CPU/service-sft24'),Path('/CPU/sft24/free'),123.)
    module=c.implementation();args=module.parse_args(argv[2:])
    assert (args.mode,args.plan,args.start,args.stop)==('free','FREE_PLAN.json',0,48)
    async def run(args):
        import od_study,od_binding
        assert od_study is s and od_binding is s and args.output==Path('/CPU/sft24/free')
    monkeypatch.setattr(module,'run',run);monkeypatch.setattr(sys,'argv',argv[1:]);c.main()
