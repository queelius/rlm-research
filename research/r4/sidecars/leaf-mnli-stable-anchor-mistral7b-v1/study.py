"""Cross-family stable-anchor bindings for released Mistral-7B-Instruct-v0.3."""
import contextlib,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;PRIOR=SIDE/'leaf-mnli-stable-anchor-vs-sequence-counting-v1';FREE=SIDE/'leaf-free-id-correspondence-v1';MODEL_PATH=Path('/project/alex_phd/research-cache/models/mistralai--Mistral-7B-Instruct-v0.3--c170c708c41dac9275d15a8fff4eca08d52bab71');ATTEMPT=ROOT/'outputs/attempt-001';NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
MODEL={'alias':'mistral-7b-instruct-v0.3-stable-anchor','path':str(MODEL_PATH),'revision':'c170c708c41dac9275d15a8fff4eca08d52bab71','manifest_sha256':'41257c6fa03926b08fe846efff48f846a7b8d14eba533db0db74d8be4aa1d7b0'};MODELS={'mistral':MODEL};MAX_MODEL_LEN=8448
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
write_once=write
def serialize(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@contextlib.contextmanager
def aliases(values):
 old={k:sys.modules.get(k) for k in values};sys.modules.update(values)
 try:yield
 finally:
  for k,v in old.items():sys.modules.pop(k,None) if v is None else sys.modules.__setitem__(k,v)
def load(name,path,pin=None,aliases_map=None):
 if pin and sha(path)!=pin:raise ValueError('source changed: '+str(path))
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module
 with aliases(aliases_map or {}):spec.loader.exec_module(module)
 return module
prior=load('mistral_stable_prior',PRIOR/'study.py','a11a23ba286745a32a16b9c47e9cbceaa995fffa9bf3a1cbbecf9fa399b13243');base,lifecycle=prior.base,prior.lifecycle
service=load('mistral_stable_service_contract',FREE/'service.py','51215324f767d3b7fc214bed4c64e61592fb3be8223c8d5f1dd4773fae4c48cd',{'study':sys.modules[__name__]});_service_config,_service_descriptor,_service_validate=service.config,service.descriptor,service.validate_descriptor
def _mistral_config(model,directory,key):
 value=_service_config(model,directory,key);value['vllm']['max_model_len']=MAX_MODEL_LEN;return value
def _mistral_descriptor(model,directory):
 value=_service_descriptor(model,directory);value['max_model_len']=MAX_MODEL_LEN;return value
def _mistral_validate(endpoint,model):
 value=dict(endpoint);value['max_model_len']=8192;_service_validate(value,model)
 if endpoint.get('max_model_len')!=MAX_MODEL_LEN:raise ValueError('Mistral context bound differs')
service.config=_mistral_config;service.descriptor=_mistral_descriptor;service.validate_descriptor=_mistral_validate
def tokenizer():
 from transformers import AutoTokenizer
 return AutoTokenizer.from_pretrained(MODEL_PATH,local_files_only=True,trust_remote_code=False)
def verify():
 prior.verify();ready=read(ROOT/'READY.json')
 if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
 for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():
  if sha(path)!=pin:raise ValueError('closure changed: '+path)
 manifest=read(MODEL_PATH/'ACQUISITION_MANIFEST.json')
 if manifest['revision']!=MODEL['revision'] or sha(MODEL_PATH/'ACQUISITION_MANIFEST.json')!=MODEL['manifest_sha256']:raise ValueError('Mistral acquisition manifest changed')
 return ready
