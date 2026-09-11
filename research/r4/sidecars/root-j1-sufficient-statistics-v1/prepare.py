import copy,json
from pathlib import Path
from tokenizers import Tokenizer
import study as s
TOKENIZER=Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554/tokenizer.json")
DEFINITIONS="""human being: a person, organization, group of people, role, title, or person description.
location: a geographic place.
abbreviation: a shortened form or its expanded wording.
entity: a nonhuman, nongeographic thing or name.
description and abstract concept: a definition, explanation, reason, or manner.
numeric value: a quantity, count, measurement, date, duration, rank, or numerical code."""
def prompt(records,spec):
 visible=[{"id":r["id"],"text":r["text"],"user":r["user"],"weight":r["weight"]} for r in records]
 return f"""Use these answer-type definitions:\n{DEFINITIONS}\nFor each eligible user in {json.dumps(spec['users'],separators=(',',':'))}, inspect only the records below and return: (1) has_target_a, true iff at least one of that user's records asks for answer type {json.dumps(spec['target'])}; and (2) target_b_weight_sum, the integer sum of weights of that user's records asking for answer type {json.dumps(spec['target_b'])}. Return exactly one JSON object with every eligible user once and no other users. Each value must be an object with exactly has_target_a (boolean) and target_b_weight_sum (nonnegative integer).\nRecords: {json.dumps(visible,separators=(',',':'),ensure_ascii=False)}"""
def build(write=True):
 oldplan=s.read(s.CEILING/"inputs/PLAN.json");oldreq=s.read(s.CEILING/"inputs/REQUESTS.json");public=s.read(s.CEILING/"inputs/PUBLIC.json");host=s.read(s.CEILING/"inputs/HOST_GOLD.json");records={e["id"]:{r["id"]:r for r in e["records"]} for e in public};tok=Tokenizer.from_file(str(TOKENIZER));template=copy.deepcopy(next(iter(oldreq.values())));decoded=tok.decode(template["token_ids"],skip_special_tokens=False);marker="<|im_start|>user\n";start=decoded.index(marker)+len(marker);end=decoded.index("<|im_end|>\n<|im_start|>assistant",start);prefix,suffix=decoded[:start],decoded[end:];plan=[];requests={}
 for old in oldplan:
  row={k:v for k,v in old.items() if k!="id"};row["record_ids"]=row.pop("ids");row["ids"]=list(row["users"]);row["n"]=len(row["record_ids"]);row["interface"]="public_j1_sufficient_statistics";row["id"]=s.digest([s.ROOT.name,row]);plan.append(row)
  body=copy.deepcopy(template);body["token_ids"]=tok.encode(prefix+prompt([records[row["context_id"]][k] for k in row["record_ids"]],row)+suffix,add_special_tokens=False).ids;body["sampling_params"]["seed"]=row["seed"]
  item={"type":"object","properties":{"has_target_a":{"type":"boolean"},"target_b_weight_sum":{"type":"integer","minimum":0}},"required":["has_target_a","target_b_weight_sum"],"additionalProperties":False};body["sampling_params"]["structured_outputs"]["json"]={"type":"object","properties":{u:item for u in sorted(row["users"])},"required":row["users"],"additionalProperties":False}
  if len(body["token_ids"])+2048>8192:raise ValueError("context admission")
  requests[row["id"]]=body
 value={"plan":plan,"requests":requests,"public":public,"host":host}
 if write:
  for n,x in (("PLAN.json",plan),("REQUESTS.json",requests),("PUBLIC.json",public),("HOST_GOLD.json",host)):s.write(s.ROOT/"inputs"/n,x)
  s.write(s.ROOT/"CPU_INPUT_NATIVE.json",{"planned_calls":40,"episodes":8,"same_ceiling_chunks_seeds_order":True,"eligible_users_only":True,"selection_or_prompt_uses_gold":False,"bundle":["task_aware_prompt","statistics_format","LLM_summation"]})
 return value
if __name__=="__main__":build()

