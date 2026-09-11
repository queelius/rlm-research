import contextlib,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; SIDE=ROOT.parent; PRIOR=SIDE/'leaf-mnli-stable-anchor-vs-sequence-counting-v1'; ATTEMPT=ROOT/'outputs/attempt-001'; NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n')
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
prior=load('balanced_tag_prior',PRIOR/'study.py','a11a23ba286745a32a16b9c47e9cbceaa995fffa9bf3a1cbbecf9fa399b13243')
for n in ('BASE','MODEL','service','lifecycle','tokenizer','serialize'):globals()[n]=getattr(prior,n)
def verify():
 r=read(ROOT/'READY.json');assert digest({k:v for k,v in r.items() if k!='identity'})==r['identity']
 for p,h in {**r['source_sha256'],**r['input_sha256']}.items():assert sha(p)==h
 return r
