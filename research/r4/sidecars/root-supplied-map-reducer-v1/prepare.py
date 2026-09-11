"""CPU preparation and immutable source closure; no runtime/model launch."""
import argparse
import json
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
    rows = protocol.plan_for(public)
    st = s.stack()
    template = s.read(s.SOURCE / 'prepared/NATIVE_TEMPLATE.json')
    renderer = st.native.renderer()
    tools = json.loads(template['tools_ordered_json'])
    prompts = []
    for row in rows:
        context = next(c for c in public if c['id'] == row['context_id'])
        prompt = protocol.prompt(st.prior.prompt(context, row['family']), row)
        ids = renderer.render([template['system'], {'role': 'user', 'content': prompt}],
                              tools=tools, add_generation_prompt=True).token_ids
        if len(ids) + 2048 > 8192:
            raise ValueError('prompt exceeds native budget')
        native = s.task(context, prompt, host[context['id']]['answers'][row['family']], row)
        if native.data.context_window_id != row['context_window_id'] or native.data.dataset != s.ROOT.name:
            raise ValueError('new context metadata')
        prompts.append(dict(id=row['id'], prompt=prompt, token_ids=ids, task_hash=native.hash))
    values = {'PUBLIC.json': public, 'HOST_GOLD.json': host, 'PLAN.json': rows,
              'PROMPTS.json': prompts, 'BINDING.json': s.binding(), 'NATIVE_TEMPLATE.json': template}
    for name, value in values.items():
        s.write(s.ROOT / 'inputs' / name, value)
    s.write(s.ROOT / 'PREPARED.json', dict(master_seed=protocol.MASTER,
            seed_collision_scan='rg981334[0-9]{3} before source creation returned1/no matches in sidecars+ideas excluding outputs and qualification',
            contexts=4, endpoints=32, native_map_acquisitions=4, paired_blocks=8,
            data_ready_sha256=s.sha(s.SOURCE / 'DATA_READY.json'),
            max_prompt_tokens=max(len(p['token_ids']) for p in prompts), gpu_calls=0))


def seal():
    previous = s.read(s.SOURCE / 'READY.json')
    inherited_rl4 = s.read(s.RL4 / 'READY.json')
    sources = {**previous['source_sha256'], **inherited_rl4['source_sha256']}
    runtime = s.ROOT.parent / 'runtime-an27-5780-v1'
    cpu = s.read(runtime / 'CPU_READY.json')
    lifecycle = s.read(runtime / 'LIFECYCLE_READY.json')
    sources.update(cpu['source_and_artifact_sha256'])
    sources.update(lifecycle['source_sha256'])
    inputs = dict(previous['input_sha256'])
    mapping = s.read(s.ROOT / 'SOURCE_PATH_MAP.json')
    if sources.pop(mapping['old']) != mapping['sha256'] or s.sha(mapping['source']) != mapping['sha256']:
        raise ValueError('exact archived supervisor correspondence changed')
    if s.sha(runtime / 'COPY_MANIFEST.json') != mapping['copy_manifest_sha256']:
        raise ValueError('accepted image-copy manifest changed')
    copied = s.read(runtime / 'COPY_MANIFEST.json')['entries']
    if not any(r['source'] == mapping['source'] and r['target'] == mapping['runtime_target']
               and r['sha256'] == mapping['sha256'] for r in copied):
        raise ValueError('supervisor absent from qualified image copy')
    sources[mapping['source']] = mapping['sha256']
    # Carry only byte-identical historical closure members; any disagreement is an error.
    for path, pin in {**sources, **inputs}.items():
        if s.sha(path) != pin:
            raise ValueError('inherited closure drift: ' + path)
    for path in [*s.ROOT.glob('*.py'), *s.ROOT.glob('*.md')]:
        sources[str(path)] = s.sha(path)
    for path in [s.SOURCE / 'READY.json', s.RL4 / 'READY.json', s.SOURCE / 'DATA_READY.json',
                 runtime / 'CPU_READY.json', runtime / 'LIFECYCLE_READY.json',
                 s.ROOT / 'SOURCE_PATH_MAP.json',
                 s.ROOT / 'PREPARED.json', s.ROOT / 'CPU_TESTS.json', *list((s.ROOT / 'inputs').glob('*.json'))]:
        inputs[str(path)] = s.sha(path)
    ready = dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE', source_sha256=sources,
                 input_sha256=inputs, prepared_epoch=time.time(), gpu_calls=0,
                 root_sha256=s.binding()['models'][s.binding()['role_map']['root']]['adapter_sha256'],
                 child_sha256=s.source().CHILD_SHA, endpoints=32, acquisitions=4,
                 outer_seconds=1350, work_seconds=1200, cleanup_seconds=120,
                 collector_argv=[str(s.NATIVE), str(s.ROOT / 'collect.py'), '--binding', str(s.ROOT / 'inputs/BINDING.json'),
                                 '--endpoint', 'MAIN_OWNED_ENDPOINT_JSON', '--output', str(s.ROOT / 'outputs/attempt-001'),
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
