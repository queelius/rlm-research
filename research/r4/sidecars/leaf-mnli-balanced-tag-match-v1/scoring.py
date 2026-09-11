import json,protocol as p,study as s
native=s.load('balanced_native',s.SIDE/'leaf-role-tool-contract-v1/scoring_v2.py','8028956dfe19b05097b5cd0f80b64c1a5b8f966885d0704dbfb7dc5d3dee0236',{'study':s})
verified_response=native.verified_response
def unique(pairs):
 out={}
 for key,value in pairs:
  if key in out:raise ValueError('duplicate object key')
  out[key]=value
 return out
def missing(c):return dict(available=False,strict_correct=None,early_correct=None,late_correct=None,contract_valid=None,shape_valid=None,key_position_matches=None,named_record_correct=None,predictions=None,reason='unavailable')
def score(m,c,arm):
 z=dict(available=True,strict_correct=0,early_correct=0,late_correct=0,contract_valid=False,shape_valid=False,key_position_matches=0,named_record_correct=None,predictions=None,reason='whole_contract_failure')
 try:
  row=arm if isinstance(arm,dict) else next(x for x in p.plan() if x['arm']==arm and x['context_index']==c['index'])
  v=json.loads(m['content'],object_pairs_hook=unique,parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)));want=p.tags(c,row['output_set'])
  if len(v)!=48 or any(list(x)!=['answer_tag','label'] or x['answer_tag']!=want[i] or x['label'] not in p.LABELS for i,x in enumerate(v)):return z
  pred=[x['label'] for x in v];ok=[a==b['gold_label'] for a,b in zip(pred,c['records'],strict=True)]
  named=None
  if row['relation']!='alien':
   gold={x['id']:x['gold_label'] for x in c['records']};named=sum(x==gold[i] for x,i in zip(pred,p.visible_ids(c,row['relation']),strict=True))
  return dict(available=True,strict_correct=sum(ok),early_correct=sum(ok[:16]),late_correct=sum(ok[16:]),contract_valid=True,shape_valid=True,key_position_matches=48,named_record_correct=named,predictions=pred,reason='strict_contract')
 except Exception:return z
def summarize(rows):
 cells={}
 for relation in p.RELATIONS:
  for cell in p.CELLS:
   values=[x for x in rows if x['coordinate']['relation']==relation and x['coordinate']['cell']==cell];available=[x for x in values if x['score']['available']]
   cells[f'{relation}_{cell}']={'planned':len(values),'available':len(available),'null':len(values)-len(available),'contract_valid':sum(bool(x['score']['contract_valid']) for x in available),'strict_correct':sum(x['score']['strict_correct'] for x in available),'late_correct':sum(x['score']['late_correct'] for x in available),'named_record_correct':sum(x['score']['named_record_correct'] for x in available if x['score']['named_record_correct'] is not None)}
 effects={}
 for relation in p.RELATIONS:
  values=[]
  for index in range(16):
   q={x['coordinate']['cell']:x['score'] for x in rows if x['coordinate']['relation']==relation and x['coordinate']['context_index']==index}
   known=all(x in q and q[x]['available'] and type(q[x]['late_correct']) is int for x in p.CELLS)
   values.append({'context_index':index,'available':known,'late_match_minus_nonmatch_correct':q['AA']['late_correct']+q['BB']['late_correct']-q['AB']['late_correct']-q['BA']['late_correct'] if known else None})
  known=[x['late_match_minus_nonmatch_correct'] for x in values if x['available']]
  effects[relation]={'contexts':values,'known_contexts':len(known),'positive_contexts':sum(x>0 for x in known),'effect_pp':100*sum(known)/(64*len(known)) if known else None}
 known=[x['late_match_minus_nonmatch_correct'] for v in effects.values() for x in v['contexts'] if x['available']]
 pooled=[]
 for index in range(16):
  parts=[effects[r]['contexts'][index] for r in p.RELATIONS];pooled.append({'context_index':index,'available':all(x['available'] for x in parts),'late_match_minus_nonmatch_correct':sum(x['late_match_minus_nonmatch_correct'] for x in parts) if all(x['available'] for x in parts) else None})
 pknown=[x['late_match_minus_nonmatch_correct'] for x in pooled if x['available']];effect=100*sum(pknown)/(192*len(pknown)) if pknown else None;positive=sum(x>0 for x in pknown);available_gate=all(x['available']>=15 for x in cells.values())
 return {'cells':cells,'primary':{'population':'positions 17 through 48','estimand':'mean(AA,BB)-mean(AB,BA), pooled over relations and contexts','known_context_relation_units':len(known),'known_contexts':len(pknown),'effect_pp':effect,'positive_contexts':positive,'context_effects':pooled,'relation_effects':effects,'promotion_gate':{'minimum_effect_pp':10,'minimum_positive_contexts':12,'availability_each_cell':15,'availability_pass':available_gate,'promote':effect is not None and effect>=10 and positive>=12 and available_gate}},'interpretation':{'grammar_forces_answer_tags':True,'key_fidelity_not_evidence_of_free_copying':True,'encoding_package_not_mechanism_isolation':True}}
