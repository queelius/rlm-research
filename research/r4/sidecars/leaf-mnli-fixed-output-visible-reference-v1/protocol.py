"""Only visible IDs vary; every requested tag and output schema stays fixed."""
import functools,hashlib,itertools
import study as s
MASTER=981624001;LABELS=('entailment','neutral','contradiction');ARMS=('aligned','wrong','unrelated')
with s.aliases({'study':s}):
    ancestor=s.load('visible_reference_request_ancestor',s.ANCESTOR/'protocol.py','4df068fb53854d1af4a0231579aa25ecef5eb4952e6144b769bce3026fb8f4d7')
SYSTEM=ancestor.SYSTEM
def contexts():return s.read(s.ROOT/'DATA.json')['contexts']
def context_index(context):
    ids=[r['id'] for r in context['records']]
    return next(i for i,c in enumerate(contexts()) if [r['id'] for r in c['records']]==ids)
def expected_tags(context,arm):
    if arm not in ARMS:raise ValueError(arm)
    ids=[r['id'] for r in context['records']];return ids[17:]+ids[:17]
@functools.lru_cache(maxsize=1)
def unrelated_dictionary():
    cs=contexts();tok=s.tokenizer();used={r['id'] for c in cs for r in c['records']};out={}
    for ci,c in enumerate(cs):
        values=[]
        for i,r in enumerate(c['records']):
            size=len(tok.encode(r['id'],add_special_tokens=False));nonce=0
            while True:
                tag='m'+hashlib.sha256(f'fixed-output-visible-reference:{MASTER}:{ci}:{i}:{nonce}'.encode()).hexdigest()[:12]
                if tag not in used and len(tok.encode(tag,add_special_tokens=False))==size:break
                nonce+=1
            used.add(tag);values.append(tag)
        out[str(ci)]=values
    return out
def visible_records(context,arm):
    tags=expected_tags(context,arm)
    if arm=='aligned':ids=tags
    elif arm=='wrong':ids=[r['id'] for r in context['records']]
    else:ids=unrelated_dictionary()[str(context_index(context))]
    return [dict(id=identifier,premise=r['premise'],hypothesis=r['hypothesis'],requested_tag=tag) for identifier,r,tag in zip(ids,context['records'],tags,strict=True)]
def schema(context,arm):
    tags=expected_tags(context,arm)
    return {'json':{'type':'array','minItems':48,'maxItems':48,'items':False,'prefixItems':[{'type':'object','properties':{'tag':{'type':'string','const':t},'label':{'type':'string','enum':list(LABELS)}},'required':['tag','label'],'additionalProperties':False} for t in tags]}}
ancestor.visible_records=visible_records;ancestor.schema=schema
request=ancestor.request
def plan():
    rows=[];orders=list(itertools.permutations(ARMS));indices=sorted(range(16),key=lambda ci:s.digest([MASTER,'dispatch',ci]))
    for block,ci in enumerate(indices):
        for position,arm in enumerate(orders[block%6]):
            row=dict(context_index=ci,repeat=0,seed=981624101+ci,arm=arm,decoder='exact_requested_tag',size=48,block=ci,pair_position=position,dispatch_order=len(rows));row['id']=s.digest(['fixed-output-visible-reference48',row]);rows.append(row)
    return rows
def null_row(row,reason):return dict(coordinate=row,available=False,strict_correct=None,strict_bounds=[0,48],reason=reason)
