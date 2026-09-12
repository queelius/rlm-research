"""Freeze exact prompt delta and all32 paired coordinates, one native CPU fixture, seal."""
import os
from pathlib import Path
import subprocess
import time
import checkpoint
import study as s

CONTROL_SHA='c3a657addcf87f64b970fbe83de00d4e2fb1f83321139af2ed5d395e004f8061'
AUDIT=s.ROOT.parents[1]/'analyses/openai-mrcr-sft32-fresh8-g4-mechanism-2026-09-12/REPORT.json'
AUDIT_SHA='e8b0ae49b29415130e990d62cface02ab9d330b0b983d5b9db504c683d913f19'


def inputs():
    assert not (s.INPUTS/'train/tasks.json').exists()
    assert s.sha(s.CONTROL/'READY.json')==CONTROL_SHA and s.sha(AUDIT)==AUDIT_SHA
    audit=s.read(AUDIT);assert audit['available']==32 and audit['owner']['complete'] and audit['owner']['released']
    for p,w in audit['source_sha256'].items():assert s.sha(Path(p))==w,p
    old_plan=s.read(s.CONTROL/'inputs/train/PUBLIC.json')['plan'];plan=s.schedule('train');tasks=s.read(s.CONTROL/'inputs/train/tasks.json')
    assert len(plan)==len(old_plan)==len(tasks)==32 and len(s.records('train'))==8
    old_prefix=s.read(s.CONTROL/'inputs/train/PREFIXES.json');new_tasks=[];prefixes={};pairs=[]
    teacher=s.load('literal_inspection_renderer_system',s.TEACHER_SOURCE)
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    system,tools=teacher._system_and_ordered_tools();renderer=create_renderer(load_tokenizer(str(s.BASE)),Qwen3RendererConfig(enable_thinking=True))
    for before,row,task in zip(old_plan,plan,tasks,strict=True):
        assert {k:v for k,v in row.items() if k not in ('study','id')}=={k:v for k,v in before.items() if k not in ('study','id')}
        assert task['name']==before['id'];new={**task,'name':row['id'],'prompt':task['prompt']+'\n\n'+s.INSPECT_RULE};new_tasks.append(new)
        def render(prompt):return renderer.render([system,{'role':'user','content':prompt}],tools=tools,add_generation_prompt=True).token_ids
        prior=render(task['prompt']);assert prior==old_prefix[before['id']]['token_ids']
        ids=render(new['prompt']);assert ids!=prior
        prefixes[row['id']]={'token_ids':ids,'token_ids_sha256':s.digest(ids),'task_prompt_sha256':s.hashlib.sha256(new['prompt'].encode()).hexdigest()}
        pairs.append({'record_id':row['record_id'],'repeat':row['repeat'],'seed':row['seed'],'control_id':before['id'],'new_id':row['id'],
                      'control_prefix_sha256':s.digest(prior),'new_prefix_sha256':s.digest(ids),'only_root_instruction_changed':True})
    public=s.read(s.CONTROL/'inputs/train/PUBLIC.json');public.update(plan=plan,selection='all8 exact prior fresh contexts; no outcome selection')
    for name,value in [('tasks.json',new_tasks),('PREFIXES.json',prefixes),('PUBLIC.json',public),('HOST_GOLD.json',s.read(s.CONTROL/'inputs/train/HOST_GOLD.json'))]:
        s.write_x(s.INPUTS/'train'/name,value)
    (s.INPUTS/'train/HOST_GOLD.json').chmod(0o600)
    s.write_x(s.INPUTS/'CONTROL_PAIRING.json',{'pairs':pairs,'old_raw_exact':7,'old_available':32,'control_audit_sha256':AUDIT_SHA,
              'control_READY_sha256':CONTROL_SHA,'source_hashes_verified':audit['source_sha256'],'same_requested_seed_integers':True})
    assert checkpoint.binding('checkpoint32')==s.read(s.CONTROL/'outputs/attempt-001/owned-service/BINDING.json')
    return pairs


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not s.READY.exists() and not (s.ROOT/'outputs/attempt-001').exists()
    pairs=inputs();control=s.read(s.CONTROL/'READY.json')
    for p,w in control['closure_sha256'].items():assert s.sha(Path(p))==w,p
    command=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_prefix.py','--basetemp='+str(s.ROOT/'cpu-fixture-001')]
    test=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True,timeout=240)
    s.write_x(s.ROOT/'CPU_TESTS.json',{'command':command,'returncode':test.returncode,'stdout':test.stdout,'stderr':test.stderr,
              'scope':'Single actual env→role hooks→native HTTP double→parser→ACP fixture; all32 task deltas; no GPU/model or generated tool code.'})
    assert test.returncode==0,test.stdout+test.stderr
    paths=[*s.ROOT.glob('*.py'),s.ROOT/'RUNBOOK.md',s.ROOT/'CPU_TESTS.json',s.CONTROL/'READY.json',AUDIT,checkpoint.RECEIPT,
           *s.INPUTS.rglob('*.json'),*(s.ROOT/'cpu-fixture-001').rglob('*.json')]
    closure={**control['closure_sha256'],**s.read(AUDIT)['source_sha256'],**{str(p):s.sha(p) for p in paths}}
    ready={**{k:v for k,v in control.items() if k not in ('identity','closure_sha256')},'schema':'mrcr-fresh8-literal-inspection-ready-v1',
           'created_epoch':time.time(),'question':'Does one generic instruction induce actual literal-request inspection and prevent guessed exact-match strings?',
           'output':str(s.ROOT/'outputs/attempt-001'),'inputs':{**control['inputs'],'selection':'same all8 fresh controls, all32 paired trajectories',
              'schedule_sha256':s.digest(s.schedule('train')),'train':{'schedule_sha256':s.digest(s.schedule('train'))}},
           'instruction':s.INSPECT_RULE,'instruction_placement':'append exactly twoLF plus rule to existing root user task prompt; no other task fields except coordinate name changed',
           'control':{'ready_sha256':CONTROL_SHA,'audit_sha256':AUDIT_SHA,'pairing_sha256':s.sha(s.INPUTS/'CONTROL_PAIRING.json'),'cached_episodes':32},
           'metrics':{'primary':'raw exact; all8 G4 vectors; unavailable separate','diagnostics':['actual tool-observed user request strings before selection','literal request match versus guessed constants','clean target stdout','exact terminal copy','root/child calls and tokens'],
              'inspection_not_inferred_from_success':True,'mechanism_audit':'Inert inspection of all saved programs and tool observations after terminal; substring presence alone is not proof of use.'},
           'mechanism_limits':'No fixed request catalog, index, gold, examples or email-specific hints. Do not infer an abstract recursion algorithm. One prompt condition, no sweep if ineffective.',
           'claim_boundary':'Adaptively proposed inspection instruction on exposed8, different prompt tokens and potentially extra tool cost; same cp32/source/seeds, not equal actual call/token cost.',
           'fixed_argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--outer-seconds','1100'],
           'external_seconds':1200,'question_workers':4,'launch_authority':'MAIN only','closure_sha256':closure}
    ready['identity']=s.digest(ready);s.write_x(s.READY,ready)
    print({'READY_sha256':s.sha(s.READY),'identity':ready['identity'],'closure_files':len(closure),'pairs':len(pairs),'tests':test.stdout})


if __name__=='__main__':main()
