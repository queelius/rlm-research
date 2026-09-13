"""Pure public projection and strict scalar union; no eligibility computation."""
import copy
import json

MARKER='Mechanically normalized local shard (authoritative JSON):\n'
CONTRACT='Return exactly one JSON object with exactly one key, eligible_ids.'


def unique(items):
    result={}
    for key,value in items:
        if key in result:raise ValueError('duplicate JSON key')
        result[key]=value
    return result


def normalized_public(prompt):
    assert prompt.count(MARKER)==1
    return json.JSONDecoder().raw_decode(prompt.split(MARKER,1)[1])[0]


def singleton_prompt(list_prompt,index):
    assert list_prompt.count(CONTRACT)==1
    prefix=list_prompt.split(MARKER,1)[0]
    original='ALL original candidates are retained; no eligibility decision has been made.'
    assert prefix.count(original)==1
    prefix=prefix.replace(original,'Exactly one publicly scheduled candidate is included; selection was by position only, not eligibility. No eligibility decision has been made.')
    view=copy.deepcopy(normalized_public(list_prompt));rows=view['stage']['effective_candidates']
    assert type(index) is int and 0<=index<len(rows)
    view['stage']['effective_candidates']=[rows[index]]
    suffix=('\nReturn exactly one JSON object with exactly one key, eligible. Its value must be a literal JSON boolean: '
            'true if the sole candidate is eligible under every local policy clause and required check, false otherwise. '
            'Return no IDs, array, additional keys, explanation, or markdown. Use true/false, not numbers or strings.\n')
    return prefix+MARKER+json.dumps(view,ensure_ascii=False,sort_keys=True,indent=2)+suffix


def parse_scalar(text):
    value=json.loads(text,object_pairs_hook=unique)
    assert type(value) is dict and set(value)=={'eligible'}
    assert type(value['eligible']) is bool,'literal JSON boolean required'
    return value['eligible']


def singleton_union(order,records):
    assert len(order)==len(set(order)) and set(records)<=set(range(len(order)))
    unknown=[];invalid=[];decisions={}
    for index in range(len(order)):
        record=records.get(index,{})
        if not record.get('transport_valid'):unknown.append(index);continue
        try:decisions[index]=parse_scalar(record['text'])
        except (ValueError,AssertionError,TypeError,KeyError):invalid.append(index)
    valid=not unknown and not invalid
    return dict(available=not unknown,semantic_valid=valid,strict_valid=valid,
        ids=[key for i,key in enumerate(order) if decisions[i]] if valid else None,
        unknown_candidates=unknown,invalid_candidates=invalid,observed_decisions=decisions)
