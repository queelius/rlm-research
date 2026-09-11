"""Bounded CPU qualification/input closure; READY is the last write."""
import argparse
import json
import subprocess
import time
from pathlib import Path
import study as s
import adapter

def prepare(qualification):
    if (s.ROOT/'READY.json').exists():raise ValueError('already frozen')
    proof=s.read(qualification/'RESULT.json')
    if proof['status']!='PASS' or proof['provider_calls']!=5 or proof['gpu_calls']!=0:raise ValueError('native fixture missing')
    contexts,gold,tasks=s.inputs();plan=s.plan_for(contexts);bindings={w:s.binding(w) for w in s.WEIGHTS};st=s.stack()
    trace=s.read(qualification/'EPISODE.json')['traces'][0]
    template=s.read(s.OLD/'inputs/NATIVE_TEMPLATE.json');system=trace['nodes'][0]['message'];tools=st.native.wire_tools(trace['tools'])
    if system!=template['system'] or json.dumps(tools)!=template['tools_ordered_json']:raise ValueError('native system/tool serialization differs')
    renderer=st.native.renderer();fixture=renderer.render([system,{'role':'user','content':'Use records.json and batch_contract.py. Return only Answer: N.'}],tools=tools,add_generation_prompt=True).token_ids
    if fixture!=s.read(qualification/'PROVIDER_REQUESTS.json')[0]['body']['token_ids']:raise ValueError('actual fixture prefix not reproduced')
    old_plan={r['id']:r for r in s.read(s.OLD/'inputs/PLAN.json')}
    old_prompts={old_plan[r['id']]['context_id']:r for r in s.read(s.OLD/'inputs/PROMPTS.json')}
    public={c['id']:c for c in contexts};prompts=[];pairs=[]
    for row in plan:
        context=public[row['context_id']];task=adapter.task(context,tasks[row['task_name']]['prompt'],gold[context['id']],row['task_name'],row)
        ids=renderer.render([system,{'role':'user','content':task.data.prompt}],tools=tools,add_generation_prompt=True).token_ids
        old=old_prompts[context['id']]
        if task.hash!=old['task_hash'] or ids!=old['token_ids']:raise ValueError('old initial task/prompt bytes changed')
        if len(ids)+2048>8192:raise ValueError('initial prompt plus cap does not fit')
        prompts.append({'id':row['id'],'weight':row['weight'],'token_ids':ids,'task_hash':task.hash,
                        'prompt_sha256':s.digest(task.data.prompt),'old_prompt_exact':True})
    for match in dict.fromkeys(r['matched_coordinate'] for r in plan):
        ids=[r['id'] for r in plan if r['matched_coordinate']==match]
        current=[p for p in prompts if p['id'] in ids]
        if len(current)!=6 or len({s.digest(p['token_ids']) for p in current})!=1 or len({p['task_hash'] for p in current})!=1:raise ValueError('six-cell coordinate crosswalk differs')
        pairs.append({'matched_coordinate':match,'ids':ids,'all6_task_and_prompt_equal':True})
    scanned=[];collisions=[]
    for directory in s.SIDE.iterdir():
        if directory==s.ROOT:continue
        for name in ('SPEC.json','CAMPAIGN.json','RECIPE.json','inputs/PLAN.json','inputs/PLANS.json','prepared/PLAN.json','prepared-v1/PLAN.json','prepared-v2/PLAN.json','SEED_AUDIT.json','inputs/SEED_AUDIT.json','prepared/SEED_AUDIT.json'):
            path=directory/name
            if not path.is_file() or path.stat().st_size>4*1024*1024:continue
            text=path.read_text();scanned.append({'path':str(path),'sha256':s.sha(path)})
            if any(str(seed) in text for seed in (s.MASTER,*s.SEEDS)):collisions.append(str(path))
    if collisions:raise ValueError('seed metadata collision: '+repr(collisions))
    for name,value in [('PUBLIC.json',contexts),('HOST_GOLD.json',gold),('TASKS.json',tasks),('PLAN.json',plan),
        ('PROMPTS.json',prompts),('PAIRS.json',pairs),('NATIVE_TEMPLATE.json',template),
        ('SEED_AUDIT.json',{'master':s.MASTER,'sampling_seeds':s.SEEDS,'scanned':scanned,'collisions':collisions,'bounded_scope':True}),
        ('FIXED8.json',{'selected':s.final8_identity(),'result_sha256':s.RESULT_SHA,'selection_rule':'fixed8 availability, no readout consulted'})]:s.write(s.ROOT/'inputs'/name,value)
    for name in ('PUBLIC.json','HOST_GOLD.json','TASKS.json','NATIVE_TEMPLATE.json'):
        if s.sha(s.ROOT/'inputs'/name)!=s.sha(s.OLD/'inputs'/name):raise ValueError('copied immutable input bytes differ')
    tests=subprocess.run([str(s.NATIVE),'-m','unittest','discover','-s',str(s.ROOT),'-p','test_*.py','-v'],capture_output=True,text=True)
    s.write(s.ROOT/'CPU_TESTS.json',{'argv':tests.args,'exit_code':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,
        'prior_red':'five missing-implementation failures; inherited sys.path leakage reproduced by dispatch import-order test, then privately contained; no model reroll'})
    if tests.returncode:raise ValueError('focused tests failed')
    spec={'schema':s.ROOT.name,'plan':plan,'bindings':bindings,'root_order':s.WEIGHTS,'arms':s.ARMS,'master_seed':s.MASTER,'sampling_seeds':s.SEEDS,
        'planned_episodes':48,'context_clusters':4,'environment':adapter.environment(),
        'caps':{'per_root_collection_seconds':900,'shared_work_seconds':2550,'owned_seconds':2670,'outer_seconds':2700,'final_cleanup_reserve_seconds':120},
        'primary':'coverage_first minus always_counts within each fixed root, strict whole ASCII Answer:N; completed wrong/empty0; infrastructure/unavailable NULL',
        'secondary':'map contrasts and root interaction exploratory; four exposed clusters; source/native-corroborated coverage/partial totals/physical cost',
        'projection':'omit counts key only in added coverage_first suffix until summary.partial false; no original observation redaction, target, gold or completion gate',
        'initial_prefix_unchanged':True,'initial_max_prompt_tokens':max(len(p['token_ids']) for p in prompts),'root_grammar':False,
        'sampling':{'temperature':.5,'top_p':1,'top_k':-1,'min_p':0,'max_tokens':2048},
        'retries':'no episode retry/replacement; native request hook rejects repeated wire request within one logical call; all recorded attempts retained',
        'qualification':str(qualification),'qualification_sha256':s.sha(qualification/'RESULT.json'),
        'source_bound_ledger_trust':'runtime-writable claims; corroborate native branches/returned children/actual tool observation; broker drain is not caller-read acknowledgement',
        'exposure':'four named previously exposed global contexts, not independent new task evidence'}
    s.write(s.ROOT/'SPEC.json',spec)
    pins=dict(s.old_pins());pins[str(s.OLD/'READY.json')]=s.READY_SHA
    training_ready=s.TRAINING.parents[2]/'READY.json';pins[str(training_ready)]=s.sha(training_ready)
    pins.update(s.read(training_ready)['source_sha256'])
    for path in [s.TRAINING/'RESULT.json',s.TRAINING/'checkpoint-0008/state.json',
        s.STORE/'ideas/2026-09-09-coverage-first-root-options.md',s.STORE/'ideas/2026-09-09-coverage-first-root-main-approval.md']:
        pins[str(path)]=s.sha(path)
    for name,want in s.read(s.TRAINING/'checkpoint-0008/state.json')['files_sha256'].items():pins[str(s.TRAINING/'checkpoint-0008'/name)]=want
    for binding in bindings.values():
        for model in binding['models'].values():
            for name,key in [('adapter_model.safetensors','adapter_sha256'),('adapter_config.json','config_sha256')]:pins[str(Path(model['path'])/name)]=model[key]
    for path in list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+list((s.ROOT/'inputs').glob('*.json'))+[s.ROOT/'SPEC.json',s.ROOT/'CPU_TESTS.json']+list(qualification.rglob('*.json')):pins[str(path.resolve())]=s.sha(path)
    for path,want in pins.items():s.check(path,want)
    s.write(s.ROOT/'READY.json',{'status':'CPU_READY_NOT_LAUNCH_AUTHORITY','prepared_epoch':time.time(),'source_sha256':pins,
        'spec_sha256':s.sha(s.ROOT/'SPEC.json'),'planned_episodes':48,'caps':spec['caps'],'phase_order':s.WEIGHTS,
        'launch_argv':[str(s.NATIVE),str(s.ROOT/'driver.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
        'qualification_sha256':spec['qualification_sha256'],'gpu_calls_in_preparation':0,'actual_model_calls_in_preparation':0})
    print(json.dumps({'READY_sha256':s.sha(s.ROOT/'READY.json'),'source_paths':len(pins),'planned':48,'max_prompt':spec['initial_max_prompt_tokens']},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--qualification',type=Path,required=True);prepare(p.parse_args().qualification.resolve())
