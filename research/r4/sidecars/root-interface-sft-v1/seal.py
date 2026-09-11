"""CPU final freeze; READY is the final publication operation."""
import importlib.metadata
import json
import time
from pathlib import Path
import study as s
import native as n
import interface

def seal():
    prepared=s.ROOT/'prepared-v2'
    q=s.read(prepared/'QUALIFICATION.json')
    if q['status']!='PASS':raise ValueError('native qualification incomplete')
    typed_proof=s.ROOT/'qualification-typed-001/RESULT.json'
    if s.read(typed_proof)['status']!='PASS':raise ValueError('typed new-catalog native qualification incomplete')
    binding=n.initial_binding();root=binding['campaign_policy']
    expected={'adapter_model.safetensors':s.START_SHA,'adapter_config.json':root['config_sha256'],'optimizer.pt':root['optimizer_sha256'],'rng_state.pt':root['rng_sha256'],'state.json':root['state_sha256']}
    for name,sha in expected.items():s.check(s.START/name,sha)
    # Base artifact manifest is pinned; training validates actual base files once before load.
    base_manifest=s.BASE/'local-research-manifest.json'
    s.check(base_manifest,'19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f')
    source=dict(s.read(s.ROOT.parent/'adaptive-filter-pilot-v1/SPEC.json')['source_file_sha256'])
    source.update({str(p):s.sha(p) for p in [s.ROOT.parent/'leaf-post-sft-suite-v1/suite.py',s.ROOT.parent/'root-seed-lifecycle-continuation-v1/driver.py',s.ROOT.parent/'trec-leaf-sft-v1/source/data.py',s.ROOT.parent/'trec-leaf-sft-v1/source/experiment.py',base_manifest]})
    rows=s.read(prepared/'ROWS.json');public=s.read(prepared/'PUBLIC.json');plan=s.plan(public)
    final_rows=[]
    for row in rows:
        cid='-'.join(row['id'].split('-')[:2]);context=next(c for c in public if c['id']==cid)
        final_rows.append({**row,'context_id':cid,'context_window_id':s.context_window_id(context),'source_group_ids':context['group_ids'],'raw_prepared_rows_sha256':s.sha(prepared/'ROWS.json'),'native_metadata_note':'16 metadata executions retain old fixture bookkeeping IDs in raw traces; exact new public text/context group mapping is bound here. IDs do not enter prompt. New-ID typed owned proof confirms unchanged physical first prefix; runtime evaluation uses truthful new IDs.'})
    s.write(prepared/'TRAINING_ROWS_FINAL.json',final_rows)
    s.write(prepared/'EVAL_PLAN_FINAL.json',plan)
    source.update(s.read(interface.ROOT/'SPEC.json')['source_file_sha256'])
    source.update({str(interface.ROOT/file):sha for file,sha in interface.PINS.items()})
    source.update({str(p):s.sha(p) for p in (s.ROOT/'qualification-typed-001').rglob('*.json') if 'runtime-cache' not in p.parts})
    source[str(s.ROOT/'CPU_TESTS.json')]=s.sha(s.ROOT/'CPU_TESTS.json')
    template=s.read(prepared/'NATIVE_TEMPLATE.json');renderer=n.renderer();tools=json.loads(template['tools_ordered_json'])
    prompts=[]
    for r in plan:
        c=next(c for c in public if c['id']==r['context_id'])
        tokenids=renderer.render([template['system'],{'role':'user','content':s.prompt(c,r['family'])}],tools=tools,add_generation_prompt=True).token_ids
        if len(tokenids)+2048>8192:raise ValueError('root input+output exceeds native context')
        prompts.append(dict(id=r['id'],prompt=s.prompt(c,r['family']),token_ids=tokenids,token_ids_sha256=s.digest(tokenids)))
    s.write(prepared/'EVAL_PROMPTS.json',prompts)
    seeds={r['seed'] for r in plan}|{981284001,981284002,981284003}
    audit=[]
    def all_seeds(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if 'seed' in k and isinstance(v,int):yield v
                yield from all_seeds(v)
        elif isinstance(value,list):
            for v in value:yield from all_seeds(v)
    for p in (s.ROOT.parent/'adaptive-filter-pilot-v1/SPEC.json',s.ROOT.parent/'root-receipt-uptake-v1/SPEC.json',s.ROOT.parent/'root-broad-curriculum-v1/RECIPE.json',s.ROOT.parent/'typed-helper-child-v1/SPEC.json'):
        collision=sorted(seeds&set(all_seeds(s.read(p))))
        if collision:raise ValueError('named source seed collision '+str(p))
        audit.append(dict(path=str(p),sha256=s.sha(p),collision=[]))
    s.write(prepared/'SEED_AUDIT.json',dict(scope='Only four named prior specs/recipes, not global store',sources=audit,seeds=sorted(seeds)))
    recipe=dict(schema='root-interface-authored-sft-v1',prepared=str(prepared),epochs=2,effective_batch=16,microbatch=1,updates=4,lr=1e-4,weight_decay=0,clip=1,train_seed=981284002,max_causal_tokens=8192,training_cap_seconds=600,owned_cap_seconds=3300,outer_cap_seconds=3330,collection_cap_each=900,root_start=str(s.START),starting_files_sha256=expected,base_manifest_sha256=s.sha(base_manifest),base_dtype='bfloat16',adapter_dtype='float32',fresh_optimizer=True,selection='fixed final4, not validation-selected',child_interface={'kind':'typed_batch','pins':interface.PINS,'rule':'same fixed child/typed public batch matcher for both roots; no root grammar/no response repair','decision':'Parent chose typed interface before either new-model readout to control known native child protocol bottleneck'},record_exposures=64,target_token_exposures=2*sum(r['target_tokens'] for r in rows),input_token_exposures=2*sum(len(r['input_ids']) for r in rows),input_sha256={str(p):s.sha(p) for p in prepared.rglob('*.json')},source_file_sha256=source)
    s.write(s.ROOT/'RECIPE.json',recipe)
    source.update({str(p):s.sha(p) for p in list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+list((s.ROOT/'tests').glob('*.py'))+[s.ROOT/'RECIPE.json']})
    identity=s.digest(dict(source=source,recipe=recipe))
    ready=dict(schema='root-interface-sft-ready-v1',status='CPU_READY_PARENT_LAUNCH_ONLY',identity=identity,source_sha256=source,recipe_sha256=s.sha(s.ROOT/'RECIPE.json'),qualification_sha256=s.sha(prepared/'QUALIFICATION.json'),launch_argv=[str(s.NATIVE),str(s.ROOT/'launch.py'),'--output',str(s.ROOT/'outputs/attempt-001')],caps=dict(train=600,owned=3300,outer=3330,collect_each=900),training_rows=32,updates=4,evaluation_episodes=48,gpu_calls_in_preparation=0)
    s.write(s.ROOT/'READY.json',ready)
    print(json.dumps(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=identity)))

if __name__=='__main__':seal()
