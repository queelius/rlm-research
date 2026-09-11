import asyncio
import importlib
import json
from types import SimpleNamespace
import sm_study as s
import sm_protocol as p

def test_actual_setup_all_files_equal_and_query_never_inline():
    n=importlib.import_module('sm_native');values=p.build();context=values['PUBLIC.json'][0];pair=values['PLAN.json'][:2]
    query=values['QUERIES.json'][pair[0]['task_name']]['question'];raw=json.dumps({r['id']:'entity' for r in context['records']},indent=2)
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,value):self.files[name]=value
        async def read(self,name,**kwargs):return self.files[name]
    async def setup(task):
        m=Memory();trace=SimpleNamespace(info={});await task.setup(trace,m);return m.files,trace.info
    tasks=[n.task(context,query,row,raw) for row in pair];files=[asyncio.run(setup(t))[0] for t in tasks]
    assert files[0]==files[1] and files[0]['query.txt']==query.encode() and files[0]['labels.json']==raw.encode()
    assert 'sitecustomize.py' not in files[0] # no compact-role override in this study
    assert tasks[0].plain_query==tasks[1].plain_query==query
    assert tasks[0].data.prompt==tasks[1].data.prompt+'\n\n'+raw
    assert n.expected(tasks[0],pair[0])['messages'][0]==n.expected(tasks[1],pair[1])['messages'][0]

def test_actual_source_grammar_ids_and_only_public_id_text():
    c=importlib.import_module('sm_collect');values=p.build();context=values['PUBLIC.json'][0];row=values['ACQUISITION_PLAN.json'][0]
    body=c.extraction_request(context,row,s.binding());schema=body['structured_outputs']['json']
    assert schema['required']==[r['id'] for r in context['records']] and len(schema['properties'])==16
    rows=json.loads(body['messages'][1]['content'].split('\nRecords: ')[1]);assert all(set(r)=={'id','text'} for r in rows)
    assert body['max_tokens']==1536 and all(v['enum']==list(s.contract().LABELS) for v in schema['properties'].values())
