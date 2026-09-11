"""Null-aware strict endpoint and explicit48-logical/40-physical projections."""
import ast
import collections
import json
import re
from pathlib import Path


def episode_metrics(raw,seconds):
    traces=raw.get('traces') or []
    completed=bool(traces) and all(t.get('is_completed',False) for t in traces)
    reply=traces[0].get('root_reply') if len(traces)==1 else None
    match=re.fullmatch(r'Answer: ([0-9]+)',reply.strip()) if isinstance(reply,str) else None
    strict=None
    if completed and isinstance(reply,str) and reply.strip():
        strict=0
        if match:
            answer=traces[0]['task']['data']['answer']
            gold=ast.literal_eval(answer)
            if isinstance(gold,list):gold=gold[0]
            strict=int(int(match.group(1))==int(gold))
    operator=[]
    for trace in traces:
        payload=trace.get('info',{}).get('operator_transcript',{}).get('raw')
        if payload:operator.append(json.loads(payload))
    return {'execution_completed':completed,'strict_reward':strict,'root_reply':reply,
        'terminal_schema_valid':bool(match) if reply else None,
        'inherited_raw_rewards':[t.get('rewards') for t in traces],
        'wall_seconds':seconds,'operator_transcripts':operator,
        'model_calls':sum(len(t.get('calls',[])) for t in traces),
        'failure_kind':next((x['status'] for x in operator if x['status']!='complete'),
            'infrastructure_or_incomplete' if not completed else 'unanswered' if strict is None else None)}


def summarize(records,plan):
    from experiment import c,ROOT
    by_id={r['coordinate']['id']:r for r in records}
    if len(by_id)!=len(records):raise ValueError('duplicate execution')
    refs=c.read(ROOT/'inputs/LOGICAL_CELLS.json')
    cells=[]
    for family in ('user','global'):
        for method in ('all16','filter16','free'):
            selected=[r for r in refs if r['family']==family and r['method']==method]
            values=[by_id.get(r['execution_id'],{}).get('derived',{}) for r in selected]
            cells.append({'family':family,'method':method,'planned':len(selected),
                'recorded':sum(r['execution_id'] in by_id for r in selected),
                'observable':sum(v.get('strict_reward') is not None for v in values),
                'correct':sum(v.get('strict_reward')==1 for v in values),
                'null_or_unstarted':sum(v.get('strict_reward') is None for v in values),
                'logical_execution_ids':[r['execution_id'] for r in selected]})
    return {'planned':len(plan),'logical_cells':len(refs),'recorded':len(records),'cells':cells,
        'unrun_coordinates':[r['id'] for r in plan if r['id'] not in by_id],
        'physical_episode_wall_seconds':sum(r['derived']['wall_seconds'] for r in records),
        'caution':'Eight global fixed executions shared by two method references; never48 independent observations. User constant2=6/8 exposed descriptive baseline; zero child calls is not adaptation proof.'}


def analyze(output):
    import experiment as e
    c=e.c
    output=Path(output)
    records=e.capture.q.CheckpointStore(output/'rollout').records()
    spec=c.read(e.ROOT/'SPEC.json');report=summarize(records,spec['plan'])
    audit_directory=output/'rollout-routing/role-audit'
    audits=[c.read(p) for p in audit_directory.glob('*-result.json')]
    seen={a.get('request_id') for a in audits}
    for path in audit_directory.glob('*-request.json'):
        request=c.read(path)
        if request.get('request_id') not in seen:
            audits.append({**request,'status':'request_only_unconfirmed_wire','ended':None})
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(Path(c.pilot_recipe()['base_model'])/'tokenizer.json'))
    costs=[]
    for a in audits:
        wire=a.get('native_wire_request',{}).get('body') or {}
        response=a.get('native_wire_response') or {}
        if a.get('status')=='returned':
            native=a['native_response'];usage=native.get('usage') or {}
        else:usage={}
        costs.append({'request_id':a.get('request_id'),'depth':a.get('depth'),'invocation':a.get('invocation'),
            'status':a.get('status'),'http_status':response.get('http_status'),
            'physical_prompt_tokens':len(wire['token_ids']) if 'token_ids' in wire else None,
            'usage':usage,'error':a.get('error'),'seconds':a['ended']-a['started'] if a['ended'] is not None else None,
            'uncached_input_tokens':usage['prompt_tokens']-usage['cached_input_tokens']
                if usage.get('prompt_tokens') is not None and usage.get('cached_input_tokens') is not None else None,
            'physical_token_ids':wire.get('token_ids'),'sampling':wire.get('sampling_params'),
            'rendered_prompt':tokenizer.decode(wire['token_ids'],skip_special_tokens=False) if 'token_ids' in wire else None,
            'native_answer':a.get('native_response',{}).get('message',{}).get('content'),
            'native_finish_reason':a.get('native_response',{}).get('finish_reason')})
    report['physical_native_requests']=costs
    report['physical_request_count']=sum(a['physical_token_ids'] is not None for a in costs)
    report['attempt_record_count']=len(costs)
    report['unconfirmed_request_only_records']=sum(a['status']=='request_only_unconfirmed_wire' for a in costs)
    report['root_child_request_counts']=dict(collections.Counter(str(a['depth']) for a in costs))
    report['usage_by_depth']={str(depth):{key:{'known_sum':sum(r['usage'][key] for r in costs if r['depth']==depth and r['usage'].get(key) is not None),
        'unknown_calls':sum(r['usage'].get(key) is None for r in costs if r['depth']==depth)}
        for key in ('prompt_tokens','cached_input_tokens','completion_tokens')} for depth in (0,1)}
    report['episode_physical_linkage']=[]
    for record in records:
        ids={call['acp']['request_id'] for trace in record['episode'].get('traces',[]) for call in trace.get('calls',[])}
        linked=[x for x in costs if x['request_id'] in ids]
        root_messages=[]
        for trace in record['episode'].get('traces',[]):
            seen=set()
            for call in trace.get('calls',[]):
                if call['model']!=spec['binding']['role_map']['root']:continue
                index=call['node']
                while type(index) is int and 0<=index<len(trace['nodes']) and index not in seen:
                    seen.add(index);node=trace['nodes'][index]
                    if node.get('message',{}).get('role') in ('assistant','tool'):
                        root_messages.append({'node':index,'message':node['message']})
                    index=node.get('parent')
        report['episode_physical_linkage'].append({'execution_id':record['coordinate']['id'],
            'request_ids':sorted(ids),'matched_native_requests':len(linked),
            'root_messages_and_observed_tool_outputs':root_messages,
            'operator_transcripts':record['derived'].get('operator_transcripts',[]),
            'caveat':'Runtime-writable operator transcript is corroborable against native prompts/answers; direct root semantic inspection and silent coverage remain unobservable.'})
    report['paired']=[{'block':block,'family':family,'outcomes':{
        ref['method']:next((r['derived']['strict_reward'] for r in records if r['coordinate']['id']==ref['execution_id']),None)
        for ref in c.read(e.ROOT/'inputs/LOGICAL_CELLS.json') if ref['block']==block and ref['family']==family}}
        for block in range(8) for family in ('user','global')]
    c.write_once(output/'INDEPENDENT_PROJECTION.json',report)
    return report
