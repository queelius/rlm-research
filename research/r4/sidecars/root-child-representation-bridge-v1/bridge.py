"""Public-only request transformation and broker projection; never native token repair."""
import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path

try:
    from rlm import _representation_batch as batch
except ImportError:
    path=Path(__file__).resolve().parents[1]/'adaptive-filter-pilot-v1/batch_contract.py'
    if hashlib.sha256(path.read_bytes()).hexdigest()!='d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88':raise ValueError('public contract changed')
    spec=importlib.util.spec_from_file_location('representation_batch',path);batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)

LABELS=list(batch.LABELS)
def encoded(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def digest(v):return hashlib.sha256(encoded(v).encode()).hexdigest()

def match_public(prompt,records):
    if not isinstance(prompt,str) or prompt.count('\nRecords: ')!=1:return None
    try:
        rows=json.loads(prompt.split('\nRecords: ')[1]);ids=[r['id'] for r in rows]
        public={r['id']:r for r in records};selected=[public[i] for i in ids]
        if not ids or len(ids)!=len(set(ids)) or batch.request_for(selected)!=prompt:return None
        return {'ids':ids,'records':selected,'original_request':prompt}
    except (ValueError,KeyError,TypeError):return None

def child_prompt(records,arm):
    if arm not in ('array','map'):raise ValueError('unknown representation')
    output=('Return only one JSON object mapping every supplied id exactly once to one label. No missing or extra ids.' if arm=='map'
        else f'Return only one JSON array of exactly {len(records)} labels in supplied record order. No missing or extra labels.')
    rows=[{'id':r['id'],'text':r['text']} for r in records]
    return ('Classify the type of answer requested by each question using these TREC definitions:\n'+batch.DEFINITIONS+
            output+' Allowed labels: '+encoded(LABELS)+'\nRecords: '+encoded(rows))

def schema(ids,arm):
    item={'type':'string','enum':LABELS[:]}
    if arm=='map':return {'type':'object','properties':{i:dict(item) for i in ids},'required':ids[:],'additionalProperties':False}
    if arm=='array':return {'type':'array','items':item,'minItems':len(ids),'maxItems':len(ids)}
    raise ValueError('unknown representation')

def project(raw,ids,arm):
    if arm=='map':value=batch.strict_map(raw,ids)
    elif arm=='array':
        value=json.loads(raw)
        if not isinstance(value,list) or len(value)!=len(ids) or any(not isinstance(v,str) or v not in LABELS for v in value):raise ValueError('invalid exact canonical array')
        value=dict(zip(ids,value,strict=True))
    else:raise ValueError('unknown representation')
    return encoded({i:value[i] for i in ids})

class Bridge:
    def __init__(self,root_id,config,path):
        self.root_id=root_id;self.config=config;self.path=path;self.pending={};self.deliveries={}
    def log(self,event):
        with self.path.open('a') as stream:stream.write(encoded({'coordinate':self.config['coordinate'],'root_invocation':self.root_id,**event})+'\n')
    def begin(self,parent,child,prompt,depth):
        match=match_public(prompt,self.config['records']) if parent==self.root_id and depth==1 else None
        actual=child_prompt(match['records'],self.config['arm']) if match else prompt
        value={'event':'invocation','parent_invocation':parent,'child_invocation':child,'depth':depth,'eligible':match is not None,
               'original_request':prompt,'actual_child_prompt':actual,'representation':self.config['arm'],'ids':match['ids'] if match else []}
        self.pending[child]=value;self.log(value);return actual
    def finish(self,task,parent,child,prompt,result,depth):
        event={**self.pending.pop(child),'event':'child_result','raw_answer':result.answer,'projection_valid':None,'projection_error':None}
        projected=result
        if event['eligible']:
            try:
                answer=project(result.answer,event['ids'],self.config['arm'])
                projected=dataclasses.replace(result,answer=answer);event['projection_valid']=True
            except (ValueError,TypeError) as error:
                event['projection_valid']=False;event['projection_error']=type(error).__name__+': '+str(error)
        event['broker_answer']=projected.answer
        self.log(event);self.deliveries[task]=event;return projected
    def deliver(self,task):
        event=self.deliveries.pop(task,None)
        if event:self.log({**event,'event':'delivered'})
