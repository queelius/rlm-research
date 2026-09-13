"""Six fresh base-model stages; fixed 176-call singleton/list/vector comparison."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PRIOR=ROOT.parent/'b05-decision-vector-v1'
spec=importlib.util.spec_from_file_location('singleton_prior_vector_study',PRIOR/'study.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
for name in ('read','sha','digest','write_x','bytes_x','now','load','aliases','tokenizer','renderer','request_body','decode_response','base_owner','call_id','MUSIQUE','MODEL','MODEL_ALIAS','NATIVE','SOURCE','TRAIN','source','normalize'):
    globals()[name]=getattr(prior,name)
ATTEMPT=ROOT/'outputs/attempt-001';READY_RUN=ROOT/'CPU_READY.json';INPUTS=ROOT/'PUBLIC_INPUTS.json';HOST=ROOT/'HOST_GOLD.json'
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=1000,900,1100
MAX_PHYSICAL,CONCURRENCY=176,4
PRIOR_SHA='992d7159904040919776081d768adb6fe89f3f556cb2c05e4bef3402fa19999c'


def calls():return read(INPUTS)['calls']


def verify():
    ready=read(READY_RUN);assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for path,want in ready['closure_sha256'].items():assert sha(path)==want,path
    assert sha(PRIOR/'CPU_READY.json')==PRIOR_SHA
    terminal=read(PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json')
    assert all(terminal[k] for k in ('complete','released','runtime_qualified'))
    assert terminal['result_sha256']==sha(PRIOR/'outputs/attempt-001/RESULT.json')
    plan=read(INPUTS);assert len(plan['calls'])==176 and len(plan['tasks'])==6
    assert sum(c['arm']=='singleton' for c in plan['calls'])==152
    return ready
