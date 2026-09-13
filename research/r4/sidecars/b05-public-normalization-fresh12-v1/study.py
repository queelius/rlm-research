"""Fresh twelve stages; identical public normalizer and released-base native seam."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PRIOR=ROOT.parent/'b05-public-normalization-held9-v1'
spec=importlib.util.spec_from_file_location('fresh_normalization_prior',PRIOR/'study.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
for name in ('read','sha','digest','write_x','bytes_x','now','load','aliases','tokenizer','renderer','request_body','decode_response','base_owner','call_id','MUSIQUE','MODEL','MODEL_ALIAS','NATIVE','SOURCE','TRAIN','source'):
    globals()[name]=getattr(prior,name)
normalize=load('fresh_normalization_unchanged_transform',PRIOR/'normalize.py')
ATTEMPT=ROOT/'outputs/attempt-001';READY_RUN=ROOT/'CPU_READY.json';INPUTS=ROOT/'PUBLIC_INPUTS.json';HOST=ROOT/'HOST_GOLD.json'
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=700,600,800
MAX_PHYSICAL,CONCURRENCY=48,4
PRIOR_SHA='c604f3e4de142862bf8ab62d5be6a948a9ff168bccb6e02c94837452f412584a'
NORMALIZE_SHA='515fed6eece6948951a4f9c6f3b25fc5f6f9f3feb124b62d8c5348a0d1038bda'


def calls():return read(INPUTS)['calls']


def verify():
    ready=read(READY_RUN);assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for path,want in ready['closure_sha256'].items():assert sha(path)==want,path
    assert sha(PRIOR/'CPU_READY.json')==PRIOR_SHA and sha(PRIOR/'normalize.py')==NORMALIZE_SHA
    terminal=read(PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json')
    assert all(terminal[k] for k in ('complete','released','runtime_qualified'))
    assert terminal['result_sha256']==sha(PRIOR/'outputs/attempt-001/RESULT.json')
    assert len(calls())==48 and len(read(INPUTS)['tasks'])==12
    return ready
