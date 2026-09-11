"""Unchanged QSR coding role/native tools with source-file and request authentication."""
import contextlib
import contextvars
import dataclasses
import functools
import hashlib
import json
import sys
import time
import study as s
import protocol as p

@functools.lru_cache(maxsize=1)
def role():return s.load('warm_reference_role',s.SIDE/'leaf-role-routing-v1/source/routing.py','8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f')
def task(context,query,row):
    old=s.qnative();result=old.make_task(context,query,0,row['id'])
    original_type=type(result)
    class DiagnosticTask(original_type):
        async def setup(self,trace,runtime):
            await super().setup(trace,runtime)
            expected={'records.json':json.dumps(context['records'],ensure_ascii=False),'context.txt':context['text'],'query.txt':query}
            actual={}
            for name,value in expected.items():
                raw=await runtime.read(name,max_bytes=2*1024*1024)
                if raw!=value.encode():raise ValueError('public file bytes differ: '+name)
                actual[name]=hashlib.sha256(raw).hexdigest()
            trace.info['warm_reference_setup']=dict(file_sha256=actual,root=row['root'],no_gold=True)
    result.__class__=DiagnosticTask
    result.plain_query=query;return result
def expected(task,row):
    template=s.read(s.SIDE/'root-corrective-reduction-sft-v1/inputs/NATIVE_TEMPLATE.json')
    system=template['system']
    messages=[system,dict(role='user',content=task.data.prompt)];tools=json.loads(template['tools_ordered_json'])
    tokens=s.qnative().stack().native.renderer().render(messages,tools=tools,add_generation_prompt=True).token_ids
    if len(tokens)+2048>8192:raise ValueError('first-prefix context/output budget')
    return dict(messages=messages,tools_ordered_json=template['tools_ordered_json'],token_ids=tokens)
def environment_config(interface):
    value=interface.e.environment_config();value['agent']['timeout'].update(setup=45.,rollout=120.,finalize=15.,scoring=15.)
    value['timeout']['episode']=120.;return value
def interface(output):
    value=s.qnative().interface(output)
    sys.path.insert(0,str(s.ROOT));return value
def make_context(interface,endpoint,row):
    value=interface.e.make_context(endpoint,row)
    return dataclasses.replace(value,sampling=value.sampling.model_copy(update={'max_tokens':2048}))
@contextlib.contextmanager
def installed(interface,binding,output,plan,public,expectations):
    from verifiers.v1.clients.train import TrainClient
    rows={r['id']:r for r in plan}
    with interface.installed(binding,output,plan,public):
        routed_get=TrainClient.get_response;active=contextvars.ContextVar('warm_reference_request',default=None);clients=[];first=set()
        async def wire(request):
            record=active.get()
            if record is None or request.url.path!='/inference/v1/generate':return
            body=json.loads(request.content)
            record['native_wire_request']=dict(body=body,url=str(request.url))
            row=record['coordinate']
            if record['depth']==0 and body['sampling_params'].get('max_tokens')!=2048:raise ValueError('actual root action cap differs from2048')
            if record['depth']==0 and row['id'] not in first:
                expected=expectations[row['id']]
                if record['native_request']['messages']!=expected['messages'] or json.dumps(record['native_request'].get('tools'),separators=(',',':'))!=json.dumps(json.loads(expected['tools_ordered_json']),separators=(',',':')) or body['token_ids']!=expected['token_ids']:raise ValueError('first actual native messages/tools/tokens differ')
                first.add(row['id']);record['first_prefix_verified']=True
            record['physical_request_attempt']=True
            s.write(output/'physical-requests'/(record['request_id']+'.json'),record)
        async def response_wire(response):
            record=active.get()
            if record is None or response.request.url.path!='/inference/v1/generate':return
            await response.aread();record['native_wire_response']=dict(http_status=response.status_code,body=response.text)
        async def get(self,dialect,body,sampling,session_id=None,turn=None,headers=None):
            row=rows[self.config.headers[interface.e.HEADER]]
            meta=role().route(json.loads(json.dumps(body)),headers,binding['fixed_child'],binding['role_map'])
            record=dict(coordinate=row,**meta,native_request=json.loads(json.dumps(body)),status='requested',physical_request_attempt=False,started_epoch=time.time())
            s.write(output/'audit'/(record['request_id']+'-request.json'),record)
            token=active.set(record);client=self.client._client
            if client not in clients:client.event_hooks['request'].append(wire);client.event_hooks['response'].append(response_wire);clients.append(client)
            try:
                response=await routed_get(self,dialect,body,sampling,session_id=session_id,turn=turn,headers=headers)
                record.update(native_response=response.model_dump(mode='json'),status='returned');return response
            except BaseException as error:record.update(status='error',pretransport_rejected=not record['physical_request_attempt'],error=dict(type=type(error).__name__,message=str(error)));raise
            finally:
                record['ended_epoch']=time.time();s.write(output/'audit'/(record['request_id']+'-result.json'),record);active.reset(token)
        TrainClient.get_response=get
        try:yield
        finally:
            TrainClient.get_response=routed_get
            for client in clients:client.event_hooks['request'].remove(wire);client.event_hooks['response'].remove(response_wire)
