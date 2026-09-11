"""Six-arm fresh-context output-field-order protocol."""
import study as s
MASTER=989626001;LABELS=('entailment','neutral','contradiction');GENRES=('government','slate','telephone','travel')
ARMS=tuple(r+'_'+o for r in ('wrong','alien','aligned') for o in ('tag_first','label_first'))
PRIMARY='(wrong_label_first-wrong_tag_first)-(aligned_label_first-aligned_tag_first)'
GATE={'minimum_effect':.10,'minimum_positive_contexts':12,'contexts':16,'availability_not_lower':True}
SYSTEM='You are a text classification assistant. Classify every supplied input record and return only the requested final answer in the requested format. Do not write code, use tools, provide explanations, or reason aloud.'
EXPLICIT=("For every supplied record, classify the relation of the hypothesis to the premise inside that same displayed JSON object. entailment means the hypothesis must be true given the premise; contradiction means it must be false; neutral means neither conclusion follows. requested_tag is an opaque output address and does not identify or refer to any record.\nReturn exactly 48 JSON objects in one array, in displayed record order. Each object must have exactly the string fields {order}. Copy the same object's requested_tag exactly into tag. For label, use exactly entailment, neutral, or contradiction. No additional text.\nInput records (id, premise, hypothesis, requested_tag):\n")
def contexts():return s.read(s.ROOT/'DATA.json')['contexts']
def requested_tags(context):
    ids=[r['id'] for r in context['records']];return ids[17:]+ids[:17]
def field_order(arm):
    if arm not in ARMS:raise ValueError(arm)
    return ('label','tag') if arm.endswith('label_first') else ('tag','label')
def context_index(context):
    ids=[r['id'] for r in context['records']];matches=[i for i,c in enumerate(contexts()) if [r['id'] for r in c['records']]==ids]
    if len(matches)!=1:raise ValueError('unique context required')
    return matches[0]
def visible_records(context,arm):
    relation=arm.split('_',1)[0];ids=[r['id'] for r in context['records']]
    visible=ids if relation=='wrong' else requested_tags(context) if relation=='aligned' else s.read(s.ROOT/'ALIEN_DICTIONARIES.json')[str(context_index(context))]
    return [dict(id=i,premise=r['premise'],hypothesis=r['hypothesis'],requested_tag=t) for i,r,t in zip(visible,context['records'],requested_tags(context),strict=True)]
def schema(context,arm):
    rows=[]
    for tag in requested_tags(context):
        properties={'tag':{'type':'string','const':tag},'label':{'type':'string','enum':list(LABELS)}};order=field_order(arm)
        rows.append(dict(type='object',properties={k:properties[k] for k in order},required=list(order),additionalProperties=False))
    return {'json':dict(type='array',minItems=48,maxItems=48,items=False,prefixItems=rows)}
def plan():
    rows=[]
    for ci in sorted(range(16),key=lambda i:s.digest([MASTER,'dispatch',i])):
        arms=ARMS[ci%6:]+ARMS[:ci%6]
        for pos,arm in enumerate(arms):
            row=dict(context_index=ci,repeat=0,seed=989626101+ci,arm=arm,decoder='exact_requested_tag',size=48,block=ci,pair_position=pos,dispatch_order=len(rows));row['id']=s.digest(['mnli-field-order-replication-v1',row]);rows.append(row)
    return rows
def request(context,row):
    prompt=EXPLICIT.format(order=' then '.join(field_order(row['arm'])))+s.serialize(visible_records(context,row['arm']))
    return dict(model=s.MODEL['alias'],messages=[dict(role='system',content=SYSTEM),dict(role='user',content=prompt)],temperature=.5,top_p=1,top_k=-1,min_p=0,repetition_penalty=1,presence_penalty=0,frequency_penalty=0,seed=row['seed'],max_tokens=3072,return_token_ids=True,chat_template_kwargs={'enable_thinking':False},cache_salt=s.ROOT.name,structured_outputs=schema(context,row['arm']))
def null_row(row,reason):return dict(coordinate=row,available=False,strict_correct=None,strict_bounds=[0,48],reason=reason)

