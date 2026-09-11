"""Strict primary, shape-only semantic diagnostics, and qualified native admission."""
import collections
import json
import re
import protocol as p
import study as s

with s.aliases({'study':s}):
    _native=s.load('mnli_qualified_native_authenticator',s.SIDE/'leaf-role-tool-contract-v1/scoring_v2.py',
        '8028956dfe19b05097b5cd0f80b64c1a5b8f966885d0704dbfb7dc5d3dee0236')
verified_response=_native.verified_response


def missing(context):
    return dict(available=False,strict_correct=None,strict_bounds=[0,len(context['records'])],
        shape_valid=None,contract_valid=None,shape_positional_correct=None,tag_position_matches=None,
        per_item_tag_correct=None,whole_batch_correct=None,field_order_valid=None,reason='missing_or_unverified')


def unique(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ValueError('duplicate key')
        result[k]=v
    return result


def score(message,context,arm,constant):
    n=len(context['records']);base=missing(context)
    base.update(available=True,strict_correct=0,strict_bounds=[0,0],shape_valid=False,
                contract_valid=False,whole_batch_correct=False)
    if message.get('tool_calls'):
        return {**base,'reason':'authenticated_tool_branch_not_executed'}
    try:
        values=json.loads(message.get('content'),object_pairs_hook=unique,
                          parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    except (ValueError,TypeError):return {**base,'reason':'invalid_json'}
    if not isinstance(values,list) or len(values)!=n:return {**base,'reason':'wrong_cardinality_or_array'}
    shape=all(isinstance(v,dict) and set(v)=={'tag','label'} and isinstance(v.get('tag'),str)
              and re.fullmatch(r'm[0-9a-f]{12}',v['tag']) is not None and v.get('label') in p.LABELS for v in values)
    expected=[r['id'] if arm=='matching' else constant for r in context['records']]
    tags=[v.get('tag') if isinstance(v,dict) else None for v in values]
    per_item=[a==b for a,b in zip(tags,expected,strict=True)]
    order=all(isinstance(v,dict) and list(v)==['tag','label'] for v in values)
    contract=shape and order and all(per_item)
    correct=sum(v['label']==r['gold_label'] for v,r in zip(values,context['records'],strict=True)) if shape else None
    actual=[v for v in tags if isinstance(v,str)];counts=collections.Counter(actual)
    base.update(shape_valid=shape,contract_valid=contract,strict_correct=correct if contract else 0,
        strict_bounds=[correct if contract else 0]*2,shape_positional_correct=correct,
        tag_position_matches=sum(per_item),per_item_tag_correct=per_item,field_order_valid=order,
        whole_batch_correct=bool(contract and correct==n),predictions=[v['label'] for v in values] if shape else None,
        emitted_tags=tags,duplicate_tags=sorted(k for k,v in counts.items() if v>1),
        missing_expected_tags=sorted(set(expected)-set(actual)),extra_tags=sorted(set(actual)-set(expected)),
        reason='strict_contract' if contract else 'shape_or_tag_contract_failure')
    return base
