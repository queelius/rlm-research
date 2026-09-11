"""Strict native endpoints, raw wire costs and descriptive static evidence only."""
import ast
import json
import re


def score(trace,capture,gold):
    response=(capture or {}).get('native_response') or {};message=response.get('message') or {};reply=trace.get('root_reply')
    available=(capture or {}).get('status')=='returned' and response.get('finish_reason') in ('stop','length') and not message.get('tool_calls') and isinstance(reply,str) and message.get('content')==reply
    match=re.fullmatch(r'Answer: ([0-9]+)',reply.strip()) if isinstance(reply,str) else None
    return dict(reward=int(bool(match and int(match[1])==gold)) if available else None,format=bool(match) if available else None,available=bool(available),reply=reply,finish_reason=response.get('finish_reason'),has_tools=bool(message.get('tool_calls')))


def final_capture(trace,roles):
    from verifiers.v1.trace import WireTrace
    calls={c['node']:c for c in trace['calls']};roots=[c for c in trace['calls'] if roles[c['acp']['request_id']]['depth']==0]
    if not roots:return None,[]
    last=roots[-1];native=WireTrace.model_validate(trace);indices={id(v):i for i,v in enumerate(native.nodes)};matches=[]
    for branch in native.branches:
        ids=[];nodes=[]
        for node in branch.nodes:
            index=indices[id(node)];ids.extend(node.token_ids);nodes.append(index)
            if index==last['node']:
                capture=roles[last['acp']['request_id']];tokens=capture['native_response']['tokens']
                if ids!=tokens['prompt_ids']+tokens['completion_ids'] or tokens['prompt_ids']!=capture['native_wire_request']['body']['token_ids']:raise ValueError('physical final branch mismatch')
                matches.append(nodes[:]);break
    if not matches or any(x!=matches[0] for x in matches):raise ValueError('unavailable or ambiguous native final branch')
    return roles[last['acp']['request_id']],matches[0]


def usage(records):
    values=[]
    for record in records:
        response=(record.get('native_wire_response') or {}).get('body')
        if isinstance(response,str):response=json.loads(response)
        u=response.get('usage',{}) if isinstance(response,dict) else {};incoming=u.get('prompt_tokens');outgoing=u.get('completion_tokens');cached=u.get('prompt_tokens_details',{}).get('cached_tokens')
        for v in (incoming,outgoing,cached):
            if v is not None and (type(v)!=int or v<0):raise ValueError('invalid usage')
        values.append(dict(input=incoming,output=outgoing,cached=cached,uncached=incoming-cached if incoming is not None and cached is not None else None))
    keys=('input','output','cached','uncached')
    return dict(calls=len(records),known={k:sum(v[k] or 0 for v in values) for k in keys},unknown={k:sum(v[k] is None for v in values) for k in keys})


def pipeline_cost(new,reused):
    return dict(new_physical=new,reused_acquisition=reused,standalone_full_pipeline=dict(calls=new['calls']+reused['calls'],known={k:new['known'][k]+reused['known'][k] for k in new['known']},unknown={k:new['unknown'][k]+reused['unknown'][k] for k in new['unknown']}),amortized=False)


def evidence(trace,node_ids,labels,relevant,target,available):
    count=sum(labels[k]==target for k in relevant);match=re.fullmatch(r'Answer: ([0-9]+)',(trace.get('root_reply') or '').strip());programs=[];observations=[]
    for index in node_ids:
        message=trace['nodes'][index]['message']
        if message.get('role')=='tool':
            text=message.get('content');kind='other';value=None
            try:value=ast.literal_eval(text)
            except (TypeError,ValueError,SyntaxError):pass
            if type(value) in (int,float):kind='scalar'
            elif isinstance(value,dict) and value and set(value)<=set(labels):kind='map'
            observations.append(dict(node=index,kind=kind,text=text,value=value if kind=='scalar' else None,exact_supplied_map=kind=='map' and value==labels))
        for tool in message.get('tool_calls') or []:
            if tool.get('name')!='ipython':continue
            code=None
            try:
                args=tool['arguments'];code=(json.loads(args) if isinstance(args,str) else args)['code'];tree=ast.parse(code);valid=True
            except (TypeError,ValueError,KeyError,SyntaxError):valid=False
            programs.append(dict(node=index,code=code,ast_valid=valid,literal_map_filename=bool(code and 'labels.json' in code),literal_user_key=bool(code and ('["user"]' in code or "['user']" in code))))
    return dict(supplied_map_count=count,final_map_consistent=int(bool(match and int(match[1])==count)) if available else None,requested_ids=relevant,programs=programs,observations=observations,actual_map_loading=None,actual_scoped_reduction=None,state_use_status='manual trace/code audit required; markers and scalar agreement alone are not proof')
