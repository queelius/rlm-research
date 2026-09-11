import hashlib,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).parent;SIDE=ROOT.parent;ATTEMPT=ROOT/"outputs/attempt-001";V1=SIDE/"root-j1-sufficient-statistics-v1";CEILING=SIDE/"root-lambda-supplied-plan-ceiling-v1";NATIVE=Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+".partial");q.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+"\n");os.replace(q,p)
def base():
 spec=importlib.util.spec_from_file_location("ss_v2_base_study",V1/"study.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def dependencies():return base().dependencies()
def renderer():return base().renderer()
def binding():
 x=base().binding();x["study"]=ROOT.name;x["campaign_id"]=ROOT.name;x["batch_granularity"]["planned"]=40;return x
def verify():
 r=read(ROOT/"READY.json");assert digest({k:v for k,v in r.items() if k!="identity"})==r["identity"]
 for g in ("source_sha256","input_sha256"):
  for p,h in r[g].items():
   if sha(p)!=h:raise ValueError("closure changed "+p)
 return r

