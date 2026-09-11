"""Implementer-owned terminal projection; independent raw audit remains required."""
import argparse
import collections
import json
import re
from pathlib import Path
import study as s
import bridge

def endpoint(reply,gold,completed,available):
    observed=bool(completed and available and isinstance(reply,str))
    match=re.fullmatch(r'Answer: ([0-9]+)',reply.strip()) if isinstance(reply,str) else None
    parsed=int(match[1]) if match else None
    return {'score':int(parsed==gold) if observed else None,'format_valid':bool(match) if observed else None,
        'parsed':parsed,'completed_empty':bool(completed and reply==''),'observable':observed}

def usage(audit):
    body=audit.get('native_wire_response',{}).get('body')
    if isinstance(body,str):
        try:body=json.loads(body)
        except ValueError:body=None
    u=body.get('usage',{}) if isinstance(body,dict) else {};incoming=u.get('prompt_tokens');outgoing=u.get('completion_tokens')
    cached=u.get('prompt_tokens_details',{}).get('cached_tokens')
    if any(v is not None and (type(v) is not int or v<0) for v in (incoming,outgoing,cached)):raise ValueError('invalid usage')
    if incoming is not None and cached is not None and cached>incoming:raise ValueError('cached exceeds input')
    return {'input':incoming,'cached':cached,'uncached':incoming-cached if incoming is not None and cached is not None else None,'output':outgoing}

def analyze(output,destination):
    if not (output/'TERMINAL.json').exists():raise ValueError('owned terminal required')
    spec=s.verify();directory=output/'rollout';sources={};cache={}
    def read(path):
        path=Path(path)
        if path not in cache:sources[str(path)]=s.sha(path);cache[path]=s.read(path)
        return cache[path]
    rawrows={v['coordinate']['id']:v for v in [read(p) for p in (directory/'rows').glob('*.json')]}
    role={v['request_id']:v for v in [read(p) for p in (directory/'role-audit').glob('*-result.json')]}
    typed={v['request_id']:v for v in [read(p) for p in (directory/'typed-audit').glob('*-result.json')]}
    attempts=[read(p) for p in (directory/'typed-audit').glob('*-request.json')]
    bycoord=collections.defaultdict(list)
    for rid,t in typed.items():
        if rid in role:bycoord[t['coordinate']['id']].append(role[rid])
    public={c['id']:c for c in read(s.ROOT/'inputs/PUBLIC.json')};host=read(s.ROOT/'inputs/HOST_GOLD.json')
    prompts={r['id']:r for r in read(s.ROOT/'inputs/PROMPTS.json')};rows=[];calls=[]
    for coordinate in spec['plan']:
        rid=coordinate['id'];rawrow=rawrows.get(rid,{});raw=read(rawrow['episode_path']) if rawrow.get('episode_path') else {}
        trace=(raw.get('traces') or [{}])[0];physical=sorted(bycoord[rid],key=lambda a:a['started'])
        roots=[a for a in physical if a['depth']==0];children=[a for a in physical if a['depth']>0]
        available=bool(roots and roots[-1].get('status')=='returned');gold=host[coordinate['context_id']]
        row={**coordinate,**endpoint(trace.get('root_reply'),gold['answers'][coordinate['family']],trace.get('is_completed'),available),
            'gold':gold['answers'][coordinate['family']],'reply':trace.get('root_reply'),'episode_ok':raw.get('ok'),
            'episode_errors':raw.get('errors'),'trace_errors':trace.get('errors'),'row_error':rawrow.get('error'),
            'episode_path':rawrow.get('episode_path'),'not_started':rid not in rawrows,'initial_root_token_equal':None,
            'initial_root_output_ids':None,'uptake':False,'eligible_widths':[],'strict_maps':0,'malformed_returns':0,
            'semantic_correct':0,'semantic_labels':0,'corroborated_deliveries':0,'uncorroborated_deliveries':0}
        cost=collections.Counter(physical_attempts=sum(v['coordinate']['id']==rid for v in attempts),root_requests=len(roots),child_requests=len(children));missing=collections.Counter()
        for a in physical:
            t=typed[a['request_id']];body=a.get('native_wire_request',{}).get('body');u=usage(a)
            if body:
                assert body==t.get('native_wire_request',{}).get('body') and body['model']==a['actual_alias']
                assert body['sampling_params']['seed']==coordinate['seed']
                grammar=body['sampling_params'].get('structured_outputs')
                assert grammar==({'json':t['decision']['schema']} if t['decision']['apply'] else None)
            for k,v in u.items():
                if v is None:missing[k]+=1
                else:cost[k]+=v
            tokens=a.get('native_response',{}).get('tokens',{})
            calls.append({'coordinate_id':rid,'request_id':a['request_id'],'invocation':a['invocation'],'depth':a['depth'],'status':a['status'],
                'usage':u,'prompt_ids':tokens.get('prompt_ids'),'completion_ids':tokens.get('completion_ids'),
                'completion_logprobs':tokens.get('completion_logprobs'),'eligible':t['decision']['apply'],'decision':t['decision']})
        if roots:
            row['initial_root_token_equal']=roots[0]['native_wire_request']['body']['token_ids']==prompts[rid]['token_ids']
            row['initial_root_output_ids']=roots[0].get('native_response',{}).get('tokens',{}).get('completion_ids')
        claims=trace.get('info',{}).get('representation_bridge',{});events=[]
        try:events=[json.loads(l) for l in (claims.get('raw') or '').splitlines()]
        except ValueError:row['event_parse_error']=True
        requested=set();labels={};conflicts=set();delivery_rows=[]
        for a in children:
            decision=typed[a['request_id']]['decision']
            if decision['apply']:
                row['uptake']=True;requested.update(decision['requested_ids']);row['eligible_widths'].append(len(decision['requested_ids']))
        for event in events:
            if event['event']!='delivered' or not event['eligible']:continue
            matches=[a for a in children if a['invocation']==event['child_invocation'] and
                a.get('native_response',{}).get('message',{}).get('content')==event['raw_answer'] and
                typed[a['request_id']]['decision'].get('request_text')==event['actual_child_prompt']]
            if not matches:row['uncorroborated_deliveries']+=1;continue
            row['corroborated_deliveries']+=1
            try:
                projected=bridge.project(event['raw_answer'],event['ids'],coordinate['arm'])
                assert projected==event['broker_answer'];mapping=json.loads(projected);row['strict_maps']+=1
                correct=sum(value==s.LABELS[gold['coarse_by_id'][key]] for key,value in mapping.items())
                row['semantic_correct']+=correct;row['semantic_labels']+=len(mapping)
                for key,value in mapping.items():
                    if key in labels and labels[key]!=value:conflicts.add(key)
                    labels[key]=value
                delivery_rows.append({'child_invocation':event['child_invocation'],'ids':event['ids'],'labels':mapping,
                    'semantic_correct':correct,'raw_answer':event['raw_answer'],'broker_answer':projected,'native_requests':[a['request_id'] for a in matches]})
            except ValueError:row['malformed_returns']+=1
        total=len(public[coordinate['context_id']]['records']);target_ids=[key for key,value in labels.items() if value==gold['target_label']]
        derived=len(target_ids) if coordinate['family']=='count' else sum(int(key[1:]) for key in target_ids)
        row.update(cost=dict(cost),unknown_usage_requests=dict(missing),unique_requested=len(requested),unique_returned=len(labels),
            conflicts=sorted(conflicts),complete_returned_coverage=len(labels)==total,returned_evidence_scalar_last_delivery_wins=derived,
            final_equals_returned_scalar=None if not labels or conflicts or row['parsed'] is None else row['parsed']==derived,
            fidelity_caveat='descriptive delivered-evidence union, not proof of root consumption or final branch; conflicting/revised labels withheld',
            delivered=delivery_rows,runtime_claims_available=claims.get('raw') is not None)
        rows.append(row)
    pairs=[]
    for pair_id in dict.fromkeys(r['pair_id'] for r in spec['plan']):
        members={r['arm']:r for r in rows if r['pair_id']==pair_id};a,b=members['array'],members['map']
        pairs.append({'pair_id':pair_id,'context_id':a['context_id'],'family':a['family'],'seed':a['seed'],
            'array':a['score'],'map':b['score'],'map_minus_array':None if a['score'] is None or b['score'] is None else b['score']-a['score'],
            'both_uptake':a['uptake'] and b['uptake'],'initial_output_equal':a['initial_root_output_ids']==b['initial_root_output_ids']})
    summary=[]
    for family in ('checksum','count'):
        for arm in ('array','map'):
            subset=[r for r in rows if r['family']==family and r['arm']==arm]
            summary.append({'family':family,'arm':arm,'planned':len(subset),'observed':sum(r['score'] is not None for r in subset),
                'correct':sum(r['score']==1 for r in subset),'null':sum(r['score'] is None for r in subset),'uptake':sum(r['uptake'] for r in subset),
                'cost':dict(sum((collections.Counter(r['cost']) for r in subset),collections.Counter()))})
    destination.mkdir(parents=True,exist_ok=False)
    for name,value in [('ROWS.json',rows),('CALLS.json',calls),('METRICS.json',{'planned':32,'summary':summary,'pairs':pairs,
        'analysis_owner':'implementer projection, not independent audit','terminal':read(output/'TERMINAL.json')}),('RAW_SOURCES.json',sources)]:s.write(destination/name,value)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--destination',type=Path,required=True)
    a=p.parse_args();print(json.dumps(analyze(a.output,a.destination)))
