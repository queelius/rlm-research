"""Stable-anchor scoring with tokenizer-dependent native authentication."""
import protocol as p,study as s
module=s.load('mistral_stable_scoring',s.PRIOR/'scoring.py','7f24a53c62544a48881b880a982497c00bccf9e4b78014654121ceb3dc7311eb',{'study':s,'protocol':p});score,missing=module.score,module.missing
def verified_response(raw,expected_prompt_ids,tokenizer):
 outgoing=((raw.get('choices') or [{}])[0].get('token_ids') or [])
 if outgoing and outgoing[-1] in (151643,151645):raise ValueError('foreign Qwen terminal token in Mistral response')
 return module.verified_response(raw,expected_prompt_ids,tokenizer)
def summarize(rows):
 cells={}
 for arm in p.ARMS:
  selected=[x for x in rows if x['coordinate']['arm']==arm];available=[x for x in selected if x['score']['available']];cells[arm]={'planned':len(selected),'available':len(available),'null':len(selected)-len(available),'strict_correct':sum(x['score']['strict_correct'] for x in available),'late_correct':sum(x['score']['late_correct'] for x in available),'contract_valid':sum(bool(x['score']['contract_valid']) for x in available)}
 differences={}
 for anchor in p.ANCHORS[1:]:
  values=[]
  for index in range(16):
   delta=0;known=0
   for relation in p.RELATIONS:
    left=next((x for x in rows if x['coordinate']['context_index']==index and x['coordinate']['arm']==f'{relation}_{anchor}'),None);right=next((x for x in rows if x['coordinate']['context_index']==index and x['coordinate']['arm']==f'{relation}_labels_only'),None)
    if left and right and left['score']['available'] and right['score']['available']:delta+=left['score']['late_correct']-right['score']['late_correct'];known+=32
   values.append({'context_index':index,'late_difference':delta,'known_late_labels':known})
  known=[x for x in values if x['known_late_labels']==96];differences[anchor]={'contexts':values,'complete_contexts':len(known),'positive_contexts':sum(x['late_difference']>0 for x in known),'paired_gain_pp':100*sum(x['late_difference'] for x in known)/(96*len(known)) if known else None}
 return {'cells':cells,'primary':differences,'gate':{'positive_contexts_required':12,'no_availability_loss':True},'cluster_unit':'16 paired exposed contexts; calls and labels are dependent'}
