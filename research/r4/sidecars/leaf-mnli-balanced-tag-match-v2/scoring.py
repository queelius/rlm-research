"""V2 scoring with intended-position and correctly directed named-reference diagnostics."""
import protocol as p,study as s
base=s.load('tag_match_v1_scoring',s.V1/'scoring.py','30c17e0218b5b946f396ca0de1a019cae76ae56e9c653ca36a66982fabbd5f9a',{'study':s,'protocol':p})
verified_response=base.verified_response;missing=base.missing;summarize=base.summarize
def score(message,context,arm):
 result=base.score(message,context,arm)
 if not result.get('contract_valid'):return result
 row=arm if isinstance(arm,dict) else next(x for x in p.plan() if x['arm']==arm and x['context_index']==context['index'])
 visible={identifier:record['gold_label'] for identifier,record in zip(p.visible_ids(context,row['relation']),context['records'],strict=True)}
 targets=[visible.get(address) for address in p.requested_tags(context)]
 result['named_record_correct']=sum(pred==gold for pred,gold in zip(result['predictions'],targets,strict=True)) if all(x is not None for x in targets) else None
 return result
