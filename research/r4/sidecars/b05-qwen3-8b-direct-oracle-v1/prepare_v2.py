"""Additive seal after correcting a test misunderstanding of Qwen3 nonthinking prefix."""
import json,subprocess,time
from pathlib import Path
import study
def main():
    if study.READY.exists():raise FileExistsError(study.READY)
    source=study.source();source_ready=source.verify();manifest=study.read(study.MANIFEST)
    for rel,h in manifest['files'].items():
        if study.sha(study.MODEL/rel)!=h:raise ValueError('cached model changed: '+rel)
    assert len(study.read(study.ROOT/'INPUTS.json')['rows'])==8
    cmd=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider',str(study.ROOT/'test_pilot_v2.py')];start=time.time();p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    cpu=study.ROOT/'CPU_TESTS_V2.json';study.write_x(cpu,{'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'elapsed_seconds':time.time()-start,'GPU_calls':0,'v1_failure_test_only':'nonthinking Qwen3 template deliberately includes an empty think block'});assert p.returncode==0,p.stdout+p.stderr
    closure=dict(source_ready['closure_sha256']);closure[str(source.READY_RUN)]=study.sha(source.READY_RUN)
    for rel,h in manifest['files'].items():closure[str(study.MODEL/rel)]=h
    local=[study.ROOT/x for x in ('DESIGN.md','RUNBOOK.md','study.py','collect.py','service.py','owner.py','test_pilot.py','test_pilot_v2.py','prepare.py','prepare_v2.py','INPUTS.json','CPU_TESTS.json','CPU_TESTS_V2.json')]
    local += [study.MANIFEST,study.ROOT.parents[1]/'analyses/root-published-rlm8b-port-assessment-2026-09-12/MODEL_CHARACTERIZATION_CORRECTION.md']
    for pth in local:closure[str(pth)]=study.sha(pth)
    value={'schema':'b05-qwen3-8b-direct-oracle-ready-v2','created_epoch':time.time(),'question':'Does cached post-trained Qwen3-8B improve validity/source correctness on frozen B05 direct/oracle roots?',
      'claim_boundary':'model-alternative calibration; not pure size/posttraining/architecture effect','model':study.binding(),'renderer':{'checkpoint_own_chat_template':True,'enable_thinking':False,'expected_empty_think_prefix':True},
      'source_ready_sha256':study.sha(source.READY_RUN),'source_ready_identity':source_ready['identity'],'planned':{'direct':4,'oracle_exact_report_synthesis':4,'child':0,'recombined':0,'total':8},
      'sampling':{'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'max_tokens':1024,'context':8192},'seeds':[x['seed'] for x in study.calls()],
      'metrics':{'primary':'true-source correctness','secondary':'report consistency/validity','all_calls_retained':True},'caps_seconds':{'science':300,'owner':450,'external':550},
      'fresh_4B_calls':0,'optimizer_steps':0,'model_calls_during_preparation':0,'GPU_calls_during_preparation':0,'attempt':str(study.ATTEMPT),
      'argv':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--outer-seconds','450'],'closure_sha256':dict(sorted(closure.items()))}
    value['identity']=study.digest(value);study.write_x(study.READY,value);print(json.dumps({'sha256':study.sha(study.READY),'identity':value['identity']},sort_keys=True))
if __name__=='__main__':main()
