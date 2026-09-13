"""Varied vector G4 collection only; held input frozen, no optimizer or adapter."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PRIOR=ROOT.parent/'b05-decision-vector-v1'
spec=importlib.util.spec_from_file_location('varied_vector_native_source',PRIOR/'study.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
for name in ('read','sha','digest','write_x','bytes_x','now','load','aliases','tokenizer','renderer','request_body','decode_response','base_owner','call_id','MUSIQUE','MODEL','MODEL_ALIAS','NATIVE','SOURCE','TRAIN','source','normalize'):
    globals()[name]=getattr(prior,name)
interface=load('varied_vector_unchanged_interface',PRIOR/'interface.py')
ATTEMPT=ROOT/'outputs/attempt-001';READY_RUN=ROOT/'CPU_READY.json';INPUTS=ROOT/'TRAIN_PUBLIC.json';HELD=ROOT/'HELD_PUBLIC.json';HOST=ROOT/'HOST_GOLD.json'
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=700,600,800
MAX_PHYSICAL,CONCURRENCY=64,4
PRIOR_SHA='992d7159904040919776081d768adb6fe89f3f556cb2c05e4bef3402fa19999c'


def calls():return read(INPUTS)['calls']


def verify():
    ready=read(READY_RUN);assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for path,want in ready['closure_sha256'].items():assert sha(path)==want,path
    assert sha(PRIOR/'CPU_READY.json')==PRIOR_SHA
    terminal=read(PRIOR/'outputs/attempt-001/OWNER_TERMINAL.json')
    assert all(terminal[k] for k in ('complete','released','runtime_qualified')) and terminal['result_sha256']==sha(PRIOR/'outputs/attempt-001/RESULT.json')
    assert len(calls())==64 and len(read(INPUTS)['tasks'])==16 and len(read(HELD)['tasks'])==12
    return ready
