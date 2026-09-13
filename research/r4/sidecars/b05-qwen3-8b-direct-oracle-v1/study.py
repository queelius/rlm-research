"""Frozen eight-call B05 alternative-model calibration; no calls on import."""
import functools,hashlib,importlib.util,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
SOURCE=SIDE/'b05-recombination-feasibility-v1';READY=ROOT/'READY.json';ATTEMPT=ROOT/'outputs/attempt-001'
MODEL=Path('/project/alex_phd/research-cache/models/Qwen--Qwen3-8B--b968826d9c46dd6066d109eabc6255188de91218')
MANIFEST=MODEL/'local-research-manifest.json';MODEL_ALIAS='Qwen3-8B-b968826-nonthinking-b05'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python');OWNER_SECONDS=450;SCIENCE_SECONDS=300;EXTERNAL_SECONDS=550
MUSIQUE=SIDE/'musique-task-directed-followup-v1';SERVICE=ROOT/'service.py';CONCURRENCY=4;MAX_PHYSICAL=8
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_x(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False);f.write('\n')
def bytes_x(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(v)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);old=list(sys.path)
    try:sys.path.insert(0,str(Path(p).parent));spec.loader.exec_module(m);return m
    finally:sys.path[:]=old
@functools.lru_cache(None)
def source():return load('b05_qwen8_source_study',SOURCE/'runner_study_v3.py')
@functools.lru_cache(None)
def contract():return load('b05_qwen8_contract',SOURCE/'contract_v3.py')
@functools.lru_cache(None)
def tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(str(MODEL),local_files_only=True)
def roots():return source().active_roots()
def host_by_root():return source().host_by_root()
def calls():return [x for x in source().calls() if x['kind'] in ('direct','oracle_exact_report_synthesis')]
def call_id(call):return source().call_id(call)
def binding():
    manifest=read(MANIFEST)
    if manifest['model_id']!='Qwen/Qwen3-8B' or manifest['huggingface_revision']!='b968826d9c46dd6066d109eabc6255188de91218':raise ValueError('cached post-trained model identity changed')
    return {'schema':'released-base-single-model-binding-v1','model':'qwen3','checkpoint':{'alias':MODEL_ALIAS,'path':str(MODEL),'revision':manifest['huggingface_revision'],'manifest_sha256':sha(MANIFEST)},'adapter':None,'weights_sha256':digest(manifest['files'])}
def request_body(prompt,seed,max_tokens):
    ids=tokenizer().apply_chat_template([{'role':'user','content':prompt}],tokenize=True,add_generation_prompt=True,enable_thinking=False)
    if hasattr(ids,'keys'):ids=ids['input_ids']
    if not ids or len(ids)+max_tokens>8192:raise ValueError('prefix plus output exceeds8192')
    return {'model':MODEL_ALIAS,'token_ids':ids,'sampling_params':{'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'max_tokens':max_tokens,'seed':seed,'logprobs':1},'cache_salt':'0'}
def decode_response(body,response):
    value={'transport_valid':False,'text':None,'finish_reason':None,'usage':response.get('usage',{}) if isinstance(response,dict) else {},'response_sha256':digest(response),'failure':None}
    try:
        assert response['model']==MODEL_ALIAS and isinstance(response['request_id'],str) and response['request_id'] and len(response['choices'])==1
        c=response['choices'][0];ids=c['token_ids'];content=c['logprobs']['content'];finish=c['finish_reason'];assert ids and len(ids)==len(content)<=body['sampling_params']['max_tokens']
        assert all(type(x) is int and 0<=x<len(tokenizer()) for x in ids);assert finish in ('stop','length')
        assert all(x['token']==f'token_id:{t}' and math.isfinite(float(x['logprob'])) for t,x in zip(ids,content,strict=True))
        usage=response['usage'];assert usage['prompt_tokens']==len(body['token_ids']) and usage['completion_tokens']==len(ids)
        value.update(transport_valid=True,text=tokenizer().decode(ids,skip_special_tokens=True),finish_reason=finish,completion_ids=ids,completion_logprobs=[float(x['logprob']) for x in content],request_id=response['request_id'],model=response['model'])
    except (AssertionError,KeyError,TypeError,ValueError) as e:value['failure']=type(e).__name__+': native token/model/finish/usage contract'
    return value
def score_root(text,root,reports=None):return source().score_root(text,root,reports)
def verify():
    r=read(READY);assert r['identity']==digest({k:v for k,v in r.items() if k!='identity'})
    for p,h in r['closure_sha256'].items():assert sha(p)==h,p
    assert len(roots())==4 and len(calls())==8;binding();return r
