"""Breaks caught: altered common source/prompt, absent loader, root cap drift."""
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
import cl_study as s
import cl_protocol as p

def test_actual_setup_common_files_and_treatment_only_plain_loader():
    assert Path(__file__).with_name('cl_native.py').exists(), 'native loader setup not implemented'
    import cl_native as n
    values=p.build();context=values['PUBLIC.json'][0];pair=values['PLAN.json'][:2]
    query=values['QUERIES.json'][pair[0]['task_name']]['question']
    raw=next(e['record']['map']['raw'] for e in values['REUSED_SOURCES.json'] if e['coordinate']['context_id']==context['id'])
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,value):self.files[name]=value
        async def read(self,name,**kwargs):return self.files[name]
    async def setup(task):
        memory=Memory();trace=SimpleNamespace(info={});await task.setup(trace,memory);return memory.files,trace.info
    tasks=[n.task(context,query,row,raw) for row in pair];prepared=[asyncio.run(setup(task)) for task in tasks]
    files=[x[0] for x in prepared]
    assert 'source_state.py' not in files[0] and 'source_state.py' in files[1]
    assert files[0]=={k:v for k,v in files[1].items() if k!='source_state.py'}
    assert files[0]['labels.json']==raw.encode() and files[0]['query.txt']==query.encode()
    namespace={};exec(compile(files[1]['source_state.py'],'AUTHORED_SETUP_MODULE','exec'),namespace)
    assert namespace['load']()=={'records':context['records'],'predictions':json.loads(raw)}
    assert tasks[0].data.prompt==p.old.prompt(context,query,raw,'FILE')
    assert tasks[1].data.prompt==tasks[0].data.prompt+'\n\n'+p.API_DESCRIPTION
    assert tasks[0].data.source_split==tasks[1].data.source_split=='QSR-research-operator-SFT-child-training-exposed'
    expected=[n.expected(task,row) for task,row in zip(tasks,pair)]
    assert expected[0]['messages'][0]==expected[1]['messages'][0] and expected[0]['tools_ordered_json']==expected[1]['tools_ordered_json']
    assert all(len(v['token_ids'])+2048<=8192 for v in expected)
