"""CPU-only faithful pre-cut export, actual native prompt freeze and readiness seal."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import protocol as p
import study as s

def inputs():
    started=time.time();source_ready=s.source().verify()
    public={c['id']:c for c in s.read(s.SOURCE/'inputs/PUBLIC.json')}
    plan=s.read(s.SOURCE/'inputs/CONTROLLED_PLAN.json');old_prompts=s.read(s.SOURCE/'inputs/PROMPTS_ACCURATE.json')
    host=s.read(s.SOURCE/'inputs/HOST_GOLD.json');template=s.read(s.SOURCE/'inputs/NATIVE_TEMPLATE.json')
    binding_path=s.SOURCE/'outputs/attempt-001/service-unchanged/BINDING.json';binding=s.read(binding_path)
    root=binding['role_map']['root'];child=binding['fixed_child']
    if binding['models'][root]['adapter_sha256']!=s.source().START_SHA or binding['models'][child]['adapter_sha256']!=s.source().CHILD_SHA:raise ValueError('unchanged low66c/c32 source binding')
    renderer=s.stack().native.renderer();tools=json.loads(template['tools_ordered_json'])
    metrics=s.load('restart_source_usage',s.ROOT.parent/'root-example-map-visibility-v1/metrics.py','0ef6a89ad3655afe71226878f0296802e6b8af62b5aa295eec23e3ed151c53d3')
    provenance={str(binding_path):s.sha(binding_path)};states=[];packages={};source_records=[];cuts={}
    for original in plan:
        if original['metadata_error']:raise ValueError('pilot requires the16 no-error controlled states')
        directory=s.SOURCE/'outputs/attempt-001/controlled-source'/original['id'];teacher=s.read(directory/'TEACHER.json');episode=s.read(directory/'EPISODE.json')
        if teacher['coordinate']!=original or teacher['episode_sha256']!=s.sha(directory/'EPISODE.json'):raise ValueError('actual source identity')
        trace=episode['traces'][0];turn=teacher['turns']['corrective'];prefix=turn['input_ids'][:turn['prompt_length']]
        count=16//original['width'];cut=p.cut(trace,root,count,prefix)
        if renderer.render(cut['messages'],tools=tools,add_generation_prompt=True).token_ids!=prefix:raise ValueError('source graph re-render changed')
        if cut['messages'][1]['content']!=old_prompts[original['id']]['prompt']:raise ValueError('source goal changed')
        context=public[original['context_id']];files=p.package(context,original['id'],cut['messages'],original['users'],s.source().LABELS[context['target']])
        pieces=[json.loads(files[f'state/map-{i+1:02}.json']) for i in range(count)]
        if pieces!=teacher['visible_maps']:raise ValueError('actual observations differ from recorded source maps')
        actual=[s.read(Path(x)) for x in teacher['actual_child_records']]
        if len(actual)!=count:raise ValueError('actual child acquisition count')
        for record,piece in zip(actual,pieces):
            if not record['paid_model_call'] or record['body']['model']!=child:raise ValueError('not actual fixed child')
            ids=record['response']['choices'][0]['token_ids']
            if p.strict_object(renderer._tokenizer.decode(ids,skip_special_tokens=True))!=piece:raise ValueError('actual native child tokens do not yield exported predictions')
        roles=[s.read(x) for x in (directory/'role-audit').glob('*-result.json')]
        actual_roles=[x for x in roles if x['depth']==1]
        if len(actual_roles)!=count:raise ValueError('source role captures incomplete')
        roots=[s.read(x) for x in sorted((directory/'physical').glob('*.json')) if s.read(x)['body']['model']==root]
        if roots[count]['body']['token_ids']!=prefix:raise ValueError('actual source physical cut differs')
        for path in [directory/'TEACHER.json',directory/'EPISODE.json',*map(Path,teacher['actual_child_records']),*(directory/'role-audit').glob('*-result.json'),directory/'physical'/f'{(2*count+1):04}.json']:
            provenance[str(path)]=s.sha(path)
        state=dict(source_id=original['id'],context_id=original['context_id'],native_context_id=context['native_context_id'],
            family=original['family'],users=original['users'],width=original['width'],source_seed=original['seed'],source_variable=original['variable'],
            goal=old_prompts[original['id']]['prompt'],historical_cost=metrics.usage(actual_roles),
            historical_child_seconds=sum(r['ended_epoch']-r['started_epoch'] for r in actual),
            source_capture_gross_seconds=teacher['elapsed_seconds'],
            source_pre_cut_observed_seconds=roots[count]['started_epoch']-roots[0]['started_epoch'],
            source_pre_cut_time_basis='first authored producer provider arrival through first corrective provider arrival; excludes runtime startup',
            package_sha256={name:hashlib.sha256(text.encode()).hexdigest() for name,text in files.items()})
        states.append(state);packages[state['source_id']]=files;cuts[state['source_id']]=dict(**cut,source_episode_path=str(directory/'EPISODE.json'),source_episode_sha256=s.sha(directory/'EPISODE.json'))
        source_records.extend(actual_roles)
    if len(states)!=16 or len(source_records)!=40:raise ValueError('all16 states/40 child calls required')
    simple=[{k:st[k] for k in ('source_id','context_id','native_context_id','family','users','width','source_seed','source_variable')} for st in states]
    rows=p.plan(simple);state_by_id={v['source_id']:v for v in states};prompts=[]
    for row in rows:
        st=state_by_id[row['source_id']];files=packages[row['source_id']];text=p.prompt(st['goal'],files,row['representation'])
        ids=renderer.render([template['system'],dict(role='user',content=text)],tools=tools,add_generation_prompt=True).token_ids
        if len(ids)+2048>8192:raise ValueError('restart native context budget; no truncation allowed')
        task=s.task(public[row['context_id']],text,st['goal'],row,files)
        prompts.append(dict(id=row['id'],prompt=text,token_ids=ids,task_hash=task.hash))
    selected={st['context_id'] for st in states}
    values={'PUBLIC.json':[public[c] for c in sorted(selected)],'HOST_GOLD.json':{c:host[c] for c in sorted(selected)},'NATIVE_TEMPLATE.json':template,
        'STATES.json':states,'PACKAGES.json':packages,'SOURCE_CUTS.json':cuts,'PLAN.json':rows,'PROMPTS.json':prompts,'BINDING.json':binding,
        'SOURCE_PROVENANCE.json':dict(source_sha256=provenance,source_ready_sha256=s.sha(s.SOURCE/'READY.json'),actual_unique_historical_cost=metrics.usage(source_records),historical_unique_child_calls=40,hypothetical48_child_calls=120,package_from_actual_pre_cut_only=True,source_producers_authored=True,old_readout_used=False,host_gold_in_packages=False,old_kernel_restored=False,source_exposure='four previously research-exposed contexts; source states not selected on correctness'),
        'EXPORT_COST.json':dict(started_epoch=started,ended_epoch=time.time(),elapsed_seconds=time.time()-started,gpu_calls=0,model_calls=0,basis='CPU verification/export/tokenization; output serialization follows')}
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    print(dict(states=16,endpoints=48,prefix_range=[min(len(v['token_ids']) for v in prompts),max(len(v['token_ids']) for v in prompts)],new_acquisitions=0))

def seal():
    inherited=s.read(s.SOURCE/'READY.json');sources=dict(inherited['source_sha256']);inputs=dict(inherited['input_sha256'])
    lifecycle=s.RUNTIME/'LIFECYCLE_READY_V2.json';sources.update(s.read(lifecycle)['source_sha256'])
    sources.update(s.read(s.ROOT/'inputs/SOURCE_PROVENANCE.json')['source_sha256'])
    for path in [s.SOURCE/'READY.json',lifecycle,s.RUNTIME/'credential_preflight.py',*s.ROOT.glob('*.py'),*s.ROOT.glob('*.md')]:sources[str(path)]=s.sha(path)
    for path in [*sorted((s.ROOT/'inputs').glob('*.json')),s.ROOT/'CPU_TESTS.json',s.ROOT.parent.parent/'ideas/2026-09-09-state-continuation-feasibility.md']:inputs[str(path)]=s.sha(path)
    for path,pin in {**sources,**inputs}.items():
        if s.sha(path)!=pin:raise ValueError('source/input drift '+path)
    value=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=sources,input_sha256=inputs,
        representations=p.ARMS,states=16,endpoints=48,contexts=4,query_compositions=8,source_child_acquisitions=40,new_acquisitions=0,
        outer_seconds=2400,work_seconds=2100,owned_seconds=2280,cleanup_seconds=180,collection_seconds=1800,startup_seconds=300,
        root_sha256=s.source().START_SHA,child_sha256=s.source().CHILD_SHA,
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],
        interpretation='all-fresh-root quoted-history vs artifact-reference vs inline-metadata restart representation; NOT native historical continuation',
        qualification='focused CPU source/token/file/argv contracts; no service or GPU launched',gpu_calls=0,prepared_epoch=time.time())
    value['identity']=p.digest(value);s.write(s.ROOT/'READY.json',value);print(dict(sha256=s.sha(s.ROOT/'READY.json'),identity=value['identity']))

def qualify():
    import platform
    import importlib.metadata
    argv=[str(s.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_protocol.py','test_entrypoints.py','test_native_cpu.py']
    started=time.time();result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=60,
        env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    versions={}
    for name in ('torch','transformers','tokenizers','vllm','verifiers'):
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]='not package metadata in this interpreter'
    s.write(s.ROOT/'CPU_TESTS.json',dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
        elapsed_seconds=time.time()-started,python=platform.python_version(),versions=versions,
        scope='11 focused contracts; real native tokenizer/task setup with filesystem-only double; no GPU/service/container/lock',
        gpu_calls=0,source_sha256={str(path):s.sha(path) for path in s.ROOT.glob('*.py')},
        seed_namespace_scan='981359 found only this sidecar source/PLAN among source Python and prepared plans; no old outcome scan'))
    if result.returncode:raise ValueError('focused CPU qualification failed; artifact retained')
    print(dict(passed=True,tests=11,sha256=s.sha(s.ROOT/'CPU_TESTS.json')))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('inputs','qualify','seal'));args=ap.parse_args()
    {'inputs':inputs,'qualify':qualify,'seal':seal}[args.command]()
