import copy
import json
import pytest

def test_actual_wide_native_response_and_smaller_native_prefix():
    import bg_study as s
    import bg_protocol as p
    import importlib.util
    spec=importlib.util.spec_from_file_location('batch_granularity_local_prepare_fixture',s.ROOT/'prepare.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);requests=module.requests
    renderer,tokenizer=s.renderer();contexts=s.read(s.ROOT/'inputs/PUBLIC.json');templates=s.read(s.ROOT/'inputs/TEMPLATES.json')
    plan,bodies,checks=requests(contexts,templates,tokenizer)
    assert len(plan)==76 and max(r['input_tokens'] for r in checks)==3763
    prior=s.read(templates[0][0]['path']);parsed=p.native(prior['response'],prior['body'],renderer)
    ids=plan[0]['ids'];gold=s.read(s.ROOT/'inputs/HOST_GOLD.json')[contexts[0]['id']]['labels']
    scored=p.score(parsed['content'],ids,gold,True,parsed['tool_calls'])
    assert scored['complete_map'] and scored['strict_correct']==89
    small=next(r for r in plan if r['arm']=='S');body=bodies[small['id']]
    text=tokenizer.decode(body['token_ids']);offset=text.rindex('Records: ')+len('Records: ');records=json.JSONDecoder().raw_decode(text[offset:])[0]
    assert len(records)==16 and list(records[0])==['id','text']
    assert [r['id'] for r in records]==small['ids'] and 'weight' not in records[0]
    changed=copy.deepcopy(contexts)
    for ctx in changed:
        for i,r in enumerate(ctx['records']):r['private_label']=p.CATEGORIES[(i*5+2)%6]
    assert requests(changed,templates,tokenizer)[1]==bodies

def test_native_wrong_tokens_rejected():
    import bg_study as s
    import bg_protocol as p
    renderer,_=s.renderer();raw=s.read(s.read(s.ROOT/'inputs/TEMPLATES.json')[0][0]['path']);response=copy.deepcopy(raw['response']);response['choices'][0]['token_ids'].pop()
    with pytest.raises(ValueError):p.native(response,raw['body'],renderer)

def test_authored_native_empty_and_tool_route_are_observed_invalid():
    import bg_protocol as p
    assert p.score(None,['x'],{'x':'entity'},True)['strict_correct']==0
    assert p.score('{"x":"entity"}',['x'],{'x':'entity'},True,True)['strict_correct']==0
