"""Additive V2 input preparation, qualification, and seal."""
import os,subprocess,time
import protocol as p,study as s
base=s.load('tag_match_v2_prepare_base',s.V1/'prepare.py','8b76899f60a75fcbaaef075f43db0c26c3a4b4a81fb8fb2730f7a56060b1dca3',{'study':s,'protocol':p})
inputs=base.inputs
def qualify():
 cmd=[str(s.NATIVE),'-m','pytest','-q','test_runtime.py'];started=time.time();r=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=300,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'});s.write(s.ROOT/'CPU_TESTS.json',{'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.time()-started,'source_sha256':{str(x):s.sha(x) for x in s.ROOT.glob('*.py')},'gpu_calls':0,'service_calls':0});print(r.stdout,r.stderr)
 if r.returncode:raise SystemExit(r.returncode)
def seal():
 tests=s.read(s.ROOT/'CPU_TESTS.json');assert tests['returncode']==0
 for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
 names=('PLAN.json','REQUESTS.json','ORDERED_REQUESTS.json','PROMPT_IDS.json','CPU_NATIVE.json','PLANNED_NULL_ENDPOINTS.json','TAG_SETS.json','DATA.json','DATASET_MANIFEST.json','SOURCE_PINS.json');inputs_sha={str(s.ROOT/n):s.sha(s.ROOT/n) for n in names};sources={str(x):s.sha(x) for x in s.ROOT.iterdir() if x.is_file() and x.name not in ('READY.json','CPU_TESTS.json')};sources[str(s.V1/'READY.json')]=s.sha(s.V1/'READY.json');ready={'schema':'leaf-mnli-balanced-tag-match-ready-v2','status':'CPU_READY_FOR_MAIN_ACCEPTANCE','supersedes_unlaunched_ready_sha256':'d4419c04b00b0613bd8351368ac414349cf4b40a5c035bba411cb294b0c4fd51','correction':'restore requested_tag so wrong/alien/aligned reference conditions are active; fix named-reference diagnostic direction; counterbalance cell order','planned_endpoints':192,'contexts':16,'cells':list(p.CELLS),'relations':list(p.RELATIONS),'master':p.MASTER,'primary':'late mean(match AA,BB)-mean(nonmatch AB,BA), pooled over relations and contexts','outer_seconds':1800,'owned_seconds':1770,'work_seconds':1650,'workers':4,'request_seconds':90,'model':s.MODEL,'adapter':None,'source_sha256':sources,'input_sha256':inputs_sha,'test_receipt_sha256':s.sha(s.ROOT/'CPU_TESTS.json'),'argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],'gpu_calls':0,'service_calls':0};ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify();print(s.sha(s.ROOT/'READY.json'),ready['identity'])
if __name__=='__main__':
 import sys
 if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU only')
 globals()[sys.argv[1]]()
