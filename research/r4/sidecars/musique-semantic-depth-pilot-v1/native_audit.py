"""Request-local native wire capture and hard all-depth physical-call admission."""
from collections import Counter
import contextlib
import contextvars
import copy
import itertools
import json
import time
import musique_study as s


@contextlib.contextmanager
def capture(directory,coordinates):
    from verifiers.v1.clients.train import TrainClient
    from verifiers.v1.errors import ProviderError
    original=TrainClient.get_response
    active=contextvars.ContextVar('musique_native_call',default=None)
    by_id={row['id']:row for row in coordinates}; reservations=Counter(); clients=[]; rows=[]
    indices=itertools.count(); recorder=s.recorder()

    async def request_hook(request):
        record=active.get()
        if record is None or request.url.path!='/inference/v1/generate':return
        text=request.content.decode('utf-8'); body=json.loads(text)
        if record.get('wire_request_text') is not None:raise ValueError('unexpected native retry')
        params=body['sampling_params']
        if body['model']!=s.MODEL_ALIAS or params['max_tokens']!=1024 or params['temperature']!=.5:
            raise ValueError('actual native policy/cap changed')
        if params.get('structured_outputs') is not None:raise ValueError('unexpected restrictive tool grammar')
        record['actual_prompt_tokens']=len(body['token_ids'])
        record['actual_prompt_plus_output_cap']=len(body['token_ids'])+1024
        if record['actual_prompt_plus_output_cap']>8192:
            record.update(status='refused',refusal='musique_context_cap',physical_forward_started=False)
            trace=active.get().get('_trace')
            if trace is not None:trace.stop('max_input_tokens')
            raise ProviderError('musique_context_cap: actual prompt + 1024 exceeds 8192')
        record.update(wire_request_text=text,wire_request_sha256=s.digest(body),
                      physical_forward_started=True,wire_started_epoch=time.time())
        s.write_x(directory/(record['stem']+'-wire-request.json'),
                  {'index':record['index'],'coordinate_id':record['coordinate_id'],
                   'session_id':record['session_id'],'request_text':text,'body_sha256':s.digest(body),
                   'url_path':request.url.path,'started_epoch':record['wire_started_epoch']})

    async def response_hook(response):
        record=active.get()
        if record is None or response.request.url.path!='/inference/v1/generate':return
        payload=await response.aread();text=payload.decode('utf-8')
        record.update(wire_response_text=text,wire_status_code=response.status_code,
                      wire_ended_epoch=time.time())
        s.write_x(directory/(record['stem']+'-wire-response.json'),
                  {'index':record['index'],'coordinate_id':record['coordinate_id'],
                   'session_id':record['session_id'],'response_text':text,
                   'http_status':response.status_code,'ended_epoch':record['wire_ended_epoch']})

    async def get(client,dialect,body,sampling,session_id=None,turn=None,headers=None):
        coordinate_id=client.config.headers.get(s.HEADER)
        if coordinate_id not in by_id:raise ValueError('missing study-owned coordinate header')
        coordinate=by_id[coordinate_id];index=next(indices);stem=f'{index:04d}'
        record={'index':index,'stem':stem,'coordinate_id':coordinate_id,'coordinate':coordinate,
                'session_id':session_id,'model':body.get('model'),'started_epoch':time.time(),
                'body':copy.deepcopy(body),'sampling':sampling.model_dump(mode='json'),
                'turn':recorder.pending_turn_metadata(turn),'status':'started','physical_forward_started':False}
        rows.append(record);s.write_x(directory/(stem+'-start.json'),record)
        trace=turn.trace if turn is not None else None
        token=active.set(record);record['_trace']=trace
        try:
            if body.get('model')!=s.MODEL_ALIAS:raise ValueError('non-base root/child alias')
            limit=1 if coordinate['arm']=='question_only' else 6
            # Synchronous admission before any await: concurrent child requests share one
            # coordinate, including inflight actions, unlike completed-turn framework limits.
            if reservations[coordinate_id]>=limit:
                record.update(status='refused',refusal='musique_physical_call_cap')
                if trace is not None:trace.stop('max_turns')
                raise ProviderError('musique_physical_call_cap: no seventh physical request',status_code=400)
            reservations[coordinate_id]+=1
            record['reservation_ordinal']=reservations[coordinate_id]
            http=client.client._client
            if http not in clients:
                http.event_hooks['request'].append(request_hook);http.event_hooks['response'].append(response_hook);clients.append(http)
            response=await original(client,dialect,body,sampling,session_id=session_id,turn=turn,headers=headers)
            payload=response.model_dump(mode='json');evidence=recorder.validate_native_response(payload)
            wire=json.loads(record['wire_response_text'])
            if response.model!=s.MODEL_ALIAS or record['wire_status_code']!=200:
                raise ValueError('native response model/status changed')
            if wire['choices'][0]['token_ids']!=payload['tokens']['completion_ids']:
                raise ValueError('raw/typed completion IDs differ')
            if evidence['action_tokens']>1024:raise ValueError('native output exceeded cap')
            record.update(status='returned',response=payload,evidence=evidence,finish_reason=response.finish_reason)
            return response
        except BaseException as error:
            if record['status']!='refused':record['status']='error'
            record['error']={'type':type(error).__name__,'message':str(error)}
            if record['status']=='refused':
                # The SDK wraps exceptions from request hooks as Connection error.
                # Preserve that original error in the receipt, but restore our own
                # authenticated pre-transport refusal at the typed boundary.
                raise ProviderError(record['refusal']+': authenticated pre-transport refusal',status_code=400) from error
            raise
        finally:
            record.pop('_trace',None);record['ended_epoch']=time.time()
            record['wall_seconds']=record['ended_epoch']-record['started_epoch']
            s.write_x(directory/(stem+'-result.json'),record);active.reset(token)

    TrainClient.get_response=get
    try:yield rows
    finally:
        TrainClient.get_response=original
        for http in clients:
            http.event_hooks['request'].remove(request_hook);http.event_hooks['response'].remove(response_hook)
