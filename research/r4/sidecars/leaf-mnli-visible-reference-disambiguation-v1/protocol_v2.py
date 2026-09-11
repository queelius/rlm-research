"""Additive full 3 relation x 2 wording allocation over frozen draft contexts."""
import protocol as v1

s=v1.s;MASTER=v1.MASTER;LABELS=v1.LABELS;SYSTEM=v1.SYSTEM;LEGACY=v1.LEGACY;EXPLICIT=v1.EXPLICIT
RELATIONS=('wrong','alien','aligned')
ARMS=('wrong_legacy','wrong_explicit_slot','alien_legacy','alien_explicit_slot','aligned_legacy','aligned_explicit_slot')
contexts=v1.contexts;context_index=v1.context_index;requested_tags=v1.requested_tags;alien_dictionary=v1.alien_dictionary
def expected_tags(context,arm):
    del arm
    return requested_tags(context)
def visible_ids(context,arm):
    relation=arm.split('_',1)[0];ids=[r['id'] for r in context['records']]
    if relation=='wrong':return ids
    if relation=='alien':return alien_dictionary()[str(context_index(context))]
    if relation=='aligned':return requested_tags(context)
    raise ValueError(arm)
def visible_records(context,arm):
    return [dict(id=i,premise=r['premise'],hypothesis=r['hypothesis'],requested_tag=t) for i,r,t in zip(visible_ids(context,arm),context['records'],requested_tags(context),strict=True)]
def schema(context,arm):return v1.schema(context,arm)
def plan():
    rows=[];order=sorted(range(8),key=lambda ci:s.digest([MASTER,'dispatch-v2',ci]))
    for ci in order:
        arms=ARMS[ci%6:]+ARMS[:ci%6]
        for position,arm in enumerate(arms):
            row=dict(context_index=ci,repeat=0,seed=981626101+ci,arm=arm,decoder='exact_requested_tag',size=48,block=ci,pair_position=position,dispatch_order=len(rows));row['id']=s.digest(['mnli-visible-reference-disambiguation48-v2',row]);rows.append(row)
    return rows
def request(context,row):
    prefix=LEGACY if row['arm'].endswith('legacy') else EXPLICIT
    prompt=prefix+s.serialize(visible_records(context,row['arm']))
    return dict(model=s.MODEL['alias'],messages=[dict(role='system',content=SYSTEM),dict(role='user',content=prompt)],temperature=.5,top_p=1,top_k=-1,min_p=0,repetition_penalty=1,presence_penalty=0,frequency_penalty=0,seed=row['seed'],max_tokens=3072,return_token_ids=True,chat_template_kwargs={'enable_thinking':False},cache_salt=s.ROOT.name,structured_outputs=schema(context,row['arm']))
def null_row(row,reason):return v1.null_row(row,reason)
