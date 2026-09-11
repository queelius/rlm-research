"""Additive V2 binding; V1 remains sealed and unlaunched."""
import contextlib,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;V1=SIDE/'leaf-mnli-balanced-tag-match-v1';PRIOR=SIDE/'leaf-mnli-stable-anchor-vs-sequence-counting-v1';ATTEMPT=ROOT/'outputs/attempt-001';NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n')
def serialize(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@contextlib.contextmanager
def aliases(v):
 old={k:sys.modules.get(k) for k in v};sys.modules.update(v)
 try:yield
 finally:
  for k,x in old.items():sys.modules.pop(k,None) if x is None else sys.modules.__setitem__(k,x)
def load(n,p,pin,a=None):
 assert sha(p)==pin;sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sys.modules[n]=m
 with aliases(a or {}):sp.loader.exec_module(m)
 return m
v1=load('tag_match_v1_study',V1/'study.py','72ff37edf8789918306944caef04058d75fcaf804c11d4ba28e5b05dbe607d50')
for n in ('BASE','MODEL','service','lifecycle','tokenizer'):globals()[n]=getattr(v1,n)
prior=v1.prior
def verify():
 r=read(ROOT/'READY.json');assert digest({k:v for k,v in r.items() if k!='identity'})==r['identity']
 for p,h in {**r['source_sha256'],**r['input_sha256']}.items():assert sha(p)==h
 return r
