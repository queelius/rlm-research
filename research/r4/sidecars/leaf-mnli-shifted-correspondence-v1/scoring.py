"""Strict requested-tag primary and non-repairing shifted-name diagnostic."""
import collections,json,re
import protocol as p
import study as s
with s.aliases({'study':s}):
    native=s.load('mnli_shift_native_auth',s.SIDE/'leaf-role-tool-contract-v1/scoring_v2.py',
                  '8028956dfe19b05097b5cd0f80b64c1a5b8f966885d0704dbfb7dc5d3dee0236')
verified_response=native.verified_response

def missing(context):
    return dict(available=False,strict_correct=None,strict_bounds=[0,len(context['records'])],shape_valid=None,
        contract_valid=None,shape_positional_correct=None,tag_position_matches=None,whole_batch_correct=None,
        field_order_valid=None,shifted_named_correct_disagree=None,shifted_named_disagree_items=None,
        reason='missing_or_unverified')
def unique(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('duplicate key')
        out[k]=v
    return out
def score(message,context,arm):
    n=len(context['records']);base=missing(context);base.update(available=True,strict_correct=0,strict_bounds=[0,0],
        shape_valid=False,contract_valid=False,whole_batch_correct=False)
    if message.get('tool_calls'):return {**base,'reason':'authenticated_tool_branch_not_executed'}
    try:values=json.loads(message.get('content'),object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    except (ValueError,TypeError):return {**base,'reason':'invalid_json'}
    if not isinstance(values,list) or len(values)!=n:return {**base,'reason':'wrong_cardinality_or_array'}
    shape=all(isinstance(v,dict) and set(v)=={'tag','label'} and isinstance(v.get('tag'),str)
        and re.fullmatch(r'm[0-9a-f]{12}',v['tag']) and v.get('label') in p.LABELS for v in values)
    expected=p.expected_tags(context,arm);tags=[v.get('tag') if isinstance(v,dict) else None for v in values]
    tag_ok=[a==b for a,b in zip(tags,expected,strict=True)];order=all(isinstance(v,dict) and list(v)==['tag','label'] for v in values)
    contract=bool(shape and order and all(tag_ok));correct=sum(v['label']==r['gold_label'] for v,r in zip(values,context['records'],strict=True)) if shape else None
    named_correct=named_n=None
    if contract and arm=='shift17':
        by_id={r['id']:r['gold_label'] for r in context['records']};pairs=[(v,by_id[t],r['gold_label']) for v,t,r in zip(values,expected,context['records'],strict=True) if by_id[t]!=r['gold_label']]
        named_n=len(pairs);named_correct=sum(v['label']==named for v,named,_ in pairs)
    counts=collections.Counter(t for t in tags if isinstance(t,str))
    base.update(shape_valid=bool(shape),contract_valid=contract,strict_correct=correct if contract else 0,
        strict_bounds=[correct if contract else 0]*2,shape_positional_correct=correct,tag_position_matches=sum(tag_ok),
        per_item_tag_correct=tag_ok,field_order_valid=order,whole_batch_correct=bool(contract and correct==n),
        predictions=[v['label'] for v in values] if shape else None,emitted_tags=tags,
        duplicate_tags=sorted(k for k,v in counts.items() if v>1),missing_expected_tags=sorted(set(expected)-set(tags)),
        extra_tags=sorted(set(t for t in tags if isinstance(t,str))-set(expected)),shifted_named_correct_disagree=named_correct,
        shifted_named_disagree_items=named_n,reason='strict_contract' if contract else 'shape_or_tag_contract_failure')
    return base
