import json
import study as s
MASTER=998477001; LABELS=('entailment','neutral','contradiction'); RELATIONS=('wrong','alien','aligned'); CELLS=('AA','AB','BA','BB')
def contexts():return s.read(s.PRIOR/'DATA.json')['contexts']
def tags(c,setname):return ['k'+s.digest([MASTER,setname,c['index'],r['id']])[:12] for r in c['records']]
def visible_ids(c,relation):
 ids=[r['id'] for r in c['records']]
 if relation=='wrong':return ids
 if relation=='aligned':return ids[17:]+ids[:17]
 return s.read(s.PRIOR/'ALIEN_DICTIONARIES.json')[str(c['index'])]
def plan():
 out=[]
 for c in contexts():
  for relation in RELATIONS:
   for cell in CELLS:
    r=dict(context_index=c['index'],relation=relation,cell=cell,arm=f'{relation}_{cell}',input_set=cell[0],output_set=cell[1],seed=998477101+c['index'],size=48);r['id']=s.digest([s.ROOT.name,r]);out.append(r)
 return out
def request(c,r):
 inp=tags(c,r['input_set']);out=tags(c,r['output_set']);ids=visible_ids(c,r['relation'])
 rows=[dict(id=i,input_tag=t,premise=x['premise'],hypothesis=x['hypothesis']) for i,t,x in zip(ids,inp,c['records'],strict=True)]
 prompt=('Classify each hypothesis against the premise in that same displayed object. entailment means the hypothesis must be true given the premise; contradiction means it must be false; neutral means neither follows. Return exactly 48 objects in displayed order. Output position i always labels displayed input object i. input_tag and answer_tag are opaque bookkeeping; neither refers to another record. Copy the grammar-required answer_tag and use label entailment, neutral, or contradiction. Input records:\n'+json.dumps(rows,separators=(',',':')))
 items=[{'type':'object','properties':{'answer_tag':{'type':'string','const':t},'label':{'type':'string','enum':list(LABELS)}},'required':['answer_tag','label'],'additionalProperties':False} for t in out]
 return dict(model=s.MODEL['alias'],messages=[{'role':'system','content':'Return only the requested JSON array; no tools or explanation.'},{'role':'user','content':prompt}],temperature=.5,top_p=1,top_k=-1,min_p=0,repetition_penalty=1,presence_penalty=0,frequency_penalty=0,seed=r['seed'],max_tokens=3072,return_token_ids=True,chat_template_kwargs={'enable_thinking':False},cache_salt=s.ROOT.name,structured_outputs={'json':{'type':'array','minItems':48,'maxItems':48,'items':False,'prefixItems':items}})
def null_row(r,reason):return dict(coordinate=r,available=False,strict_correct=None,reason=reason)
