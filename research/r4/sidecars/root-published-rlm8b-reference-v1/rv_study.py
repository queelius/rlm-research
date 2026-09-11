"""Explicit paths and immutable bindings for the isolated historical reference."""
import contextlib,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent
OFFICIAL=Path('/project/alex_phd/research-cache/repos/rlm--beb0603f1efa4725a7bb4ae73a1a870e140fe7d5')
DEPS=Path('/project/alex_phd/envs/rlm-beb0603-reference/pure')
RUNTIME=SIDE/'runtime-an27-5780-v1';IMAGE='8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python');ATTEMPT=ROOT/'outputs/attempt-001'
QSR=SIDE/'root-query-sensitive-rl-v1/inputs'
PAPER=Path('/project/alex_phd/research-cache/papers/2512.24601v2/source.tar')
MODEL_ROOT=Path('/project/alex_phd/research-cache/models')
MODELS={'base':dict(path=str(MODEL_ROOT/'Qwen--Qwen3-8B--b968826d9c46dd6066d109eabc6255188de91218'),alias='qwen3-8b'),'rlm':dict(path=str(MODEL_ROOT/'mit-oasys--rlm-qwen3-8b-v0.1--171c96639865d559206cd7ef78c4d8188a91992a'),alias='qwen3-8b')}
TEMPLATE=Path(MODELS['rlm']['path'])/'chat_template.jinja'
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def load(name,path,pin=None):
    if pin is not None and sha(path)!=pin:raise ValueError('source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
@contextlib.contextmanager
def aliases(values):
    old={k:sys.modules.get(k) for k in values};paths=list(sys.path);sys.modules.update(values)
    try:yield
    finally:
        sys.path[:]=paths
        for k,v in old.items():sys.modules.pop(k,None) if v is None else sys.modules.__setitem__(k,v)
def tokenizer(policy='base'):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(MODELS[policy]['path'],local_files_only=True,trust_remote_code=False);tok.chat_template=TEMPLATE.read_text();return tok
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in ready['source_sha256'].items():
        if sha(path)!=pin:raise ValueError('READY pin changed: '+path)
    return ready
