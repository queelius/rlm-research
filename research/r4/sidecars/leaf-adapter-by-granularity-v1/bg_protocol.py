"""Native map contract; gold is scoring-only and never part of requests."""
import json
import math
CATEGORIES=('human being','location','abbreviation','entity','description and abstract concept','numeric value')
def partitions(records,arm):
    width=100 if arm=='W' else 16 if arm=='S' else None
    if width is None:raise ValueError('unknown granularity')
    return [records[i:i+width] for i in range(0,len(records),width)]
def unique(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('duplicate map ID')
        value[key]=item
    return value
def score(content,ids,gold,authenticated,tool_calls=False):
    base=dict(available=bool(authenticated),complete_map=False,strict_correct=None if not authenticated else 0,labels=None,canonical_id_matches=None if not authenticated else 0,output_order_equal=None,invalid_reason=None)
    if not authenticated:return base
    try:
        if tool_calls:raise ValueError('wrong tool route; no execution')
        labels=json.loads(content,object_pairs_hook=unique)
        if not isinstance(labels,dict):raise ValueError('not a JSON object')
        base['canonical_id_matches']=sum(k in labels and isinstance(labels[k],str) and labels[k] in CATEGORIES for k in ids)
        if set(labels)!=set(ids) or len(ids)!=len(set(ids)) or any(not isinstance(v,str) or v not in CATEGORIES for v in labels.values()):raise ValueError('incomplete/extra/noncanonical map')
        base.update(complete_map=True,labels=labels,strict_correct=sum(labels[k]==gold[k] for k in ids),output_order_equal=list(labels)==ids)
    except (ValueError,TypeError) as error:base['invalid_reason']=str(error)
    return base
def native(raw,body,renderer):
    if raw['model']!=body['model'] or len(raw['choices'])!=1:raise ValueError('native model/choice identity')
    c=raw['choices'][0];ids=c['token_ids'];logs=c['logprobs']['content'];usage=raw['usage']
    if not ids or len(ids)!=len(logs) or not all(math.isfinite(x['logprob']) for x in logs):raise ValueError('token/logprob identity')
    if usage['prompt_tokens']!=len(body['token_ids']) or usage['completion_tokens']!=len(ids):raise ValueError('native prompt/output usage')
    if not isinstance(raw.get('request_id'),str) or not raw['request_id']:raise ValueError('provider request identity')
    if c['finish_reason'] not in ('stop','length','tool_calls'):raise ValueError('unverified finish reason')
    parsed=renderer.parse_response(ids)
    return dict(content=parsed.content,tool_calls=bool(parsed.tool_calls) or c['finish_reason']=='tool_calls',finish_reason=c['finish_reason'],completion_ids=ids,provider_request_id=raw['request_id'])
