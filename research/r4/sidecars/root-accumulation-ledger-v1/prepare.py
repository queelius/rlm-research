"""CPU-only frozen input/source preparation; READY is the final write."""
import argparse
import json
import subprocess
import time
from pathlib import Path
import study as s
import adapter
import overlay

def prepare(qualification):
    if (s.ROOT/'READY.json').exists():raise ValueError('already frozen')
    result=s.read(qualification/'RESULT.json')
    if result.get('status')!='PASS' or result['provider_calls']!=12 or result['gpu_calls']!=0:raise ValueError('missing scoped native fixture')
    contexts,gold,alltasks=s.inputs();plan=s.plan_for(contexts);binding=s.binding();st=s.stack()
    tasks={r['task_name']:alltasks[r['task_name']] for r in plan}
    checks=[];prompts=[]
    template=s.read(qualification/'map/EPISODE.json')['traces'][0]
    system=template['nodes'][0]['message'];tools=st.native.wire_tools(template['tools']);renderer=st.native.renderer()
    fixture_tokens=renderer.render([system,{'role':'user','content':'Use records.json and batch_contract.py. Return only Answer: N.'}],tools=tools,add_generation_prompt=True).token_ids
    first=s.read(qualification/'PROVIDER_REQUESTS.json')[0]['body']['token_ids']
    if fixture_tokens!=first:raise ValueError('renderer does not reproduce actual fixture root prefix')
    for offset in range(0,len(plan),2):
        left,right=plan[offset:offset+2];context=next(c for c in contexts if c['id']==left['context_id'])
        a=adapter.task(context,tasks[left['task_name']]['prompt'],gold[context['id']],left['task_name'],left)
        b=adapter.task(context,tasks[right['task_name']]['prompt'],gold[context['id']],right['task_name'],right)
        if a.hash!=b.hash or a.data.model_dump()!=b.data.model_dump():raise ValueError('paired root task/prompt changed')
        checks.append({'pair_id':left['pair_id'],'task_hash':a.hash,'identical_data_and_prompt':True,'seed':left['seed']})
        tokens=renderer.render([system,{'role':'user','content':a.data.prompt}],tools=tools,add_generation_prompt=True).token_ids
        for row in (left,right):prompts.append({'id':row['id'],'token_ids':tokens,'task_hash':a.hash,'prompt_sha256':s.digest(a.data.prompt)})
    # Fresh-seed search is limited to small frozen prospective manifests, not outcome graphs.
    scanned=[];collisions=[]
    for directory in s.SIDE.iterdir():
        for name in ('SPEC.json','CAMPAIGN.json','RECIPE.json','inputs/PLAN.json','inputs/PLANS.json'):
            path=directory/name
            if directory==s.ROOT or not path.is_file() or path.stat().st_size>4*1024*1024:continue
            text=path.read_text();scanned.append({'path':str(path),'sha256':s.sha(path)})
            if any(str(seed) in text for seed in (s.MASTER,*s.SEEDS)):collisions.append(str(path))
    if collisions:raise ValueError('proposed seed collision: '+repr(collisions))
    for name,value in [('PUBLIC.json',contexts),('HOST_GOLD.json',gold),('TASKS.json',tasks),('PLAN.json',plan),
                       ('PROMPT_PAIRS.json',checks),('PROMPTS.json',prompts),('NATIVE_TEMPLATE.json',{'system':system,'tools_ordered_json':json.dumps(tools)}),
                       ('SEED_AUDIT.json',{'master':s.MASTER,'seeds':s.SEEDS,'scanned':scanned,'collisions':collisions})]:s.write(s.ROOT/'inputs'/name,value)
    pins=dict(s.read(s.PRIOR/'READY.json')['source_sha256'])
    local=s.read(s.SIDE/'runtime-local-cache-v1/CPU_READY.json');pins.update(local['source_and_artifact_sha256'])
    for path in [s.PRIOR/'READY.json',s.ADAPTIVE/'study.py',s.ADAPTIVE/'native.py',s.ADAPTIVE/'inputs/TASKS.json',
                 s.LOCAL/'adapter.py',s.LOCAL/'READY.json',s.LOCAL/'outputs/attempt-001/training/RESULT.json',
                 s.SIDE/'runtime-local-cache-v1/CPU_READY.json',overlay.SUPERVISOR,
                 s.ROOT.parents[1]/'ideas/2026-09-09-accumulation-ledger-options.md']:
        pins[str(path)]=s.sha(path)
    for model in binding['models'].values():
        for filename,want in [('adapter_model.safetensors',model['adapter_sha256']),('adapter_config.json',model['config_sha256'])]:
            path=Path(model['path'])/filename;s.check(path,want);pins[str(path)]=want
    test=subprocess.run([str(s.NATIVE),'-m','unittest','discover','-s',str(s.ROOT),'-p','test_*.py','-v'],capture_output=True,text=True)
    s.write(s.ROOT/'CPU_TESTS.json',{'argv':test.args,'exit_code':test.returncode,'stdout':test.stdout,'stderr':test.stderr,
        'prior_red':'3 missing-ledger tests;1 missing-dispatch test. Local test event index corrected for initialized event; one wrong-cwd discovery command failed, no fixture/model reroll.'})
    if test.returncode:raise ValueError('focused tests failed')
    spec={'schema':s.ROOT.name,'plan':plan,'binding':binding,'master_seed':s.MASTER,'seeds':s.SEEDS,
          'planned_episodes':16,'context_clusters':4,'environment':adapter.environment(),
          'caps':{'collection_seconds':1200,'shared_work_seconds':1650,'inclusive_owned_seconds':1770,'outer_seconds':1800,'cleanup_seconds':120},
          'primary':'whole ASCII Answer integer, completed empty/wrong0; unavailable infrastructure NULL; all16 planned',
          'exposure':'exact four old validation global contexts; exploratory whole-policy harness comparison',
          'root_initial_prompt_identical':True,'root_grammar':False,'child_grammar':'exact public batch contract, fixed canonical6',
          'ledger':'delivered strict source-bound maps; all6 counts; dedup conflicts excluded; root-only observation after unchanged original truncation',
          'retries':'no new episode retry/replacement; inherited transient native retries possible within common cap',
          'image_id':local['image_id'],'qualified_runtime_ready_sha256':s.sha(s.SIDE/'runtime-local-cache-v1/CPU_READY.json'),
          'qualification':str(qualification),'qualification_sha256':s.sha(qualification/'RESULT.json')}
    s.write(s.ROOT/'SPEC.json',spec)
    for path in list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+list((s.ROOT/'inputs').glob('*.json'))+[s.ROOT/'SPEC.json',s.ROOT/'CPU_TESTS.json']+list(qualification.rglob('*.json')):
        pins[str(path.resolve())]=s.sha(path)
    # Authenticate closure once at preparation, not per episode.
    for path,want in pins.items():s.check(path,want)
    s.write(s.ROOT/'READY.json',{'status':'CPU_READY_NOT_LAUNCH_AUTHORITY','schema':s.ROOT.name,'prepared_epoch':time.time(),
        'planned_episodes':16,'source_sha256':pins,'spec_sha256':s.sha(s.ROOT/'SPEC.json'),'caps':spec['caps'],
        'launch_argv':[str(s.NATIVE),str(s.ROOT/'driver.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
        'gpu_calls_in_preparation':0,'actual_model_calls_in_preparation':0,'qualification_sha256':spec['qualification_sha256']})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--qualification',type=Path,required=True);prepare(p.parse_args().qualification.resolve())
