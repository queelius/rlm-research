"""Frozen prospective inputs, CPU grammar/native proof, closure; READY last."""
import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path
import study as s
import adapter
import bridge
import overlay
import qualify

def grammar_checks(contexts):
    import xgrammar as xgr
    from transformers import AutoTokenizer
    base=s.stack().prior.BASE;tokenizer=AutoTokenizer.from_pretrained(str(base),local_files_only=True,trust_remote_code=False)
    compiler=xgr.GrammarCompiler(xgr.TokenizerInfo.from_huggingface(tokenizer,vocab_size=s.read(base/'config.json')['vocab_size']),max_threads=2,cache_enabled=True)
    proofs=[]
    # Runtime selects arbitrary subsets; qualify boundary widths and full actual catalogs,
    # including nonascending requested IDs, using synthetic labels only.
    for width in (1,4,16,32,64,128):
        ids=[f'q{i:04d}' for i in range(width,0,-1)]
        for arm in ('array','map'):
            schema=bridge.schema(ids,arm);compiled=compiler.compile_json_schema(bridge.encoded(schema),any_whitespace=True)
            labels=['location']*width;good=labels if arm=='array' else dict(zip(ids,labels,strict=True))
            matcher=xgr.GrammarMatcher(compiled)
            if not matcher.accept_string(bridge.encoded(good).encode()) or not matcher.is_completed():raise ValueError('valid schema fixture rejected')
            bad=labels[:-1] if arm=='array' else {**good,'unknown':'location'}
            matcher=xgr.GrammarMatcher(compiled)
            if matcher.accept_string(bridge.encoded(bad).encode()) and matcher.is_completed():raise ValueError('wrong cardinality/ID accepted')
            proofs.append({'arm':arm,'width':width,'schema_ordered_json':bridge.encoded(schema),'schema_sha256':bridge.digest(schema),
                'valid_synthetic_accepted':True,'invalid_cardinality_or_unknown_rejected':True})
    return proofs

def prepare(qualification):
    if (s.ROOT/'READY.json').exists():raise ValueError('already frozen')
    os.sched_setaffinity(0,{34,35});result=s.read(qualification/'RESULT.json')
    if result['status']!='PASS' or result['provider_calls']!=6 or result['gpu_calls']!=0 or not result['subsequent_root_wire_equal_for_same_projected_evidence']:raise ValueError('native bridge qualification missing')
    contexts,gold,tasks=s.inputs();plan=s.plan_for(contexts);binding=s.binding();st=s.stack()
    template=s.read(qualification/'array/EPISODE.json')['traces'][0];system=template['nodes'][0]['message']
    tools=st.native.wire_tools(template['tools']);renderer=st.native.renderer()
    tokens=renderer.render([system,{'role':'user','content':qualify.FIXTURE_PROMPT}],tools=tools,add_generation_prompt=True).token_ids
    if tokens!=s.read(qualification/'PROVIDER_REQUESTS.json')[0]['body']['token_ids']:raise ValueError('actual root renderer differs')
    prompts=[];pairs=[]
    for offset in range(0,len(plan),2):
        a,b=plan[offset:offset+2];context=next(c for c in contexts if c['id']==a['context_id']);target=gold[context['id']]['answers'][a['family']]
        left=adapter.task(context,tasks[a['task_name']]['prompt'],target,a['task_name'],a)
        right=adapter.task(context,tasks[b['task_name']]['prompt'],target,b['task_name'],b)
        if left.hash!=right.hash or left.data.model_dump()!=right.data.model_dump():raise ValueError('root task differs within pair')
        tokens=renderer.render([system,{'role':'user','content':left.data.prompt}],tools=tools,add_generation_prompt=True).token_ids
        if len(tokens)+1536>8192:raise ValueError('full initial root prompt does not fit; no crop')
        pairs.append({'pair_id':a['pair_id'],'task_hash':left.hash,'root_prompt_data_equal':True,'tokens':len(tokens)})
        for row in (a,b):prompts.append({'id':row['id'],'token_ids':tokens,'task_hash':left.hash,'prompt_sha256':s.digest(left.data.prompt)})
    scanned=[];collisions=[];pattern=re.compile(r'\b(?:'+ '|'.join(map(str,(s.MASTER,*s.SEEDS)))+r')\b')
    for directory in s.SIDE.iterdir():
        for name in ('SPEC.json','RECIPE.json','CAMPAIGN.json','inputs/PLAN.json','inputs/PLANS.json','prepared/PLAN.json','prepared-v2/PLAN.json'):
            path=directory/name
            if directory==s.ROOT or not path.is_file() or path.stat().st_size>4*1024*1024:continue
            text=path.read_text();scanned.append({'path':str(path),'sha256':s.sha(path)})
            if pattern.search(text):collisions.append(str(path))
    if collisions:raise ValueError('fresh seed collision: '+repr(collisions))
    values={'PUBLIC.json':contexts,'HOST_GOLD.json':gold,'TASKS.json':tasks,'PLAN.json':plan,'PROMPTS.json':prompts,
        'PROMPT_PAIRS.json':pairs,'NATIVE_TEMPLATE.json':{'system':system,'tools_ordered_json':json.dumps(tools)},
        'GRAMMAR_PROOF.json':grammar_checks(contexts),'SEED_AUDIT.json':{'master':s.MASTER,'seeds':s.SEEDS,'scanned':scanned,'collisions':collisions}}
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    test=subprocess.run([str(s.NATIVE),'-m','unittest','discover','-s',str(s.ROOT),'-p','test_*.py','-v'],capture_output=True,text=True)
    s.write(s.ROOT/'CPU_TESTS.json',{'argv':test.args,'exit_code':test.returncode,'stdout':test.stdout,'stderr':test.stderr,
        'red_evidence':'3 absent bridge failures;2 absent collector failures;2 absent scorer failures;fixed-context regression reproduced missing global query key before correction'})
    if test.returncode:raise ValueError('focused tests failed')
    local=s.read(s.SIDE/'runtime-local-cache-v1/CPU_READY.json')
    spec={'schema':s.ROOT.name,'plan':plan,'binding':binding,'master_seed':s.MASTER,'seeds':s.SEEDS,'planned_episodes':32,
        'context_clusters':4,'environment':adapter.environment(),'primary':'checksum map-minus-array strict whole ASCII Answer; count separate',
        'null_rule':'observed completed empty/malformed/wrong0; incomplete or unavailable NULL; all32 denominator',
        'caps':{'collection_seconds':1500,'shared_work_seconds':1650,'inclusive_owned_seconds':1770,'outer_seconds':1800,'cleanup_seconds':120},
        'source_contexts':list(s.CONTEXTS),'child_representation':['array','map'],'root_initial_prompt_identical_within_task_pair':True,
        'root_grammar':False,'child_intervention':'exact source-bound depth1 child output instruction and ordered schema; native untouched; broker-only map projection',
        'retry_policy':'no new study retry/replacement; inherited transient native retries possible within same cap',
        'image_id':local['image_id'],'qualified_runtime_ready_sha256':s.sha(s.SIDE/'runtime-local-cache-v1/CPU_READY.json'),
        'qualification':str(qualification),'qualification_sha256':s.sha(qualification/'RESULT.json')}
    s.write(s.ROOT/'SPEC.json',spec)
    pins=dict(s.read(s.OLD/'READY.json')['source_sha256'])
    for path in [s.OLD/'READY.json',s.OLD/'study.py',s.OLD/'overlay.py',s.OLD/'collect.py',s.OLD/'driver.py',
        s.PRIOR/'prepared-v2/PUBLIC.json',s.PRIOR/'prepared-v2/HOST_GOLD.json',s.ADAPTIVE/'inputs/TASKS.json',
        s.ROOT.parents[1]/'ideas/2026-09-09-checksum-bridge-main-approval.md',
        s.ROOT.parents[1]/'ideas/2026-09-09-correspondence-to-rlm-checksum-amendment.md']:
        pins[str(path)]=s.sha(path)
    for model in binding['models'].values():
        for file,key in [('adapter_model.safetensors','adapter_sha256'),('adapter_config.json','config_sha256')]:
            path=Path(model['path'])/file;s.check(path,model[key]);pins[str(path)]=model[key]
    for path in list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+list((s.ROOT/'inputs').glob('*.json'))+[s.ROOT/'SPEC.json',s.ROOT/'CPU_TESTS.json']+list(qualification.rglob('*.json'))+list((s.ROOT/'qualification-001').rglob('*.json')):
        pins[str(path.resolve())]=s.sha(path)
    for path,want in pins.items():s.check(path,want)
    s.write(s.ROOT/'READY.json',{'status':'CPU_READY_NOT_LAUNCH_AUTHORITY','schema':s.ROOT.name,'prepared_epoch':time.time(),
        'planned_episodes':32,'source_sha256':pins,'spec_sha256':s.sha(s.ROOT/'SPEC.json'),'caps':spec['caps'],
        'launch_argv':[str(s.NATIVE),str(s.ROOT/'driver.py'),'run','--output',str(s.ROOT/'outputs/attempt-001')],
        'gpu_calls_in_preparation':0,'actual_model_calls_in_preparation':0,'qualification_sha256':spec['qualification_sha256']})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--qualification',type=Path,required=True)
    prepare(p.parse_args().qualification.resolve())
