"""Separate operational/null, uptake, strict outcome and physical-corroboration projections."""
import ast
import collections
import json
import sys
from functools import lru_cache
from pathlib import Path
import experiment as e

saved=sys.modules.get('experiment')
sys.modules['experiment']=e.receipt
baseline=e.checked_import('uptake_frozen_results',e.PRIOR/'results.py','4878bf245d105a41e7d008343f8bbaae577832c800cff11964222276c02d012a')
sys.modules['experiment']=saved


def root_observations(episode):
    codes,observations=[],[]
    for trace in episode.get('traces') or []:
        nodes=trace.get('nodes') or []
        index,seen=len(nodes)-1,set()
        while type(index) is int and 0<=index<len(nodes) and index not in seen:
            seen.add(index)
            node=nodes[index]
            message=node.get('message') or {}
            if message.get('role')=='tool': observations.append(message.get('content') or '')
            for tool in message.get('tool_calls') or []:
                function=tool.get('function') or tool
                if function.get('name')!='ipython': continue
                try:
                    args=function.get('arguments')
                    args=json.loads(args) if isinstance(args,str) else args
                    codes.append(args['code'])
                except (ValueError,TypeError,KeyError):
                    codes.append('UNPARSEABLE_TOOL_ARGUMENTS')
            index=node.get('parent')
    return codes,observations


def episode_metrics(episode,seconds):
    result=baseline.episode_metrics(episode,seconds)
    codes,observations=root_observations(episode)
    parsed=[]
    for code in codes:
        try: parsed.append(ast.parse(code))
        except (SyntaxError,TypeError): pass
    calls=[n for tree in parsed for n in ast.walk(tree) if isinstance(n,ast.Call)]
    def named(name):
        return sum(isinstance(n.func,ast.Name) and n.func.id==name for n in calls)
    result['uptake_intent']={'source_records_code_calls':named('source_records'),
        'rlm_records_code_calls':named('rlm_records'),
        'receipt_access_code_calls':sum(isinstance(n.func,ast.Attribute) and n.func.attr=='receipt' for n in calls),
        'mapping_aggregation_code_marker':any('labels_by_id' in code and ('sum(' in code or 'values(' in code) for code in codes),
        'observed_catalog_marker':any('group_id' in text and 'text_sha256' in text for text in observations),
        'observed_example_batch_count_marker':any('example_batch_count' in text for text in observations),
        'observed_KeyError':'KeyError' in str(observations),
        'observed_SyntaxError':'SyntaxError' in str(observations),'root_code':codes,'tool_observations':observations,
        'interpretation':'Code/observation markers only; dispatch and returned-data incorporation require physical corroboration.'}
    return result


def summarize(records,plan):
    planned={r['id']:r for r in plan}
    observed={r['coordinate']['id']:r for r in records}
    if len(observed)!=len(records) or any(r['coordinate']!=planned.get(k) for k,r in observed.items()):
        raise ValueError('duplicate/unplanned coordinate')
    cells=[]
    for weight in ('original','step8'):
        for arm in e.ARMS:
            rows=[r['derived'] for r in records if r['coordinate']['weight']==weight and r['coordinate']['arm']==arm]
            cells.append({'weight':weight,'arm':arm,
                'planned':sum(r['weight']==weight and r['arm']==arm for r in plan),'recorded':len(rows),
                'observable':sum(r['strict_reward'] is not None for r in rows),
                'strict_successes':sum(r['strict_reward']==1 for r in rows),
                'execution_failures':sum(not r.get('execution_completed',False) for r in rows),
                'usage':{key:sum(r.get(key,0) or 0 for r in rows) for key in ('model_calls','completion_tokens','logical_input_tokens','wall_seconds','recursive_subcalls','truncated_calls')},
                'helper_claims':{key:sum(r.get('receipt_diagnostics',{}).get(key,0) for r in rows) for key in ('helper_requests','helper_results','helper_errors','receipt_accesses','valid_receipts')}})
    matches={}
    for row in plan:
        match=matches.setdefault(row['matched_id'],{'matched_id':row['matched_id'],'context_sha256':row['context_sha256'],'task_name':row['task_name'],'seed':row['seed'],'outcomes':{}})
        match['outcomes'][row['weight']+'/'+row['arm']]=observed.get(row['id'],{}).get('derived',{}).get('strict_reward')
    return {'planned':len(plan),'recorded':len(records),'cells':cells,'matched':list(matches.values()),
        'unrun_coordinates':[r['id'] for r in plan if r['id'] not in observed],
        'caution':'Phase projection only. Native-corroborated helper uptake is primary; run analyze after owned GPU release.'}


@lru_cache(maxsize=8)
def role_audits(audit_root):
    values={}
    for path in (Path(audit_root)/'role-audit').glob('*-result.json'):
        value=e.c.read(path)
        request_id=value['request_id']
        if request_id in values: raise ValueError('duplicate actual request identity')
        values[request_id]=value
    return values


def corroborate(episode,audit_root,binding):
    """Native linkage first; root-writable logs remain claims with explicit unknowns."""
    roots,calls=e.native.exporter.episode_turns(episode,Path(audit_root),binding)
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(Path(e.c.pilot_recipe()['base_model'])/'tokenizer.json'))
    actual=[]
    raw_calls=[]
    for trace in episode.get('traces') or []:
        raw_calls.extend(trace.get('calls') or [])
    for call in raw_calls:
        request_id=call['acp']['request_id']
        wire=role_audits(Path(audit_root))[request_id]
        if wire['depth']:
            actual.append({'request_id':request_id,'session_id':wire['session_id'],
                'prompt':tokenizer.decode(wire['native_wire_request']['body']['token_ids'],skip_special_tokens=False),
                'answer':wire['native_response']['message'].get('content'),
                'finish_reason':wire['native_response']['finish_reason']})
    requests,results,accesses={},[],set()
    errors,audit_failures=[],[]
    for trace in episode.get('traces') or []:
        taskdata=trace['task']['data']
        context_sha=e.hashlib.sha256(taskdata['context'].encode()).hexdigest()
        public=e.c.read(e.c.ROOT/'inputs/TRANSFER_PUBLIC.json')
        context=next(r for r in public['contexts'] if r['sha256']==context_sha)
        catalog={'context_sha256':context_sha,'context_id':context['id'],'records':[
            {'id':f'q{i:04d}','text':line,'text_sha256':e.hashlib.sha256(line.encode()).hexdigest(),'group_id':group}
            for i,(line,group) in enumerate(zip(context['text'].splitlines(keepends=True),context['group_ids'],strict=True),1)]}
        log=trace.get('info',{}).get('receipt_audit')
        if not log or log.get('raw') is None:
            audit_failures.append(log)
            continue
        if e.hashlib.sha256(log['raw'].encode()).hexdigest()!=log['sha256']:
            audit_failures.append({'error':'audit byte hash mismatch'})
            continue
        try: events=[json.loads(line) for line in log['raw'].splitlines() if line]
        except (ValueError,TypeError) as error:
            audit_failures.append({'error':str(error)})
            continue
        for event in events:
            if event.get('event')=='helper_request':
                try:
                    ids=[r['id'] for r in event['selected_records']]
                    prompt,source=e.receipt.build_request(catalog,ids,event['query'],event['allowed_values'])
                    verified=all(event.get(k)==v for k,v in source.items())
                    matches=[r for r in actual if prompt in r['prompt']]
                    requests[event['call_id']]={'source_valid':verified,'matches':matches,'ids':ids,'event':event}
                except (ValueError,KeyError,TypeError) as error:
                    requests[event.get('call_id','invalid')]={'source_valid':False,'matches':[],'ids':[],'error':str(error)}
            elif event.get('event')=='helper_result': results.append(event)
            elif event.get('event')=='receipt_access': accesses.add(event['call_id'])
            elif event.get('event')=='helper_error': errors.append(event)
    from receipt_api import parse_receipt
    proof=[]
    for event in results:
        request=requests.get(event['call_id'],{})
        value=event['receipt']
        parsed=parse_receipt(value['raw_answer'],value['requested_ids'],value['allowed_values'])
        matches=[r for r in request.get('matches',[]) if r['answer']==value['raw_answer'] and r['finish_reason']=='stop']
        valid_source=request.get('source_valid',False)
        proof.append({'call_id':event['call_id'],'source_valid':valid_source,'native_request_matches':len(request.get('matches',[])),
            'native_terminal_matches':len(matches),'native_request_ids':[r['request_id'] for r in matches],
            'claimed_session':event.get('session_dir'),'actual_session_ids':[r['session_id'] for r in matches],
            'map_valid':parsed['valid'],'map_report_matches':all(value.get(k)==v for k,v in parsed.items()),
            'strict_map':parsed,'receipt_access_claim':event['call_id'] in accesses,
            'extends_example':bool(set(request.get('ids',[]))-{f'q{i:04d}' for i in range(1,5)}),
            'interpretation':'Helper request text is embedded in the rendered native prompt; answer equality is checked separately. Matches do not prove root-writable receipt consumption or semantic correctness.'})
    dispatched=[r for r in requests.values() if r['source_valid'] and r['matches']]
    native_ids={m['request_id'] for r in dispatched for m in r['matches']}
    helper_signature='Answer the query for each supplied source record. Return only a JSON object '
    uncorroborated_signature=any(helper_signature in r['prompt'] for r in actual) and not dispatched
    return {'native_capture_verified':True,'root_calls':len(roots),'child_calls':len(calls)-len(roots),
        'physical_seeds':sorted({r['sampling']['seed'] for r in calls}),
        'matching_child_model_requests':len(native_ids),'corroborated_helper_request_claims':len(dispatched),
        'helper_uptake':None if uncorroborated_signature else bool(dispatched),
        'turn_count_scope':'root_calls/child_calls count exporter-returned verified turns, not all physical attempts or rlm_records API dispatches.',
        'request_claims_with_ambiguous_call_link':sum(len(r['matches'])>1 for r in dispatched),
        'extends_example':any(set(r['ids'])-{f'q{i:04d}' for i in range(1,5)} for r in dispatched),
        'receipt_access_claims':len(accesses),'helper_errors':errors,'audit_failures':audit_failures,'results':proof,
        'semantic_validation':False,'root_writable_caveat':True}


def analyze(output):
    output=Path(output)
    if not (output/'TERMINAL.json').exists(): raise ValueError('terminal marker required before CPU analysis')
    spec=e.verify()
    records,evidence=[],[]
    for path in sorted(output.glob('phase-*/rollout/episodes/*.json')):
        row=e.c.read(path)
        if e.c.digest(row['episode'])!=row['episode_sha256']: raise ValueError('raw episode changed')
        proof={'path':str(path),'sha256':e.c.file_hash(path),'coordinate':row['coordinate']}
        try:
            proof.update(corroborate(row['episode'],path.parent.parent.with_name('rollout-routing'),spec['bindings'][row['coordinate']['weight']]))
            if proof['physical_seeds']!=[row['coordinate']['seed']]: raise ValueError('native seed mismatch')
        except (ValueError,KeyError,TypeError,AttributeError) as error:
            proof.update(native_capture_verified=False,helper_uptake=None,error={'type':type(error).__name__,'message':str(error)})
        records.append(row)
        evidence.append(proof)
    report=summarize(records,spec['plan'])
    report['episode_evidence']=evidence
    by_id={r['coordinate']['id']:r for r in evidence}
    uptake={}
    for row in spec['plan']:
        uptake.setdefault(row['matched_id'],{})[row['weight']+'/'+row['arm']]=by_id.get(row['id'],{}).get('helper_uptake')
    contrasts={}
    for weight in ('original','step8'):
        values=[]
        for match in uptake.values():
            left,right=match.get(weight+'/restored_raw'),match.get(weight+'/taught_raw')
            if left is not None and right is not None: values.append(int(left)-int(right))
        contrasts[weight]={'observable_matches':len(values),'unknown':12-len(values),'gains':sum(v>0 for v in values),'losses':sum(v<0 for v in values),'ties':values.count(0),'net':sum(values)}
    report['primary_native_helper_uptake_restored_minus_taught_raw']=contrasts
    report['uptake_by_matched_id']=uptake
    interaction=[]
    for match in uptake.values():
        keys=['step8/restored_raw','step8/taught_raw','original/restored_raw','original/taught_raw']
        values=[match.get(k) for k in keys]
        if all(v is not None for v in values):
            interaction.append(int(values[0])-int(values[1])-int(values[2])+int(values[3]))
    report['root_by_procedure_uptake_interaction']={'observable_matches':len(interaction),'unknown':12-len(interaction),
        'sum':sum(interaction),'values':interaction,'caveat':'Descriptive with residual period interactions, not causal mediation.'}
    physical,request_only=[],[]
    for routing in sorted(output.glob('phase-*/rollout-routing')):
        audits=role_audits(routing)
        for request_id,wire in audits.items():
            request=wire.get('native_wire_request',{}).get('body',{})
            response=wire.get('native_wire_response',{})
            try: payload=json.loads(response.get('body','null'))
            except (ValueError,TypeError): payload=None
            choices=payload.get('choices',[]) if isinstance(payload,dict) else []
            physical.append({'phase':routing.parent.name,'request_id':request_id,'actual_alias':wire.get('actual_alias'),
                'depth':wire.get('depth'),'status':wire.get('status'),'http_status':response.get('http_status'),
                'input_tokens':len(request['token_ids']) if 'token_ids' in request else None,
                'action_tokens':sum(len(choice.get('token_ids') or []) for choice in choices) if choices else None,
                'cached_tokens':None,'wall_seconds':wire['ended']-wire['started'] if 'ended' in wire and 'started' in wire else None})
        for path in (routing/'role-audit').glob('*-request.json'):
            request=e.c.read(path)
            if request['request_id'] not in audits:
                request_only.append({'path':str(path),'sha256':e.c.file_hash(path),'request_id':request['request_id'],
                    'interpretation':'Routed request without terminal audit; actual response/usage unknown.'})
    report['all_native_attempts']=physical
    report['routed_requests_without_result']=request_only
    report['physical_totals']={'attempts_with_result':len(physical),'request_only':len(request_only),
        'known_input_tokens':sum(r['input_tokens'] or 0 for r in physical),'known_action_tokens':sum(r['action_tokens'] or 0 for r in physical),
        'unknown_input_counts':sum(r['input_tokens'] is None for r in physical),'unknown_action_counts':sum(r['action_tokens'] is None for r in physical),'cached_tokens':None}
    e.c.write_once(output/'ANALYSIS.json',report)
    return report
