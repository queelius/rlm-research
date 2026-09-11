"""Corrected active three-reference balanced tag-match protocol."""
import study as s
base=s.load('tag_match_v1_protocol',s.V1/'protocol.py','65c70d7efa8e9c204eb45635c73ed925aa2726522ea66b693818e49408608ca9',{'study':s})
MASTER=base.MASTER;LABELS=base.LABELS;RELATIONS=base.RELATIONS;CELLS=base.CELLS
contexts=base.contexts;tags=base.tags;visible_ids=base.visible_ids;null_row=base.null_row
def requested_tags(c):
 ids=[x['id'] for x in c['records']];return ids[17:]+ids[:17]
def plan():
 out=[]
 for c in contexts():
  order=CELLS[c['index']%4:]+CELLS[:c['index']%4]
  for relation_index,relation in enumerate(RELATIONS):
   for pair_position,cell in enumerate(order):
    row={'context_index':c['index'],'relation':relation,'cell':cell,'arm':f'{relation}_{cell}','input_set':cell[0],'output_set':cell[1],'seed':998477101+c['index'],'size':48,'pair_position':pair_position,'dispatch_order':len(out),'cell_rotation':c['index']%4,'relation_position':relation_index};row['id']=s.digest([s.ROOT.name,row]);out.append(row)
 return out
def request(c,row):
 inp=tags(c,row['input_set']);out=tags(c,row['output_set']);ids=visible_ids(c,row['relation']);requested=requested_tags(c)
 records=[{'id':identifier,'input_tag':key,'requested_tag':address,'premise':record['premise'],'hypothesis':record['hypothesis']} for identifier,key,address,record in zip(ids,inp,requested,c['records'],strict=True)]
 prompt=('Classify each hypothesis against the premise in that same displayed object. entailment means the hypothesis must be true given the premise; contradiction means it must be false; neutral means neither follows. Return exactly 48 objects in displayed order. Output position i always labels displayed input object i. requested_tag is an opaque output address and does not identify or change which displayed record to classify. input_tag and answer_tag are opaque bookkeeping; neither refers to another record. Copy the grammar-required answer_tag and use label entailment, neutral, or contradiction. Input records:\n'+s.serialize(records))
 items=[{'type':'object','properties':{'answer_tag':{'type':'string','const':key},'label':{'type':'string','enum':list(LABELS)}},'required':['answer_tag','label'],'additionalProperties':False} for key in out]
 return {'model':s.MODEL['alias'],'messages':[{'role':'system','content':'Return only the requested JSON array; no tools or explanation.'},{'role':'user','content':prompt}],'temperature':.5,'top_p':1,'top_k':-1,'min_p':0,'repetition_penalty':1,'presence_penalty':0,'frequency_penalty':0,'seed':row['seed'],'max_tokens':3072,'return_token_ids':True,'chat_template_kwargs':{'enable_thinking':False},'cache_salt':s.ROOT.name,'structured_outputs':{'json':{'type':'array','minItems':48,'maxItems':48,'items':False,'prefixItems':items}}}
