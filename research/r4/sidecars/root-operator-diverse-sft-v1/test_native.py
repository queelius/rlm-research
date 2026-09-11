import asyncio
import importlib
import json
from pathlib import Path
import pytest

def test_binding_choice_is_required_before_ready(tmp_path):
    s=importlib.import_module('od_study')
    with pytest.raises(FileNotFoundError):s.starting_policy(tmp_path/'missing.json')

def test_native_task_truth_and_four_field_typed_catalog():
    s=importlib.import_module('od_study');p=importlib.import_module('od_protocol');plans=p.build(s.source_inputs());row=plans['TRAIN_PLAN.json'][0];context=plans['PUBLIC.json'][0];n=s.qnative()
    task=n.make_task(context,row['question'],0,row['id']);changed=n.make_task(context,row['question'],999,row['id'])
    assert n.first_prefix(task)==n.first_prefix(changed)
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,value):self.files[name]=value
    async def setup(t):
        m=Memory();await t.setup(None,m);return m.files
    files=asyncio.run(setup(task));assert files==asyncio.run(setup(changed))
    assert json.loads(files['records.json'])==context['records'];assert files['query.txt']==row['question'].encode()
    assert 'HOST_GOLD.json' not in files
    contract=n.stack().interface.hooks.contract;batch=context['records'][:4];request=contract.batch.request_for(batch)
    assert json.loads(request.split('\nRecords: ')[1])==[{'id':x['id'],'text':x['text']} for x in batch]
    catalog=n.stack().interface.catalogs({context['id']:context})[str(context['native_context_id'])]
    matched=contract.match_request(request,catalog);assert matched['matched'] and list(matched['schema']['properties'])==[x['id'] for x in batch]
    labels={x['id']:'entity' for x in batch};assert contract.batch.strict_map(json.dumps(labels),list(labels))==labels
