"""Reuse sealed exact-wire admission; only two turns and model-specific token checks."""
from types import ModuleType
import study as s

SOURCE=s.MUSIQUE/'native_audit.py'


def capture(directory,coordinates):
    source=SOURCE.read_text()
    before="limit=1 if coordinate['arm']=='question_only' else 6"
    assert source.count(before)==1
    source=source.replace(before,'limit=2').replace('no seventh physical request','no third physical request')
    source=source.replace('musique_physical_call_cap','controller_physical_call_cap').replace('musique_context_cap','controller_context_cap')
    check="            if evidence['action_tokens']>1024:raise ValueError('native output exceeded cap')"
    assert source.count(check)==1
    source=source.replace(check,check+'\n            validate_model_tokens(coordinate, payload, wire, body)')
    module=ModuleType('controller_screen_native_wire');module.__dict__['validate_model_tokens']=validate_model_tokens
    with s.aliases({'musique_study':s},s.ROOT):exec(compile(source,str(SOURCE)+':two-turn-controller','exec'),module.__dict__)
    return module.capture(directory,coordinates)


def validate_model_tokens(coordinate,payload,wire,body):
    arm=coordinate['arm'];tokenizer=s.tokenizer(arm)
    ids=payload['tokens']['completion_ids'];prompt=payload['tokens']['prompt_ids']
    assert all(type(i)is int and 0<=i<len(tokenizer) for i in ids+prompt)
    choice=wire['choices'][0]
    assert choice['finish_reason'] in ('stop','length')
    assert choice['finish_reason']!='stop' or ids[-1] in s.renderer(arm).get_stop_token_ids()
    assert wire['usage']['prompt_tokens']==len(prompt) and wire['usage']['completion_tokens']==len(ids)
    assert body['model']==s.MODELS[arm]['alias']
