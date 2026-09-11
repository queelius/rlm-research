"""Implementer projection; raw/native audit remains independently reproducible."""
import collections
import json
from pathlib import Path
import experiment as e
import contract

episode_metrics=e.capture.native.episode_metrics

def summarize(records,plan):
    expected={r['id']:r for r in plan};observed={r['coordinate']['id']:r for r in records}
    if len(records)!=len(observed) or any(r['coordinate']!=expected.get(k) for k,r in observed.items()): raise ValueError('coordinate drift')
    cells=[];pairs=[]
    for arm in e.ARMS:
        rows=[r['derived'] for r in records if r['coordinate']['arm']==arm];n=sum(r['arm']==arm for r in plan)
        successes=sum(r.get('strict_reward')==1 for r in rows)
        cells.append({'arm':arm,'planned':n,'recorded':len(rows),'observable':sum(r.get('strict_reward') is not None for r in rows),
            'successes':successes,'success_per_planned':successes/n if n else None,
            'graph_valid':sum(bool(r.get('trace_trainable')) for r in rows),
            'execution_completed':sum(bool(r.get('execution_completed')) for r in rows),
            'unknown_recorded_rewards':sum(r.get('strict_reward') is None for r in rows)})
    for match in sorted({r['matched_id'] for r in plan}):
        rows=[r for r in plan if r['matched_id']==match]
        outcomes={r['arm']:observed.get(r['id'],{}).get('derived',{}).get('strict_reward') for r in rows}
        a,b=outcomes.get('typed'),outcomes.get('restored_raw')
        pairs.append({'matched_id':match,'task_name':rows[0]['task_name'],'context_sha256':rows[0]['context_sha256'],
            'seed':rows[0]['seed'],'outcomes':outcomes,'typed_minus_raw':a-b if a is not None and b is not None else None})
    values=[r['typed_minus_raw'] for r in pairs if r['typed_minus_raw'] is not None]
    return {'planned':len(plan),'recorded':len(records),'cells':cells,'pairs':pairs,
        'primary':{'observable_pairs':len(values),'unknown_pairs':len(pairs)-len(values),'gains':sum(v>0 for v in values),'losses':sum(v<0 for v in values),'ties':values.count(0),'net':sum(values)},
        'unrun_coordinates':[r['id'] for r in plan if r['id'] not in observed],
        'interpretation':'Exploratory exposed contexts; raw scored-empty failures retained; paired seeds do not guarantee matched sampled actions.'}

def analyze(output):
    output=Path(output)
    if not (output/'TERMINAL.json').exists(): raise ValueError('terminal required')
    spec=e.verify();records=[];evidence=[]
    for path in sorted(output.glob('phase-*/rollout/episodes/*.json')):
        row=e.c.read(path)
        if e.c.digest(row['episode'])!=row['episode_sha256']: raise ValueError('raw episode changed')
        row['derived']=episode_metrics(row['episode'],row['timing']['wall_seconds']);records.append(row)
        proof={'coordinate_id':row['coordinate']['id'],'raw_path':str(path)}
        try:
            roots,calls=e.native.exporter.episode_turns(row['episode'],path.parent.parent.with_name('rollout-routing'),spec['bindings']['step8'])
            proof.update(graph_verified=True,returned_root_turns=len(roots),returned_all_turns=len(calls))
        except (ValueError,KeyError,TypeError,AttributeError) as error:
            proof.update(graph_verified=False,error={'type':type(error).__name__,'message':str(error)})
        evidence.append(proof)
    report=summarize(records,spec['plan']);report['episode_evidence']=evidence
    physical=[];requests_only=[];first_roots={};invocations={}
    for routing in output.glob('phase-*/rollout-routing'):
        returned=set()
        for path in sorted((routing/'typed-audit').glob('*-result.json')):
            row=e.c.read(path);returned.add(row['request_id']);decision=row['decision'];wire=row.get('native_wire_request',{}).get('body',{})
            response=row.get('response') or {};tokens=response.get('tokens') or {}
            physical.append({'path':str(path),'coordinate_id':row['coordinate']['id'],'request_id':row['request_id'],
                'depth':row['depth'],'invocation':row['invocation'],'alias':row['actual_alias'],'status':row['status'],
                'input_tokens':len(wire['token_ids']) if 'token_ids' in wire else None,
                'completion_tokens':len(tokens['completion_ids']) if 'completion_ids' in tokens else None,
                'wall_seconds':row['ended_epoch']-row['started_epoch'],'schema_verified':row.get('wire_schema_verified',False)})
            if row['depth']==0:
                key=row['coordinate']['id']
                if key not in first_roots or row['started_epoch']<first_roots[key]['started_epoch']: first_roots[key]=row
            else:
                key=(row['coordinate']['id'],row['invocation'])
                entry=invocations.setdefault(key,{'coordinate_id':key[0],'invocation':key[1],'decision':decision,'responses':[],'first_eligible_epoch':row['started_epoch'] if decision['matched'] else None})
                message=response.get('message') or {};answer=message.get('content')
                # Native nullable content serializes to empty helper answer; record both values.
                raw=answer or ''
                parsed=contract.helper.parse_receipt(raw,decision['requested_ids'],contract.LABELS) if decision['matched'] else None
                entry['responses'].append({'request_id':row['request_id'],'native_content':answer,'raw_answer':raw,'finish_reason':response.get('finish_reason'),'strict_map':parsed})
        for path in (routing/'typed-audit').glob('*-request.json'):
            row=e.c.read(path)
            if row['request_id'] not in returned: requests_only.append({'path':str(path),'coordinate_id':row['coordinate']['id'],'request_id':row['request_id'],'actual_wire_unknown':True})
    initial=[]
    for pair in report['pairs']:
        planned=[r for r in spec['plan'] if r['matched_id']==pair['matched_id']]
        roots={r['arm']:first_roots.get(r['id']) for r in planned};a,b=roots.get('restored_raw'),roots.get('typed')
        value={'matched_id':pair['matched_id'],'both_initial_observed':a is not None and b is not None}
        if a and b:
            aw=a.get('native_wire_request',{}).get('body',{});bw=b.get('native_wire_request',{}).get('body',{})
            value.update(initial_prompt_tokens_equal=aw.get('token_ids')==bw.get('token_ids'),initial_sampling_equal=aw.get('sampling_params')==bw.get('sampling_params'),
                initial_root_action_tokens_equal=(a.get('response') or {}).get('tokens',{}).get('completion_ids')==(b.get('response') or {}).get('tokens',{}).get('completion_ids'),
                caveat='Seed matching is not deterministic counterfactual equality; later adaptive children are not paired.')
        initial.append(value)
    report.update(all_physical_attempts=physical,request_only=requests_only,child_invocations=list(invocations.values()),initial_root_comparisons=initial,
        physical_cost={'known_input_tokens':sum(r['input_tokens'] or 0 for r in physical),'known_completion_tokens':sum(r['completion_tokens'] or 0 for r in physical),
            'unknown_input_attempts':sum(r['input_tokens'] is None for r in physical),'unknown_completion_attempts':sum(r['completion_tokens'] is None for r in physical)},
        provenance_caveat='Contract matched, not authenticated Python helper origin. Root-writable audit is diagnostic. This is an implementer projection, not independent audit.')
    e.c.write_once(output/'IMPLEMENTER_PROJECTION.json',report);return report
