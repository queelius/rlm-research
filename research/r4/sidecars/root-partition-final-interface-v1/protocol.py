"""Syntax/domain intervention and no-repair strict array scoring."""
from copy import deepcopy
import json

CUSTOMERS=[f'c{i:02}' for i in range(1,13)]

def request(source,seed,decoder,model):
    body=dict(model=model,messages=deepcopy(source['messages']),cache_salt='0',return_token_ids=True,
        temperature=.6,top_p=.95,top_k=-1,min_p=0.,repetition_penalty=1.,presence_penalty=0.,frequency_penalty=0.,
        max_tokens=2560,seed=seed)
    if decoder=='exact':body['structured_outputs']={'json':{'type':'array','items':{'type':'string','enum':CUSTOMERS[:]}}}
    elif decoder!='free':raise ValueError('unknown decoder')
    return body

def score(content,gold,finish,available=True):
    result=dict(available=available,reward=None,valid=None,answer=None,finish_reason=finish,length=finish=='length')
    if not available:return result
    try:
        value=json.loads(content)
        valid=isinstance(value,list) and all(isinstance(x,str) and x in CUSTOMERS for x in value) and len(value)==len(set(value)) and value==sorted(value)
    except (TypeError,ValueError):value=None;valid=False
    result.update(valid=valid,reward=int(valid and value==gold),answer=value if valid else None)
    return result

def acquisition_cost(calls):
    return dict(calls=len(calls),input_tokens=sum(x['prompt_tokens'] for x in calls),output_tokens=sum(x['output_tokens'] for x in calls),seconds=sum(x['seconds'] for x in calls),physical_new=False)
