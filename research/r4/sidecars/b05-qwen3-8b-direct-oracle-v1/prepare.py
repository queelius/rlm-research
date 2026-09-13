"""CPU-only seal; verifies cached model and frozen B05 source, never launches."""
import json,subprocess,time
from pathlib import Path
import study
def main():
    if study.READY.exists():raise FileExistsError(study.READY)
    source=study.source();source_ready=source.verify();manifest=study.read(study.MANIFEST)
    for rel,h in manifest['files'].items():
        if study.sha(study.MODEL/rel)!=h:raise ValueError('cached Qwen3-8B file changed: '+rel)
    rows=[]
    roots={r['root_id']:r for r in study.roots()}
    for call in study.calls():
        root=roots[call['root_id']]
        if call['kind']=='direct':prompt=root['direct_prompt']
        else:prompt=study.host_by_root()[call['root_id']]['oracle_synthesis_prompt']
        prompt=study.contract().clarify(call,prompt);body=study.request_body(prompt,call['seed'],call['max_tokens'])
        rows.append({'call':call,'call_id':study.call_id(call),'prompt_sha256':study.digest(prompt),'prefix_token_ids_sha256':study.digest(body['token_ids']),'prefix_tokens':len(body['token_ids']),'nonthinking':True})
    study.write_x(study.ROOT/'INPUTS.json',{'schema':'b05-qwen3-8b-direct-oracle-inputs-v1','rows':rows})
    cmd=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider',str(study.ROOT/'test_pilot.py')];start=time.time();p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    study.write_x(study.ROOT/'CPU_TESTS.json',{'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'elapsed_seconds':time.time()-start,'GPU_calls':0});assert p.returncode==0,p.stdout+p.stderr
    closure=dict(source_ready['closure_sha256']);closure[str(source.READY_RUN)]=study.sha(source.READY_RUN)
    for rel,h in manifest['files'].items():closure[str(study.MODEL/rel)]=h
    local=[study.ROOT/x for x in ('DESIGN.md','RUNBOOK.md','study.py','collect.py','service.py','owner.py','test_pilot.py','prepare.py','INPUTS.json','CPU_TESTS.json')]
    local += [study.MANIFEST,study.ROOT.parents[1]/'analyses/root-published-rlm8b-port-assessment-2026-09-12/MODEL_CHARACTERIZATION_CORRECTION.md']
    for pth in local:closure[str(pth)]=study.sha(pth)
    value={'schema':'b05-qwen3-8b-direct-oracle-ready-v1','created_epoch':time.time(),'question':'Does cached post-trained Qwen3-8B improve validity/source correctness on frozen B05 direct/oracle roots?',
      'claim_boundary':'model-alternative calibration; not pure size/posttraining/architecture effect','model':study.binding(),'renderer':{'checkpoint_own_chat_template':True,'enable_thinking':False},
      'source_ready_sha256':study.sha(source.READY_RUN),'source_ready_identity':source_ready['identity'],'planned':{'direct':4,'oracle_exact_report_synthesis':4,'child':0,'recombined':0,'total':8},
      'sampling':{'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'max_tokens':1024,'context':8192},'seeds':[x['seed'] for x in study.calls()],
      'metrics':{'primary':'true-source correctness','secondary':'report consistency/validity','all_calls_retained':True},'caps_seconds':{'science':300,'owner':450,'external':550},
      'fresh_4B_calls':0,'optimizer_steps':0,'model_calls_during_preparation':0,'GPU_calls_during_preparation':0,'attempt':str(study.ATTEMPT),
      'argv':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--outer-seconds','450'],'closure_sha256':dict(sorted(closure.items()))}
    value['identity']=study.digest(value);study.write_x(study.READY,value);print(json.dumps({'sha256':study.sha(study.READY),'identity':value['identity']},sort_keys=True))
if __name__=='__main__':main()
