"""CPU readout only: observed costs, strict answers and uncollapsed failure states."""
import collections
import re
from pathlib import Path
import experiment as e
import runtime as r


def ancestry(nodes,index):
    found=[]
    while index is not None:
        found.append(nodes[index])
        index=nodes[index].get('parent')
    return list(reversed(found))


def episode_record(record,audits):
    raw=record['episode']
    metrics=e.capture.native.episode_metrics(raw,record['timing']['wall_seconds'])
    calls=[]
    for trace in raw.get('traces',[]):
        for call in trace.get('calls',[]):
            rid=(call.get('acp') or {}).get('request_id')
            audit=audits.get(rid)
            if audit is None:
                calls.append({'request_id':rid,'audit_missing':True})
                continue
            wire=(audit.get('native_wire_request') or {}).get('body') or {}
            tokens=(audit.get('native_response') or {}).get('tokens') or {}
            index=call.get('node')
            nodes=ancestry(trace['nodes'],index) if isinstance(index,int) else []
            messages=[n.get('message') or {} for n in nodes]
            users=[m.get('content') for m in messages if m.get('role')=='user']
            system=next((m.get('content') for m in messages if m.get('role')=='system'),None)
            message=messages[-1] if messages else {}
            calls.append({'request_id':rid,'audit_path':audit['_path'],'audit_sha256':audit['_sha'],
                'invocation':audit.get('invocation'),'depth':audit.get('depth'),'model':call.get('model'),
                'model_sha256':audit.get('model_sha256'),'kind':audit.get('kind'),
                'dispatch_attempted':audit.get('dispatch_attempted'),
                'dispatch_prevented':audit.get('dispatch_prevented',False),
                'sampling':call.get('sampling'),'status':audit.get('status'),
                'http_status':(audit.get('native_wire_response') or {}).get('http_status'),
                'error':audit.get('error'),'usage':call.get('usage'),
                'physical_prompt_ids_sha256':r.digest(wire.get('token_ids')),
                'attempted_prompt_tokens':len(wire['token_ids']) if 'token_ids' in wire else None,
                'sampled_completion_tokens':len(tokens['completion_ids']) if 'completion_ids' in tokens else None,
                'physical_graph_matches':(tokens.get('prompt_ids')==wire.get('token_ids')) if tokens else None,
                'tool_request_count':len(message.get('tool_calls') or []),
                'sampled_empty_content':not message.get('content') and not message.get('tool_calls') if tokens else None,
                'message':message,'initial_user':users[0] if users else None,
                'initial_user_sha256':r.digest(users[0]) if users else None,
                'system_sha256':r.digest(system) if system is not None else None,
                'system_has_suffix':r.SUFFIX in system if isinstance(system,str) else None,
                'tool_observations_on_causal_prefix':[m for m in messages if m.get('role')=='tool'],
                'semantic_parents':trace['nodes'][index].get('semantic_parents',[]) if isinstance(index,int) else []})
    errors=[c for c in calls if c.get('status')=='error' and not c.get('dispatch_prevented')]
    normalized={'ok':metrics['execution_completed'],'reward':metrics['strict_reward'],
        'answer':(raw.get('traces') or [{}])[-1].get('root_reply')}
    state=r.outcome_state(normalized,record.get('budget_censored',False),bool(errors))
    invocations=[]
    by_inv=collections.defaultdict(list)
    for call in calls:
        if call.get('invocation'): by_inv[call['invocation']].append(call)
    for invocation,rows in by_inv.items():
        user=next((c['initial_user'] for c in rows if c.get('initial_user') is not None),None)
        conflict=isinstance(user,str) and bool(re.search(r'(?:write|return|provide|generate).{0,50}(?:python|code|script)|(?:return|compute|give).{0,35}(?:count|total|aggregate)',user[:500],re.I|re.S))
        invocations.append({'invocation':invocation,'depth':rows[0]['depth'],'model_calls':len(rows),
            'tool_request_turns':sum(c['tool_request_count']>0 for c in rows),
            'initial_prompt_tokens':rows[0]['attempted_prompt_tokens'],'last_prompt_tokens':rows[-1]['attempted_prompt_tokens'],
            'initial_user':user,'initial_user_sha256':r.digest(user) if user is not None else None,
            'possible_suffix_code_or_aggregate_conflict_needs_review':conflict,
            'conflict_rule':'lexical screen on first500 user chars, not semantic adjudication',
            'tool_observations':rows[-1]['tool_observations_on_causal_prefix'],
            'request_ids':[c['request_id'] for c in rows]})
    return {'coordinate':record['coordinate'],'timing':record['timing'],**state,
        'strict_terminal_valid':metrics['strict_terminal_valid'],'strict_correct':metrics['strict_correct'],
        'historical_capture_mask_valid':metrics['trace_trainable'],'rlvr_admission':'not evaluated; inference-only, no export',
        'trace_errors':[t.get('errors',[]) for t in raw.get('traces',[])],
        'episode_errors':raw.get('errors',[]),'calls':calls,'invocations':invocations,
        'root_calls':sum(c.get('depth')==0 for c in calls),'child_calls':sum(c.get('depth')==1 for c in calls),
        'physical_dispatch_attempts':sum(c.get('dispatch_attempted') is True for c in calls),
        'attempted_prompt_tokens_known_sum':sum(c.get('attempted_prompt_tokens') or 0 for c in calls if c.get('dispatch_attempted')),
        'sampled_completion_tokens_known_sum':sum(c.get('sampled_completion_tokens') or 0 for c in calls),
        'missing_usage_calls':sum(c.get('usage') is None for c in calls),
        'cache_measurement_missing_calls':sum((c.get('usage') or {}).get('cached_input_tokens') is None for c in calls)}


def analyze(output):
    output=Path(output)
    rollout=output/'rollout'
    audit=output/'rollout-routing'
    sources={}
    audits={}
    for p in (audit/'role-audit').glob('*-result.json'):
        value=r.read(p)
        sources[str(p)]=r.file_hash(p)
        rid=value.get('request_id')
        if rid in audits: raise ValueError('duplicate request audit identity')
        audits[rid]={**value,'_path':str(p),'_sha':sources[str(p)]}
    records=e.q.CheckpointStore(rollout).records()
    for p in (rollout/'episodes').glob('*.json'): sources[str(p)]=r.file_hash(p)
    for p in (output/'CAPTURE_SPEC.json',output/'TERMINAL.json',audit/'DISPATCH_STATUS.json'):
        if p.exists(): sources[str(p)]=r.file_hash(p)
    rows=[episode_record(record,audits) for record in records]
    by_coordinate={row['coordinate']['id']:row for row in rows}
    plan=r.read(ROOT/'SPEC.json')['plan']
    pairs=[]
    for i in range(0,len(plan),2):
        pair=[by_coordinate.get(p['id']) for p in plan[i:i+2]]
        entry={'pair_id':plan[i]['pair_id'],'complete_records':all(pair),'arms':{}}
        for p,row in zip(plan[i:i+2],pair,strict=True):
            entry['arms'][p['arm']]=None if row is None else {k:row[k] for k in (
                'observable_reward','budget_censored','empty_final','root_calls','child_calls',
                'physical_dispatch_attempts','attempted_prompt_tokens_known_sum','sampled_completion_tokens_known_sum')}
        if all(pair):
            initial=[[c for c in row['calls'] if c.get('depth')==0] for row in pair]
            entry['initial_root_physical_ids_equal']=bool(all(initial)) and initial[0][0]['physical_prompt_ids_sha256']==initial[1][0]['physical_prompt_ids_sha256']
            children=[[v['initial_user_sha256'] for v in row['invocations'] if v['depth']==1] for row in pair]
            entry['matched_child_dispatch_prefix']=next((j for j,(a,b) in enumerate(zip(*children)) if a!=b),min(map(len,children)))
            entry['child_trajectory_pairing_claim']=False
        pairs.append(entry)
    attributed={call['request_id'] for row in rows for call in row['calls']}
    value={'planned':16,'recorded':len(rows),'unrun_or_no_record':[p for p in plan if p['id'] not in by_coordinate],
        'episodes':rows,'pairs':pairs,'unattributed_audits':[v for k,v in audits.items() if k not in attributed],
        'limitations':['Failure-enriched exposed groups; fresh seeds do not remove regression-to-mean.',
            'Request conflict flag requires manual review; no child payload repair.',
            'Partial/unattributed audit cost retained, not assigned to a fabricated outcome.',
            'No learning/general-RLM-gain or paired adaptive child-trajectory claim.'],
        'source_sha256':sources}
    r.write_once(output/'READOUT.json',value)
    return value


ROOT=e.ROOT
