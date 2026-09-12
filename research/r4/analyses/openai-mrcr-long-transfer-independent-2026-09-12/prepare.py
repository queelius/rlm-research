"""Seal the one-shot CPU analyzer."""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;READY=ROOT/'CPU_READY.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build():
    files=[ROOT/n for n in ('analyze.py','test_analyze.py','run_if_terminal.py','CPU_TESTS.json','prepare.py')]
    v={'schema':'openai-mrcr-long-transfer-independent-analysis-ready-v1','created_epoch':time.time(),'source_ready':'/project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-long-transfer-eval-v1/READY_V2.json','source_ready_sha256':'d896540268ec2ced54414415de07db2e30c0d7c756a741487cd2165194efbd62','attempts':{'base':'outputs/base-002','checkpoint32':'outputs/checkpoint32-002'},'one_shot_after_both_owner_terminals':True,'polling':False,'gpu_calls':0,'closure_sha256':{str(p):sha(p) for p in files}};v['identity']=digest(v);READY.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');return v
def verify():
    v=json.loads(READY.read_text());assert v['identity']==digest({k:x for k,x in v.items() if k!='identity'})
    for p,h in v['closure_sha256'].items():assert sha(p)==h,p
    return v
if __name__=='__main__':
    v=verify() if READY.exists() else build();print(json.dumps({'identity':v['identity'],'sha256':sha(READY)},sort_keys=True))
