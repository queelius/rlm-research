"""Released-base new12 list/vector comparison, reusing the qualified fresh48 seam."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PRIOR=ROOT.parent/'b05-public-normalization-fresh12-v1'
spec=importlib.util.spec_from_file_location('vector_prior_native_study',PRIOR/'study.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
for name in ('read','sha','digest','write_x','bytes_x','now','load','aliases','tokenizer','renderer','request_body','decode_response','base_owner','call_id','MUSIQUE','MODEL','MODEL_ALIAS','NATIVE','SOURCE','TRAIN','source','normalize'):
    globals()[name]=getattr(prior,name)
ATTEMPT=ROOT/'outputs/attempt-001';READY_RUN=ROOT/'CPU_READY.json';INPUTS=ROOT/'PUBLIC_INPUTS.json';HOST=ROOT/'HOST_GOLD.json'
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=700,600,800
MAX_PHYSICAL,CONCURRENCY=48,4
PRIOR_SHA='109f3f0e1ea54bc53dbb0dd52a9544cd97e8292d15c0851f04e5e6c43992f5c0'


def calls():return read(INPUTS)['calls']


def verify():
    ready=read(READY_RUN);assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for path,want in ready['closure_sha256'].items():assert sha(path)==want,path
    assert sha(PRIOR/'CPU_READY.json')==PRIOR_SHA
    terminal=read(PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json')
    assert all(terminal[k] for k in ('complete','released','runtime_qualified'))
    assert terminal['result_sha256']==sha(PRIOR/'outputs/attempt-001/RESULT.json')
    assert len(calls())==48 and len(read(INPUTS)['tasks'])==12
    return ready
