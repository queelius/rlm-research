"""Whole-output, order-aware scoring; sampled output is never repaired."""
import json,re
import protocol_v2 as p,study as s
native=s.load('field_order_native_auth',s.SIDE/'leaf-role-tool-contract-v1/scoring_v2.py',
              '8028956dfe19b05097b5cd0f80b64c1a5b8f966885d0704dbfb7dc5d3dee0236',{'study':s})
verified_response=native.verified_response
def missing(context):
    return dict(available=False,strict_correct=None,strict_bounds=[0,len(context['records'])],
                shape_valid=None,contract_valid=None,tag_position_matches=None,
                named_correct_disagree=None,named_disagree_items=None,third_correct_disagree=None)
def unique(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ValueError('duplicate object key')
        result[k]=v
    return result
def tag_score(message,context,arm):
    result={**missing(context),'available':True,'strict_correct':0,'strict_bounds':[0,0],
            'shape_valid':False,'contract_valid':False,'field_order_valid':False}
    if message.get('tool_calls'):return {**result,'reason':'wrong_route_no_execution'}
    try:values=json.loads(message.get('content'),object_pairs_hook=unique,
                          parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    except (ValueError,TypeError):return {**result,'reason':'invalid_json'}
    if not isinstance(values,list) or len(values)!=len(context['records']):
        return {**result,'reason':'incomplete_array'}
    shape=all(isinstance(v,dict) and set(v)=={'label','tag'} and type(v['label'])is str and
              v['label'] in p.LABELS and type(v['tag'])is str and re.fullmatch('m[0-9a-f]{12}',v['tag'])
              for v in values)
    tags=[v.get('tag') if isinstance(v,dict) else None for v in values]
    expected=p.requested_tags(context)
    order=all(isinstance(v,dict) and list(v)==list(p.field_order(arm)) for v in values)
    matching=sum(t==e for t,e in zip(tags,expected,strict=True))
    result.update(shape_valid=bool(shape),field_order_valid=order,tag_position_matches=matching)
    if not(shape and order and matching==len(expected)):
        return {**result,'reason':'whole_contract_failure'}
    labels=[v['label'] for v in values];gold=[r['gold_label'] for r in context['records']]
    correct=sum(a==b for a,b in zip(labels,gold,strict=True))
    result.update(contract_valid=True,strict_correct=correct,strict_bounds=[correct,correct],
                  predictions=labels,emitted_tags=tags,whole_batch_correct=correct==len(gold),reason='strict_contract')
    if arm.startswith('wrong_'):
        named={r['id']:r['gold_label'] for r in context['records']}
        ix=[i for i,t in enumerate(tags) if named[t]!=gold[i]]
        n=sum(labels[i]==named[tags[i]] for i in ix);v=sum(labels[i]==gold[i] for i in ix)
        result.update(named_disagree_items=len(ix),named_correct_disagree=n,third_correct_disagree=len(ix)-n-v)
    return result

def host_join(labels,tags):
    if not isinstance(labels,list) or len(labels)!=len(tags) or len(set(tags))!=len(tags):
        raise ValueError('complete fixed-cardinality array and unique addresses required')
    if any(type(v)is not str or v not in p.LABELS for v in labels):
        raise ValueError('canonical labels required')
    return list(zip(tags,labels,strict=True))

def score(message,context,arm):
    if not arm.endswith('labels_only'):
        return tag_score(message,context,arm)
    invalid={**missing(context),'available':True,'strict_correct':0,'strict_bounds':[0,0],
             'shape_valid':False,'contract_valid':False,'model_emitted_identifiers':False,
             'host_join_performed':False}
    if message.get('tool_calls'):return {**invalid,'reason':'wrong_route_no_execution'}
    try:
        labels=json.loads(message.get('content'),object_pairs_hook=unique,
                          parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
        joined=host_join(labels,p.requested_tags(context))
    except (ValueError,TypeError):return {**invalid,'reason':'invalid_complete_label_array'}
    mapped=[dict(tag=t,label=v) for t,v in joined]
    result=tag_score({'content':json.dumps(mapped)},context,arm.split('_',1)[0]+'_tag_first')
    result.update(tag_position_matches=None,field_order_valid=None,emitted_tags=None,
                  model_emitted_identifiers=False,host_join_performed=True,
                  host_joined_tag_label_pairs=joined)
    return result
