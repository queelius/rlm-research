"""Common requested-tag prompt and fixed paired MNLI32 plan."""
import mn_study as s

MASTER=981621001
LABELS=('entailment','neutral','contradiction')
ARMS=('matching','constant')
SYSTEM=('You are a text classification assistant. Classify every supplied input record and return '
        'only the requested final answer in the requested format. Do not write code, use tools, '
        'provide explanations, or reason aloud.')

def contexts():return s.read(s.ROOT/'DATA.json')['contexts']
def plan():
    result=[]
    for ci in sorted(range(16),key=lambda i:s.digest([MASTER,'dispatch',i])):
        order=ARMS if ci%2==0 else tuple(reversed(ARMS))
        for position,arm in enumerate(order):
            row=dict(context_index=ci,repeat=0,seed=981621101+ci,arm=arm,decoder='exact_requested_tag',
                size=48,block=ci,pair_position=position,dispatch_order=len(result))
            row['id']=s.digest(['mnli-new-context32',row]);result.append(row)
    return result

def expected_tags(context,arm):
    ids=[r['id'] for r in context['records']]
    if arm not in ARMS:raise ValueError('matching/constant only')
    return ids if arm=='matching' else [s.read(s.ROOT/'DATA.json')['constant']]*len(ids)

def visible_records(context,arm):
    tags=expected_tags(context,arm)
    return [dict(id=r['id'],premise=r['premise'],hypothesis=r['hypothesis'],requested_tag=t)
            for r,t in zip(context['records'],tags,strict=True)]

def schema(context,arm):
    tags=expected_tags(context,arm)
    return {'json':{'type':'array','minItems':len(tags),'maxItems':len(tags),'items':False,
        'prefixItems':[{'type':'object','properties':{'tag':{'type':'string','const':tag},
        'label':{'type':'string','enum':list(LABELS)}},'required':['tag','label'],
        'additionalProperties':False} for tag in tags]}}

def request(context,row):
    records=visible_records(context,row['arm'])
    prompt=('For every supplied record, classify the relation of its displayed hypothesis to its displayed premise. '
        'entailment means the hypothesis must be true given the premise; contradiction means it must be false; '
        'neutral means neither conclusion follows. Do not infer the label from position, ID, or requested_tag.\n'
        f'Return exactly {len(records)} JSON objects in one array, in displayed record order. Each object must have '
        'exactly the string fields tag then label. Copy that record\'s requested_tag exactly into tag. For label, use '
        'exactly entailment, neutral, or contradiction. No additional text.\n'
        'Input records (id, premise, hypothesis, requested_tag):\n'+s.serialize(records))
    return dict(model=s.MODEL['alias'],messages=[dict(role='system',content=SYSTEM),dict(role='user',content=prompt)],
        temperature=.5,top_p=1,top_k=-1,min_p=0,repetition_penalty=1,presence_penalty=0,frequency_penalty=0,
        seed=row['seed'],max_tokens=3072,return_token_ids=True,chat_template_kwargs={'enable_thinking':False},
        cache_salt=s.ROOT.name,structured_outputs=schema(context,row['arm']))

def null_row(row,reason):return dict(coordinate=row,available=False,strict_correct=None,strict_bounds=[0,row['size']],reason=reason)
