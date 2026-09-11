"""Exact full-contract primary; shape semantics/tag fidelity remain separate."""
import collections
import json
import re
import mn_protocol as p
import mn_study as s
with s.aliases({'study':s}):
    native=s.load('mn_new_context_native_auth',s.SIDE/'leaf-role-tool-contract-v1/scoring_v2.py','8028956dfe19b05097b5cd0f80b64c1a5b8f966885d0704dbfb7dc5d3dee0236')
verified_response=native.verified_response
def missing(context):
    return dict(available=False,strict_correct=None,strict_bounds=[0,len(context['records'])],shape_valid=None,contract_valid=None,shape_positional_correct=None,tag_position_matches=None,whole_batch_correct=None,field_order_valid=None,reason='missing_or_unverified')
def unique(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('duplicate key')
        value[key]=item
    return value
def score(message,context,arm):
    n=len(context['records']);base=missing(context);base.update(available=True,strict_correct=0,strict_bounds=[0,0],shape_valid=False,contract_valid=False,whole_batch_correct=False)
    if message.get('tool_calls'):return {**base,'reason':'authenticated_tool_branch_not_executed'}
    try:values=json.loads(message.get('content'),object_pairs_hook=unique,parse_constant=lambda value:(_ for _ in ()).throw(ValueError(value)))
    except (ValueError,TypeError):return {**base,'reason':'invalid_json'}
    if not isinstance(values,list) or len(values)!=n:return {**base,'reason':'wrong_cardinality_or_array'}
    shape=all(isinstance(v,dict) and set(v)=={'tag','label'} and isinstance(v.get('tag'),str) and re.fullmatch(r'm[0-9a-f]{12}',v['tag']) and v.get('label') in p.LABELS for v in values)
    expected=p.expected_tags(context,arm);tags=[v.get('tag') if isinstance(v,dict) else None for v in values];tag_ok=[a==b for a,b in zip(tags,expected,strict=True)]
    order=all(isinstance(v,dict) and list(v)==['tag','label'] for v in values);contract=bool(shape and order and all(tag_ok))
    correct=sum(v['label']==r['gold_label'] for v,r in zip(values,context['records'],strict=True)) if shape else None
    counts=collections.Counter(tag for tag in tags if isinstance(tag,str));actual=set(counts)
    base.update(shape_valid=bool(shape),contract_valid=contract,strict_correct=correct if contract else 0,strict_bounds=[correct if contract else 0]*2,shape_positional_correct=correct,tag_position_matches=sum(tag_ok),per_item_tag_correct=tag_ok,field_order_valid=order,whole_batch_correct=bool(contract and correct==n),predictions=[v['label'] for v in values] if shape else None,emitted_tags=tags,duplicate_tags=sorted(k for k,v in counts.items() if v>1),missing_expected_tags=sorted(set(expected)-actual),extra_tags=sorted(actual-set(expected)),reason='strict_contract' if contract else 'shape_or_tag_contract_failure')
    return base
