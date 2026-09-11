"""Focused CPU qualification and immutable additive V2 READY seal."""
import os,subprocess,time
import protocol_v2 as p,study as s

TESTS=('test_protocol_v2','test_inputs_v2','test_scoring_v2','test_collect_v2','test_owner_v2')
INPUTS=('DATA.json','PUBLIC.json','SELECTION_AUDIT.json','ALLOCATION_AMENDMENT_V2.json','PLAN_v2.json','REQUESTS_v2.json','ORDERED_REQUESTS_v2.json','PROMPT_IDS_v2.json','ALIEN_DICTIONARIES_v2.json','COLLISION_AUDIT_v2.json','CPU_NATIVE_v2.json','PLANNED_NULL_ENDPOINTS_v2.json')
def qualify():
    started=time.time();cmd=[str(s.NATIVE),'-m','unittest','-v',*TESTS];result=subprocess.run(cmd,cwd=s.ROOT,capture_output=True,text=True,timeout=240,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    value=dict(argv=cmd,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-started,source_sha256={str(x):s.sha(x) for x in s.ROOT.glob('*.py')},gpu_calls=0,service_calls=0)
    s.write(s.ROOT/'CPU_TESTS_v2.json',value);print(result.stderr)
    if result.returncode:raise SystemExit(result.returncode)
def seal():
    tests=s.read(s.ROOT/'CPU_TESTS_v2.json');assert tests['returncode']==0
    for path,pin in tests['source_sha256'].items():assert s.sha(path)==pin
    source={str(s.QUALIFIED/'READY.json'):s.sha(s.QUALIFIED/'READY.json')}
    for path in s.ROOT.iterdir():
        if path.is_file() and path.name not in set(INPUTS)|{'READY_v2.json'}:source[str(path)]=s.sha(path)
    inputs={str(s.ROOT/name):s.sha(s.ROOT/name) for name in INPUTS}
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',version=2,source_sha256=source,input_sha256=inputs,model=s.MODEL,adapter=None,planned_endpoints=48,contexts=8,paired_seeds=1,arms=list(p.ARMS),factorial='visible_relation3_by_wording2',new_context_boundary='named MNLI inventories only; not globally/pretraining unseen',decoder='exact_requested_tag_all_arms',work_seconds=1320,owned_seconds=1410,outer_seconds=1440,startup_seconds=180,cleanup_seconds=90,outer_margin_seconds=30,workers=4,request_seconds=90,seed_master=p.MASTER,argv=[str(s.NATIVE),str(s.ROOT/'owner_v2.py'),'run','--output',str(s.ATTEMPT)],draft40_not_launched=True,gpu_calls=0,service_calls=0,prepared_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify();print(s.sha(s.READY_PATH),ready['identity'],len(source),len(inputs))
if __name__=='__main__':
    import argparse;ap=argparse.ArgumentParser();ap.add_argument('command',choices=('qualify','seal'));globals()[ap.parse_args().command]()
