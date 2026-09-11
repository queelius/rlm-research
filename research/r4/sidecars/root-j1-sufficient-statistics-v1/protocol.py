import importlib.util,json
from pathlib import Path
SOURCE=Path(__file__).parent.parent/"root-lambda-supplied-plan-ceiling-v1/protocol.py";spec=importlib.util.spec_from_file_location("ss_ceiling_protocol",SOURCE);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);native=base.native;reduce_j1=base.reduce_j1
def unique(ps):
 d={}
 for k,v in ps:
  if k in d:raise ValueError("duplicate key")
  d[k]=v
 return d
def score(content,ids,gold,authenticated,tool_calls=False):
 out={"available":bool(authenticated),"complete_map":False,"strict_correct":None,"stats":None,"labels":None,"canonical_id_matches":None if not authenticated else 0,"output_order_equal":None,"invalid_reason":None}
 if not authenticated:return out
 try:
  if tool_calls:raise ValueError("wrong tool route")
  value=json.loads(content,object_pairs_hook=unique)
  if not isinstance(value,dict) or set(value)!=set(ids) or len(ids)!=len(set(ids)):raise ValueError("missing/extra/duplicate user")
  for user,item in value.items():
   if not isinstance(item,dict) or set(item)!={"has_target_a","target_b_weight_sum"}:raise ValueError("invalid fields")
   if type(item["has_target_a"]) is not bool or type(item["target_b_weight_sum"]) is not int or item["target_b_weight_sum"]<0:raise ValueError("invalid types")
  out.update(complete_map=True,stats=value,canonical_id_matches=len(ids),output_order_equal=list(value)==ids)
 except (ValueError,TypeError) as e:out["invalid_reason"]=str(e)
 return out
def merge_chunks(rows,users):
 if any(not isinstance(r,dict) or "score" not in r or not r["score"].get("available") for r in rows):return {"status":"null","available":False,"valid":False,"answer":None}
 if any(not r["score"].get("complete_map") for r in rows):return {"status":"observed_invalid","available":True,"valid":False,"answer":None}
 flags={u:False for u in users};sums={u:0 for u in users}
 for r in rows:
  st=r["score"]["stats"]
  for u in users:flags[u]=flags[u] or st[u]["has_target_a"];sums[u]+=st[u]["target_b_weight_sum"]
 return {"status":"valid","available":True,"valid":True,"answer":sum(sums[u] for u in users if flags[u]),"has_target_a":flags,"target_b_weight_sum":sums}

