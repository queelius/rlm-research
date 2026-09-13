"""Public-order output interface only; no gold, eligibility computation or repair."""
import json

LIST_MARKER='Return exactly one JSON object with exactly one key, eligible_ids.'


def vector_prompt(list_prompt,count):
    assert type(count) is int and count>0 and list_prompt.count(LIST_MARKER)==1
    return list_prompt.split(LIST_MARKER,1)[0]+(
        'Return exactly one JSON object with exactly one key, eligible. Its value must be '
        f'an array of exactly {count} literal JSON booleans, in the same order as the '
        'stage.effective_candidates array above. For each candidate, output true if it is eligible '
        'under every local policy clause and required check, and false otherwise. '
        'Include one decision for every candidate, including candidates you would not prefer. '
        'Do not sort or reorder the candidates. Return no IDs, additional keys, explanation, '
        'or markdown. Use true/false, not numbers or strings.\n')


def unique(items):
    result={}
    for key,value in items:
        if key in result:raise ValueError('duplicate JSON key')
        result[key]=value
    return result


def parse(text,arm,public_order):
    assert public_order and len(public_order)==len(set(public_order))
    value=json.loads(text,object_pairs_hook=unique);assert type(value) is dict
    if arm=='vector':
        assert set(value)=={'eligible'};values=value['eligible']
        assert type(values) is list and len(values)==len(public_order)
        assert all(type(v) is bool for v in values),'literal JSON booleans required'
        return {'ids':[key for key,eligible in zip(public_order,values) if eligible],'strict_valid':True,'vector':values}
    assert arm=='list' and set(value)=={'eligible_ids'}
    ids=value['eligible_ids'];assert type(ids) is list and all(type(v) is str for v in ids)
    assert len(ids)==len(set(ids)) and set(ids)<=set(public_order)
    return {'ids':ids,'strict_valid':ids==sorted(ids),'vector':None}
