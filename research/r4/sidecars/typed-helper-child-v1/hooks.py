"""Study-owned request-local sampling delta over unchanged native role capture."""
import contextlib
import contextvars
import copy
import json
import os
import time
import experiment as e
import contract
role=e.checked_import('typed_exact_role',e.ROOT.parent/'leaf-role-routing-v1/source/routing.py','8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f')

@contextlib.contextmanager
def installed(binding,output,plan,catalogs):
    from verifiers.v1.clients.train import TrainClient
    from verifiers.v1.runtimes.docker import DockerRuntime
    rows={r['id']:r for r in plan};decisions=contract.Decisions();clients=[]
    active=contextvars.ContextVar('typed_request_local',default=None)
    old_runtime=DockerRuntime.run
    async def timed_runtime(self,argv,env):
        started=time.time()
        result=await old_runtime(self,argv,env)
        e.c.write_once(output/'runtime-times'/f'{time.time_ns()}.json',{'runtime':self.name,'argv':argv,
            'started_epoch':started,'ended_epoch':time.time(),'exit_code':result.exit_code})
        return result
    async def wire(request):
        record=active.get()
        if record is None or request.url.path!='/inference/v1/generate': return
        body=json.loads(request.content);actual=body['sampling_params'].get('structured_outputs')
        expected={'json':record['decision']['schema']} if record['decision']['apply'] else None
        if actual!=expected or (actual is not None and contract.encoded(actual['json'])!=record['decision']['schema_ordered_json']):
            raise ValueError('actual native grammar differs from invocation decision')
        if body['model']!=record['actual_alias']: raise ValueError('typed wire alias drift')
        record['wire_schema_verified']=True
        record['native_wire_request']={'body':body,'url':str(request.url)}
    # Native helper is imported by the frozen capture closure, not a second routing implementation.
    with e.capture.installed_hooks(binding,output):
        routed_get=TrainClient.get_response
        async def get(self,dialect,body,sampling,session_id=None,turn=None,headers=None):
            coordinate=self.config.headers.get(e.HEADER)
            if coordinate not in rows: raise ValueError('missing host-owned coordinate metadata')
            row=rows[coordinate]
            meta=role.route(copy.deepcopy(body),headers,binding['fixed_child'],binding['role_map'])
            decision=decisions.choose(coordinate,row['arm'],meta,body.get('messages',[]),catalogs[str(row['context_window_id'])])
            if sampling.wire_args().get('structured_outputs') is not None: raise ValueError('unexpected original grammar')
            actual=sampling.model_copy(deep=True)
            if decision['apply']: actual=actual.model_copy(update={'structured_outputs':{'json':copy.deepcopy(decision['schema'])}})
            record={'coordinate':row,'session_id':session_id,**meta,'decision':decision,'started_epoch':time.time(),
                    'original_sampling':sampling.model_dump(mode='json',exclude_none=True),
                    'effective_sampling':actual.model_dump(mode='json',exclude_none=True)}
            token=active.set(record);client=self.client._client
            if client not in clients: client.event_hooks['request'].append(wire);clients.append(client)
            e.c.write_once(output/'typed-audit'/f"{meta['request_id']}-request.json",record)
            try:
                response=await routed_get(self,dialect,body,actual,session_id=session_id,turn=turn,headers=headers)
                record['response']=response.model_dump(mode='json');record['status']='returned'
                return response
            except BaseException as error:
                record.update(status='error',error={'type':type(error).__name__,'message':str(error)});raise
            finally:
                record['ended_epoch']=time.time()
                e.c.write_once(output/'typed-audit'/f"{meta['request_id']}-result.json",record);active.reset(token)
        TrainClient.get_response=get;DockerRuntime.run=timed_runtime
        try: yield
        finally:
            TrainClient.get_response=routed_get;DockerRuntime.run=old_runtime
            for client in clients: client.event_hooks['request'].remove(wire)

def configure_runtime():
    proof=e.c.read(e.IMAGE_READY)
    if proof['image_id']!=e.IMAGE: raise ValueError('private image changed')
    e.capture.q.ROOTLESS=e.IMAGE_ROOT
    os.environ['PATH']=str(e.IMAGE_ROOT/'bin')+os.pathsep+os.environ['PATH']
    os.environ['VERIFIERS_CACHE_DIR']=str(e.ROOT/'runtime-cache')
