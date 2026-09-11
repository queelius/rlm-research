"""CPU preparation and immutable source closure; no runtime/model launch."""
import argparse
import json
import hashlib

import metrics
import time

import protocol
import study as s


def prepare():
    data = s.read(s.SOURCE / 'DATA_READY.json')
    for path, pin in data['data_sha256'].items():
        if s.sha(path) != pin:
            raise ValueError('panel changed')
    public = s.read(s.SOURCE / 'prepared/PUBLIC.json')
    host = s.read(s.SOURCE / 'prepared/HOST_GOLD.json')
    if public != s.read(s.SOURCE / 'data/PUBLIC.json') or host != s.read(s.SOURCE / 'data/HOST_GOLD.json'):
        raise ValueError('prepared/data panel differs')
    provenance = s.read(s.MAP_SOURCE / 'outputs/attempt-001/rollout/MAPS_READY.json')
    map_ready = s.MAP_SOURCE / 'outputs/attempt-001/rollout/MAPS_READY.json'
    if s.sha(map_ready) != 'e9774cabd25640a747436f4f8e1174c3a72ca536693e5e242b3ef926d8f98632':
        raise ValueError('accepted completed acquisition seal changed')
    for path, pin in provenance['map_files_sha256'].items():
        if s.sha(path) != pin:
            raise ValueError('completed acquisition changed: ' + path)
    maps = {}
    for context in public:
        cid = context['id']
        acquired = provenance['maps'][cid]
        directory = s.MAP_SOURCE / 'outputs/attempt-001/rollout/acquisitions' / cid
        if acquired != s.read(directory / 'MAP.json') or acquired['status'] != 'available':
            raise ValueError('completed map correspondence')
        labels = acquired['labels']
        if set(labels) != {r['id'] for r in context['records']}:
            raise ValueError('acquired map domain differs')
        if any(v not in s.source().LABELS.values() for v in labels.values()):
            raise ValueError('acquired map vocabulary differs')
        if acquired['actual_child_requests'] != 1 or acquired['authored_root_requests'] != 2:
            raise ValueError('not exactly one actual child acquisition')
        # Exact serialization used by the previous native task; errors remain untouched.
        payload = json.dumps(labels, sort_keys=True).encode()
        roles = [s.read(f) for f in (directory / 'role-audit').glob('*-result.json')]
        child = [r for r in roles if r['depth'] == 1]
        wrappers = [r for r in roles if r['depth'] == 0]
        if len(child) != 1 or len(wrappers) != 2 or child[0]['model_sha256'] != s.source().CHILD_SHA:
            raise ValueError('actual fixed child acquisition provenance')
        maps[cid] = dict(labels=labels, file_text=payload.decode(), file_sha256=hashlib.sha256(payload).hexdigest(),
                         actual_child_usage=metrics.usage(child), map_source_path=str(directory / 'MAP.json'),
                         authored_wrapper=dict(requests=2, synthetic_not_policy=True, paid_model_requests=0,
                             token_ids={key:sum(len(r['native_response']['tokens'][key]) for r in wrappers)
                                        for key in ('prompt_ids','completion_ids')},
                             usage=metrics.usage(wrappers)),
                         acquisition_elapsed_seconds=acquired['ended_epoch']-acquired['started_epoch'])
    old_plan=s.read(s.MAP_SOURCE/'inputs/PLAN.json')
    old_prompts={r['id']:r['prompt'] for r in s.read(s.MAP_SOURCE/'inputs/PROMPTS.json')}
    new_plan=s.read(s.ANCHOR/'inputs/PLAN.json')
    new_prompts={r['id']:r['prompt'] for r in s.read(s.ANCHOR/'inputs/PROMPTS.json')}
    old={(r['context_id'],r['family']):old_prompts[r['id']] for r in old_plan if r['map_source']=='native_c32' and not r['reducer']}
    new={(r['context_id'],r['family']):new_prompts[r['id']] for r in new_plan if r['example'] and not r['inline']}
    if old.keys()!=new.keys() or len(old)!=8:raise ValueError('anchor blocks differ')
    for key in old:
        if protocol.prompt(old[key],dict(schema=False,map_contract=False))!=old[key]:raise ValueError('old anchor differs')
        if protocol.prompt(old[key],dict(schema=True,map_contract=True))!=new[key]:raise ValueError('new anchor differs')
    rows = protocol.plan_for(public)
    st = s.stack()
    template = s.read(s.SOURCE / 'prepared/NATIVE_TEMPLATE.json')
    renderer = st.native.renderer()
    tools = json.loads(template['tools_ordered_json'])
    prompts = []
    for row in rows:
        context = next(c for c in public if c['id'] == row['context_id'])
        prompt = protocol.prompt(old[(context['id'],row['family'])], row)
        ids = renderer.render([template['system'], {'role': 'user', 'content': prompt}],
                              tools=tools, add_generation_prompt=True).token_ids
        if len(ids) + 2048 > 8192:
            raise ValueError('prompt exceeds native budget')
        native = s.task(context, prompt, host[context['id']]['answers'][row['family']], row, maps[context['id']]['file_text'].encode())
        if native.data.context_window_id != row['context_window_id'] or native.data.dataset != s.ROOT.name:
            raise ValueError('new context metadata')
        prompts.append(dict(id=row['id'], prompt=prompt, token_ids=ids, task_hash=native.hash))
    values = {'PUBLIC.json': public, 'HOST_GOLD.json': host, 'PLAN.json': rows,
              'PROMPTS.json': prompts, 'BINDING.json': s.binding(), 'NATIVE_TEMPLATE.json': template, 'MAPS.json': maps,
              'PROMPT_ANCHORS.json': [dict(context_id=k[0],family=k[1],old=old[k],new=new[k]) for k in old],
              'MAP_PROVENANCE.json': dict(source=str(map_ready), source_sha256=s.sha(map_ready),
                    source_files_sha256=provenance['map_files_sha256'], newly_paid_acquisitions=0)}
    for name, value in values.items():
        s.write(s.ROOT / 'inputs' / name, value)
    s.write(s.ROOT / 'PREPARED.json', dict(master_seed=protocol.MASTER,
            seed_collision_scan='rg981347[0-9]{3} before source creation returned1/no matches in sidecars+ideas excluding outputs and qualification',
            contexts=4, endpoints=96, native_map_acquisitions=0, reused_acquisitions=4, paired_blocks=8, paired_repeats=3, paired_seed_units=24,
            data_ready_sha256=s.sha(s.SOURCE / 'DATA_READY.json'),
            max_prompt_tokens=max(len(p['token_ids']) for p in prompts), gpu_calls=0))


def seal():
    previous = s.read(s.ANCHOR / 'READY.json')
    if s.sha(s.ANCHOR / 'READY.json') != '0a2e2d742e5516044a016c4e59ee964be461edd272f099223777a229fda4870f':
        raise ValueError('accepted visibility science READY changed')
    sources = dict(previous['source_sha256'])
    inputs = dict(previous['input_sha256'])
    runtime = s.ROOT.parent / 'runtime-an27-5780-v1'
    lifecycle = s.read(runtime / 'LIFECYCLE_READY_V2.json')
    sources.update(lifecycle['source_sha256'])
    provenance = s.read(s.ROOT / 'inputs/MAP_PROVENANCE.json')
    inputs.update(provenance['source_files_sha256'])
    inputs[provenance['source']] = provenance['source_sha256']
    mapping = s.read(s.ROOT / 'SOURCE_PATH_MAP.json')
    if s.sha(mapping['runtime_target']) != mapping['sha256']:
        raise ValueError('accepted runtime target changed')
    sources[mapping['runtime_target']] = mapping['sha256']
    for path, pin in {**sources, **inputs}.items():
        if s.sha(path) != pin:
            raise ValueError('inherited closure drift: ' + path)
    for path in [*s.ROOT.glob('*.py'), *s.ROOT.glob('*.md')]:
        sources[str(path)] = s.sha(path)
    for path in [s.ANCHOR / 'READY.json', s.ANCHOR / 'OWNER_READY.json', s.SOURCE / 'DATA_READY.json',
                 runtime / 'CPU_READY.json', runtime / 'LIFECYCLE_READY_V2.json',
                 runtime / 'credential_preflight.py',
                 s.ROOT / 'SOURCE_PATH_MAP.json',
                 s.ROOT / 'PREPARED.json', s.ROOT / 'CPU_TESTS.json', s.ROOT / 'CPU_FAILURE.json', *list((s.ROOT / 'inputs').glob('*.json'))]:
        inputs[str(path)] = s.sha(path)
    ready = dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE', source_sha256=sources,
                 input_sha256=inputs, prepared_epoch=time.time(), gpu_calls=0,
                 root_sha256=s.binding()['models'][s.binding()['role_map']['root']]['adapter_sha256'],
                 child_sha256=s.source().CHILD_SHA, endpoints=96, acquisitions=0, reused_acquisitions=4,
                 outer_seconds=1800, work_seconds=1650, cleanup_seconds=120,
                 collector_argv=[str(s.NATIVE), str(s.ROOT / 'collect.py'), '--binding', str(s.ROOT / 'inputs/BINDING.json'),
                                 '--endpoint', 'MAIN_OWNED_ENDPOINT_JSON', '--output', str(s.ROOT / 'outputs/attempt-001/rollout'),
                                 '--deadline', 'MAIN_SHARED_ABSOLUTE_EPOCH'],
                 launch_authority='MAIN only; collector does not start or stop model services',
                 runtime_binding='runtime-an27-5780-v1 pinned study_wrapper.adapt_stack only; service driver remains MAIN-owned',
                 reduction_metric='manual code/native observation audit required; automatic scalar agreement is separate',
                 qualification='focused CPU tests and exact native rendering; no new native runtime execution')
    ready['identity'] = protocol.digest(ready)
    s.write(s.ROOT / 'READY.json', ready)
    print(json.dumps(dict(ready_sha256=s.sha(s.ROOT / 'READY.json'), identity=ready['identity'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('inputs', 'seal', 'verify'))
    args = parser.parse_args()
    if args.command == 'inputs':
        prepare()
    elif args.command == 'seal':
        seal()
    else:
        print(s.verify()['identity'])
