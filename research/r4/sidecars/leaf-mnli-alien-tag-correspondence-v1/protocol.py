"""Three-arm exact requested-tag control with deterministic alien aliases."""
import functools,hashlib,itertools,random
import study as s
MASTER=981612001;LABELS=('entailment','neutral','contradiction');ARMS=('matching','shift17','alien')
SYSTEM=('You are a text classification assistant. Classify every supplied input record and return only the requested final answer in the requested format. Do not write code, use tools, provide explanations, or reason aloud.')
def contexts():return s.read(s.BASE/'DATA.json')['contexts']
@functools.lru_cache(maxsize=1)
def alien_dictionary():
    cs=contexts();visible={r['id'] for c in cs for r in c['records']};tok=s.tokenizer();out={}
    for ci,c in enumerate(cs):
        shifted=[r['id'] for r in c['records']][17:]+[r['id'] for r in c['records']][:17];used=set()
        values=[]
        for i,target in enumerate(shifted):
            wanted=len(tok.encode(target,add_special_tokens=False));nonce=0
            while True:
                candidate='m'+hashlib.sha256(f'alien-mnli-v1:{ci}:{i}:{nonce}'.encode()).hexdigest()[:12]
                if candidate not in visible and candidate not in used and len(tok.encode(candidate,add_special_tokens=False))==wanted:break
                nonce+=1
            used.add(candidate);values.append(candidate)
        out[str(ci)]=values
    return out
def alien_tags(context):
    ids=[r['id'] for r in context['records']]
    matches=[i for i,c in enumerate(contexts()) if [r['id'] for r in c['records']]==ids]
    if len(matches)!=1:raise ValueError('alien context identity')
    return alien_dictionary()[str(matches[0])]
def plan():
    result=[];rng=random.Random(MASTER);blocks=list(range(16));rng.shuffle(blocks)
    rotations=[ARMS[i:]+ARMS[:i] for i in range(3)]
    for block in blocks:
        ci,repeat=divmod(block,2);order=list(rotations[(ci+repeat)%3]);
        if repeat:order.reverse()
        for position,arm in enumerate(order):
            row=dict(context_index=ci,repeat=repeat,seed=981612101+block,arm=arm,decoder='exact_requested_tag',size=48,block=block,pair_position=position,dispatch_order=len(result));row['id']=s.digest(['mnli-alien-requested-tag48',row]);result.append(row)
    return result
def expected_tags(context,arm):
    ids=[r['id'] for r in context['records']]
    if arm=='matching':return ids
    if arm=='shift17':return ids[17:]+ids[:17]
    return alien_tags(context)
def visible_records(context,arm):return [dict(id=r['id'],premise=r['premise'],hypothesis=r['hypothesis'],requested_tag=t) for r,t in zip(context['records'],expected_tags(context,arm),strict=True)]
def schema(context,arm):
    tags=expected_tags(context,arm);return {'json':{'type':'array','minItems':48,'maxItems':48,'items':False,'prefixItems':[{'type':'object','properties':{'tag':{'type':'string','const':t},'label':{'type':'string','enum':list(LABELS)}},'required':['tag','label'],'additionalProperties':False} for t in tags]}}
def request(context,row):
    records=visible_records(context,row['arm']);prompt=('For every supplied record, classify the relation of its displayed hypothesis to its displayed premise. entailment means the hypothesis must be true given the premise; contradiction means it must be false; neutral means neither conclusion follows. Do not infer the label from position, ID, or requested_tag.\nReturn exactly 48 JSON objects in one array, in displayed record order. Each object must have exactly the string fields tag then label. Copy that record\'s requested_tag exactly into tag. For label, use exactly entailment, neutral, or contradiction. No additional text.\nInput records (id, premise, hypothesis, requested_tag):\n'+s.serialize(records))
    return dict(model=s.MODEL['alias'],messages=[dict(role='system',content=SYSTEM),dict(role='user',content=prompt)],temperature=.5,top_p=1,top_k=-1,min_p=0,repetition_penalty=1,presence_penalty=0,frequency_penalty=0,seed=row['seed'],max_tokens=3072,return_token_ids=True,chat_template_kwargs={'enable_thinking':False},cache_salt=s.ROOT.name,structured_outputs=schema(context,row['arm']))
def null_row(row,reason):return dict(coordinate=row,available=False,strict_correct=None,strict_bounds=[0,48],reason=reason)
