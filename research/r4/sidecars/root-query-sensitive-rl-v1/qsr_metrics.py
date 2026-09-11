"""Authenticated native endpoint availability, separate from whole-graph admission."""
import functools
import json
import re
import qsr_study as s

def score_message(reply,content,tools,finish,gold):
    available=isinstance(reply,str) and reply==content and not tools and finish in ('stop','length')
    match=re.fullmatch(r'Answer: ([0-9]+)',reply.strip()) if isinstance(reply,str) else None
    return dict(available=available,reward=int(bool(match and int(match[1])==gold)) if available else None,format=bool(match) if available else None,reply=reply,finish_reason=finish,reason=None if available else 'no authenticated returned final / outstanding tool route')

def paired_summary(inventory):
    arms={arm:{r['coordinate']['id']:r for r in inventory if r['phase']=='readout' and r['arm']==arm} for arm in ('unchanged','trained')}
    if arms['unchanged'].keys()!=arms['trained'].keys():raise ValueError('paired planned inventory differs')
    policies={};paired=dict(wins=0,losses=0,ties=0,unknown=0)
    for arm,rows in arms.items():
        success=sum(r['reward']==1 for r in rows.values());null=sum(r['reward'] is None for r in rows.values())
        policies[arm]=dict(planned=len(rows),available=len(rows)-null,correct=success,null=null,success_bounds=[success,success+null],operational_successes=success)
    for key,before in arms['unchanged'].items():
        after=arms['trained'][key]
        if before['coordinate']!=after['coordinate']:raise ValueError('paired input/seed mismatch')
        a,b=before['reward'],after['reward'];kind='unknown' if a is None or b is None else 'wins' if b>a else 'losses' if b<a else 'ties';paired[kind]+=1
    strata={}
    for name,predicate in [('heldout_cells',lambda r:r['coordinate']['heldout_cell']),('supported_cells',lambda r:not r['coordinate']['heldout_cell']),('size16',lambda r:r['coordinate']['records']==16),('size32',lambda r:r['coordinate']['records']==32)]:
        strata[name]={arm:dict(planned=sum(predicate(r) for r in rows.values()),correct=sum(predicate(r) and r['reward']==1 for r in rows.values()),null=sum(predicate(r) and r['reward'] is None for r in rows.values())) for arm,rows in arms.items()}
    return dict(policies=policies,paired=paired,strata=strata,context_clusters=len({r['coordinate']['context_id'] for r in arms['unchanged'].values()}),independence='query pairs nested within contexts',mechanism='requires independent executed-trace audit; neither answer agreement nor prompt/AST presence proves use')

@functools.lru_cache(maxsize=1)
def qualified():
    p=s.SIDE/'root-map-contract-clarity-v1/metrics.py'
    return s.load('qsr_qualified_final_metrics',p,'0ef6a89ad3655afe71226878f0296802e6b8af62b5aa295eec23e3ed151c53d3')

def audits(directory,identifier):
    ids={v['request_id'] for p in (directory/'typed-audit').glob('*-request.json') if (v:=s.read(p))['coordinate']['id']==identifier}
    result={v['request_id']:v for p in (directory/'role-audit').glob('*-result.json') if (v:=s.read(p))['request_id'] in ids}
    for p in (directory/'role-audit').glob('*-request.json'):
        v=s.read(p)
        if v['request_id'] in ids and v['request_id'] not in result:result[v['request_id']]={**v,'status':'unreturned','native_response':None}
    return result

def endpoint(episode,directory,spec,coordinate):
    import qsr_native as n
    result=dict(available=False,reward=None,format=None,reason='unverified native endpoint')
    roles=audits(directory,coordinate['id']);result['cost']=qualified().usage(list(roles.values()))
    try:
        traces=episode.get('traces') or []
        if len(traces)!=1:raise ValueError('not one native root trace')
        trace=traces[0];calls=trace.get('calls') or [];roots=[c for c in calls if roles[c['acp']['request_id']]['depth']==0]
        if not roots:raise ValueError('no native root calls')
        initial=roles[roots[0]['acp']['request_id']]['native_wire_request']['body'];task=s.read(s.ROOT/'inputs/TASKS.json')[coordinate['task_name']]
        if initial['token_ids']!=task['first_prompt_token_ids'] or initial['model']!=spec['binding']['role_map']['root']:raise ValueError('first prompt/model mismatch')
        final,nodes=qualified().final_capture(trace,roles)
        if final is None or final.get('status')!='returned':raise ValueError('final physical response missing')
        call=roots[-1];response=final['native_response'];tokens=response['tokens'];wire=final['native_wire_request']['body'];physical=final['native_wire_response'];raw=json.loads(physical['body']);choice=raw['choices'][0]
        if physical['http_status']!=200 or final['actual_alias']!=call['model'] or wire['model']!=call['model'] or final['model_sha256']!=spec['binding']['models'][call['model']]['adapter_sha256']:raise ValueError('final physical model mismatch')
        if choice['token_ids']!=tokens['completion_ids'] or [v['logprob'] for v in choice['logprobs']['content']]!=tokens['completion_logprobs']:raise ValueError('final token/logprob mismatch')
        if raw['usage']['prompt_tokens']!=len(tokens['prompt_ids']) or raw['usage']['completion_tokens']!=len(tokens['completion_ids']):raise ValueError('final physical usage mismatch')
        if any(wire['sampling_params'].get(k)!=v for k,v in dict(seed=coordinate['seed'],temperature=.5,top_p=1,top_k=-1,min_p=0,max_tokens=2048).items()):raise ValueError('final sampling mismatch')
        message=response['message'];parsed=n.stack().native.renderer().parse_response(tokens['completion_ids'])
        # Tool actions are legitimate intermediate actions in this task. A capped
        # last tool action is not a returned final, regardless of trace completion.
        if message.get('tool_calls'):
            result.update(reason='last returned root action has outstanding tools',finish_reason=response.get('finish_reason'));return result
        content=message.get('content')
        if content is None and parsed.content=='':content=''
        if parsed.content!=content or any(getattr(t.status,'value',t.status)=='ok' for t in parsed.tool_calls):raise ValueError('decoded final text/route mismatch')
        if choice['finish_reason']!=response.get('finish_reason') or call['finish_reason']!=response.get('finish_reason'):raise ValueError('final finish branch mismatch')
        gold=s.read(s.ROOT/'inputs/HOST_GOLD.json')[coordinate['context_id']]['answers'][coordinate['family']]
        result.update(score_message(trace.get('root_reply'),content,message.get('tool_calls'),response.get('finish_reason'),gold),final_branch_node_indices=nodes,final_request_id=final['request_id'],first_prompt_verified=True)
    except (ValueError,KeyError,TypeError,AttributeError) as error:result.update(reason=type(error).__name__+': '+str(error))
    return result
