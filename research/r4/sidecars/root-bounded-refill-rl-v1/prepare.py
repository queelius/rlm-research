"""CPU-only immutable candidates, existing native-prefix proof, tests and final seal."""
import argparse
import os
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
import study as s

APPROVAL=s.STORE/'ideas/2026-09-09-bounded-refill-rl-main-approval.md'

def seed_audit(plans):
    rows=[r for groups in plans['windows'].values() for g in groups for r in g]+plans['readout']
    seeds={r['seed'] for r in rows}|{s.MASTER,s.SEED}
    if len(seeds)!=154:raise ValueError('local seed collision')
    prior=s.read(s.OLD/'inputs/SEED_AUDIT.json')
    paths={v['path']:v['sha256'] for v in prior['sources']}
    # A bounded metadata-only screen, including recent accepted namespaces.
    for directory in ('root-adaptive-rlvr-v1','root-row-mean-sft-v1','root-success-trajectory-sft-v1',
                      'root-success-sft-lr-v1','root-coverage-first-v1','root-accumulation-ledger-v1'):
        root=s.SIDE/directory
        for name in ('SPEC.json','RECIPE.json','SEED_AUDIT.json','inputs/PLANS.json','inputs/SEED_AUDIT.json','EVAL_PLAN.json'):
            path=root/name
            if path.exists():paths[str(path)]=s.sha(path)
    expression=re.compile(r'\b(?:'+'|'.join(map(str,sorted(seeds)))+r')\b');evidence=[]
    for path,want in sorted(paths.items()):
        s.check(path,want);found=sorted(set(expression.findall(Path(path).read_text())))
        if found:raise ValueError('fresh namespace collision: '+path)
        evidence.append({'path':path,'sha256':want,'matches':[]})
    return {'seed_master':s.MASTER,'optimizer_seed':s.SEED,'all_unique_seeds':sorted(seeds),
            'scope':'named inherited metadata plus six recent accepted sidecars; no output reads or global collision claim',
            'sources':evidence,'paired_readout_seeds_reused_only_before_after':True}

def inputs():
    public,host=s.data();plans=s.build_plans(public)
    tasks_path=s.OLD/'inputs/TASKS.json';s.check(tasks_path,s.OLD_MANIFEST['input_sha256'][str(tasks_path)])
    tasks=s.read(tasks_path);allrows=[r for groups in plans['windows'].values() for g in groups for r in g]+plans['readout']
    if set(tasks)!={r['task_name'] for r in allrows}:raise ValueError('frozen task inventory differs')
    if any(len(t['first_prompt_token_ids'])+2048>8192 for t in tasks.values()):raise ValueError('no prompt cropping permitted')
    contexts={r['id']:r for r in public};audit=[]
    for groups in plans['windows'].values():
        for group in groups:
            row=group[0];context=contexts[row['context_id']]
            audit.append({'window':row['candidate_window'],'group':row['candidate_group'],'task':row['task_name'],
                'context':row['context_id'],'records':len(context['records']),'family':row['family'],
                'target':context['target'],'answer':host[row['context_id']]['answers'][row['family']]})
    bundle={'PLANS.json':plans,'TASKS.json':tasks,'SEED_AUDIT.json':seed_audit(plans),
            'DATA_AUDIT.json':{'source':str(s.OLD/'inputs/DATA_AUDIT.json'),'source_sha256':s.sha(s.OLD/'inputs/DATA_AUDIT.json'),
                'tasks_source':str(tasks_path),'tasks_source_sha256':s.sha(tasks_path),
                'inherited_task_count':len(tasks),'max_initial_prompt_tokens':max(len(t['first_prompt_token_ids']) for t in tasks.values()),
                'public_sha256':s.sha(s.PRIOR/'prepared-v2/PUBLIC.json'),'host_sha256':s.sha(s.PRIOR/'prepared-v2/HOST_GOLD.json'),
                'training_groups':16,'candidate_training_attempts':128,'paired_readout_coordinates':24,
                'exposure':'same source-disjoint root development composition,896 leaf-training-supported public groups; no new task novelty'},
            'GOLD_SKEW.json':{'groups':audit,'answer_histogram':dict(Counter(v['answer'] for v in audit)),
                'label_based_selection':False,'zero_answers_retained':True}}
    for name,value in bundle.items():s.write(s.ROOT/'inputs'/name,value)
    recipe=s.read(s.OLD/'RECIPE.json')
    recipe.update(schema=s.ROOT.name,training_seed=s.SEED,root_adapter=s.fixed_start()['path'],root_adapter_sha256=s.FINAL_SHA,
        training_wall_cap_seconds=240,optimizer_steps=4,
        selection='last actual committed RL step0..4, no validation choice; candidate cursor separate',
        caps={'global':3480,'inclusive':3600,'outer':3630,'candidate_group':300,'baseline':660,'final':660,
              'readout':480,'service_ready':180,'training_forward_backward':240,'training_save_release':60,'training_cutoff':2820},
        start='Fixed low-LR success-SFT8, fresh RL Adam0 and seed; old SFT Adam never loaded',
        refill='Mandatory groups1,2; then3,4 only while fewer than2 mixed groups; all admitted mixed episodes, true no-op if none')
    s.write(s.ROOT/'RECIPE.json',recipe)
    s.write(s.ROOT/'START.json',{'kind':'fixed_success_sft8','policy':s.fixed_start(),
        'approval_path':str(APPROVAL),'approval_sha256':s.sha(APPROVAL),
        'selection':'MAIN availability-fixed low-LR8; not high-LR readout-selected',
        'sft_result_path':str(s.FINAL/'RESULT.json'),'sft_result_sha256':s.sha(s.FINAL/'RESULT.json'),
        'fresh_rl_adam':True,'fresh_rl_generation':0})
    print({'tasks':len(tasks),'training':128,'readout':48,'gpu_calls':0})

def qualification():
    records=[]
    for name,python,files in [('native',s.NATIVE,['test_windows.py','test_contract.py','test_coordinator.py']),
                              ('tiny-training',s.TRAIN,['test_training.py'])]:
        argv=[str(python),'-m','pytest','-q',*files]
        result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=120,
            env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        records.append({'name':name,'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode:
            print(result.stdout,result.stderr);raise ValueError('focused CPU qualification failed')
    s.write(s.ROOT/'CPU_TESTS.json',{'status':'PASS','results':records,'gpu_calls':0,
        'red_evidence':'New window tests failed before windows.py; actual8/24 dispatch and consumed-prefix tests failed before collect/export implementation.',
        'synthetic_only':'All tiny likelihoods are CPU fixtures, excluded from scientific exports.'})
    print({'status':'PASS','gpu_calls':0})

def seal():
    s.read(s.ROOT/'CPU_TESTS.json')
    sources={**s.OLD_MANIFEST['source_sha256'],**s.OLD_MANIFEST['input_sha256'],str(s.OLD/'CAMPAIGN.json'):s.OLD_CAMPAIGN_SHA}
    sources.update({str(p):s.sha(p) for p in list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+
        [s.ROOT/'RECIPE.json',s.ROOT/'START.json',s.ROOT/'CPU_TESTS.json',APPROVAL,s.CAMPAIGN/'test_training.py']})
    sources.update({str(p):s.sha(p) for p in [s.FINAL/'RESULT.json',s.FINAL/'SELECTION.json',s.FINAL/'checkpoint-0008/state.json']})
    sources.update({str(s.FINAL/'checkpoint-0008'/name):want for name,want in s.read(s.FINAL/'checkpoint-0008/state.json')['files_sha256'].items()})
    input_hashes={str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')}
    for path,want in {**sources,**input_hashes}.items():s.check(path,want)
    campaign={'schema':s.ROOT.name,'seed_master':s.MASTER,'optimizer_seed':s.SEED,
        'source_sha256':sources,'input_sha256':input_hashes,'maximum_training_attempts':128,
        'planned_readout_episodes':48,'candidate_windows':4,'maximum_actual_updates':4,
        'start_adapter_sha256':s.FINAL_SHA,'fixed_child_sha256':s.CHILD_SHA,'gpu_calls_in_preparation':0}
    campaign['campaign_id']=s.digest(campaign);s.write(s.ROOT/'CAMPAIGN.json',campaign)
    ready={'status':'CPU_READY_WAITING_MAIN_ACCEPTANCE','campaign_id':campaign['campaign_id'],
        'campaign_sha256':s.sha(s.ROOT/'CAMPAIGN.json'),'source_paths':len(sources),'input_paths':len(input_hashes),
        'source_sha256':sources,'input_sha256':input_hashes,'cpu_tests_sha256':s.sha(s.ROOT/'CPU_TESTS.json'),
        'driver':str(s.ROOT/'coordinator.py'),'driver_sha256':s.sha(s.ROOT/'coordinator.py'),
        'output':str(s.ROOT/'outputs/attempt-001'),
        'verify_argv':[str(s.NATIVE),str(s.ROOT/'coordinator.py'),'verify'],
        'launch_argv':[str(s.NATIVE),str(s.ROOT/'coordinator.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
        'caps':{'work':3480,'inclusive':3600,'outer':3630},'launch_authorized':False,'gpu_calls_in_preparation':0,'prepared_epoch':time.time()}
    s.write(s.ROOT/'READY.json',ready)
    s.verify_prepared()
    print({'ready_sha256':s.sha(s.ROOT/'READY.json'),'campaign_sha256':ready['campaign_sha256'],'status':ready['status']})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('inputs','qualify','seal'));a=p.parse_args()
    {'inputs':inputs,'qualify':qualification,'seal':seal}[a.command]()
