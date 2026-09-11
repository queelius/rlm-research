"""CPU-only fixed inputs, narrow qualification and final prepared-source publication."""
import argparse
import json
import os
import subprocess
import time
from collections import Counter

import native as n
import study as s


def build_inputs():
    public, gold = s.data()
    contexts = {row['id']: row for row in public}
    plans = s.build_plans(public)
    st = n.stack()
    renderer = st.native.renderer()
    template = s.read(s.PRIOR / 'prepared-v2/NATIVE_TEMPLATE.json')
    tools = json.loads(template['tools_ordered_json'])
    tasks, skew = {}, []
    all_rows = [r for group in plans['training'].values() for r in group] + plans['validation'] + plans['transfer']
    for row in all_rows:
        if row['task_name'] in tasks:
            continue
        context = contexts[row['context_id']]
        prompt = st.prior.prompt(context, row['family'])
        answer = gold[context['id']]['answers'][row['family']]
        task = st.native.task(context, prompt, answer, row['task_name'])
        ids = renderer.render([template['system'], {'role': 'user', 'content': prompt}], tools=tools, add_generation_prompt=True).token_ids
        if len(ids) + 2048 > 8192:
            raise ValueError('frozen initial root prompt/output does not fit; no crop')
        tasks[row['task_name']] = {'context_id': context['id'], 'family': row['family'], 'prompt': prompt,
                                  'task_hash': task.hash, 'context_sha256': __import__('hashlib').sha256(context['text'].encode()).hexdigest(),
                                  'first_prompt_token_ids': ids, 'first_prompt_token_ids_sha256': s.digest(ids)}
        if row['split'] == 'training':
            skew.append({'task': row['task_name'], 'family': row['family'], 'records': len(context['records']),
                         'target': context['target'], 'answer': answer})
    gids = [g for context in public for g in context['group_ids']]
    if len(gids) != 896 or len(set(gids)) != 896:
        raise ValueError('duplicate/changed normalized source allocation')
    frozen_eval = s.read(s.PRIOR / 'prepared-v2/EVAL_PROMPTS.json')
    by_prompt = {t['prompt']: t['first_prompt_token_ids'] for t in tasks.values()}
    if any(by_prompt.get(row['prompt']) != row['token_ids'] for row in frozen_eval):
        raise ValueError('original SFT native root prefix changed')
    hist = Counter(row['answer'] for row in skew)
    return {'PLANS.json': plans, 'TASKS.json': tasks,
            'DATA_AUDIT.json': {'unique_groups': len(set(gids)), 'groups_by_stratum': dict(Counter(c['stratum'] for c in public for _ in c['group_ids'])),
                               'cross_stratum_overlap': 0, 'sft_frozen_eval_prompt_matches': len(frozen_eval),
                               'public_sha256': s.sha(s.PRIOR / 'prepared-v2/PUBLIC.json'),
                               'host_gold_sha256': s.sha(s.PRIOR / 'prepared-v2/HOST_GOLD.json'),
                               'source_provenance': s.read(s.PRIOR / 'prepared-v2/PROVENANCE.json'),
                               'exposure': 'same SFT896 allocation; leaf-train-supported/root-history-excluded composition; not source-test novelty'},
            'GOLD_SKEW.json': {'training_prompts': skew, 'answer_histogram': dict(hist),
                               'best_constant_correct_of16': max(hist.values()),
                               'selection_used_labels': False, 'zero_answers_retained': True}}


def seed_audit(plans):
    rows = [r for values in plans['training'].values() for r in values] + plans['validation'] + plans['transfer']
    seeds = {r['seed'] for r in rows} | {s.SEED}
    if len(seeds) != 153:
        raise ValueError('fresh seeds overlap locally')
    source = s.SIDE / 'leaf-sparse-anchor-v1/SEED_AUDIT.json'
    previous = s.read(source)['source_sha256']
    previous.update({str(s.PRIOR / 'RECIPE.json'): s.PINS[s.PRIOR / 'RECIPE.json'],
                     str(s.PRIOR / 'prepared-v2/EVAL_PLAN_FINAL.json'): '48f6831969f447ef3b0f184a2eda8950c758a6383d766c4cee1ca862a98f8cfa',
                     str(s.SIDE / 'leaf-sparse-anchor-v1/SPEC.json'): '1627f461a52811e68dfab15bd5a0ec1f173ef71accee493b50bc5fcb31c173c3'})
    audit = []
    # Literal namespace screen in named immutable metadata, including seed arrays;
    # not a global search, and it never enters output/trace files.
    import re
    pattern = re.compile(r'\b(?:' + '|'.join(map(str, sorted(seeds))) + r')\b')
    for path, expected in previous.items():
        s.check(path, expected)
        matches = sorted(set(pattern.findall(__import__('pathlib').Path(path).read_text())))
        if matches:
            raise ValueError('fresh namespace collision in named metadata: ' + path)
        audit.append({'path': path, 'sha256': expected, 'collisions': []})
    return {'seed_master': s.SEED, 'unique_seeds_including_master': sorted(seeds),
            'scope': 'Named prior sparse screen metadata plus SFT recipe/plan and sparse SPEC; not global',
            'source_manifest_sha256': s.sha(source), 'sources': audit, 'paired_readout_seed_reuse': 'Only within steps0/4/8 validation and0/8 transfer'}


def inputs():
    bundle = build_inputs()
    bundle['SEED_AUDIT.json'] = seed_audit(bundle['PLANS.json'])
    for name, value in bundle.items():
        s.write(s.ROOT / 'inputs' / name, value)
    recipe = s.read(s.CAMPAIGN / 'RECIPE.json')
    recipe.update(schema=s.ROOT.name, training_seed=s.SEED, root_adapter='MAIN_START_BINDING_REQUIRED', root_adapter_sha256=None,
                  max_concurrent_pairs=4, concurrency_amendment='Four slots, same accepted SFT typed local runtime',
                  caps={'global': 7080, 'inclusive': 7200, 'outer': 7230, 'collection': 1200, 'readout': 900, 'service_ready': 180, 'training': 600},
                  optimizer_steps=8, selection='fixed final8, never validation maximum',
                  admission='Completed observable native-graph-admissible correct1, wrong/empty/malformed0; infrastructure/null excluded; mixed within-task only; no rerolls',
                  start='Exact separately MAIN-frozen SFTfinal4 or historical473210; new campaign0, fresh Adam and RNG',
                  limitations='Adaptive exposed leaf-training-supported composition;16training prompts; conditional capped correction, not exact trajectory correction; nulls and costs retained')
    s.write(s.ROOT / 'RECIPE.json', recipe)
    print({'tasks': len(bundle['TASKS.json']), 'episodes': 184, 'gpu_calls': 0})


def seal():
    tests = []
    for name, python, files in [('native', s.NATIVE, ['test_contract.py', 'test_export.py', 'test_collection.py', 'test_coordinator.py', 'test_inputs.py', 'test_binding.py']),
                                ('training', s.TRAIN, ['test_training.py'])]:
        argv = [str(python), '-m', 'pytest', '-q', *[str(s.ROOT / 'tests' / filename) for filename in files]]
        result = subprocess.run(argv, cwd=s.ROOT, env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1', 'OMP_NUM_THREADS': '1'},
                                capture_output=True, text=True, timeout=90)
        tests.append({'name': name, 'argv': argv, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            print(result.stdout, result.stderr)
            raise ValueError('focused CPU tests failed before source freeze')
    s.write(s.ROOT / 'CPU_TESTS.json', {'status': 'PASS', 'results': tests, 'gpu_calls': 0,
                                      'red_evidence': 'Focused files failed against missing new implementation before coding; terminal tool history retained. Tiny fixtures are qualification-only.'})
    sources = {}
    for path in (s.PRIOR / 'READY.json', s.LOCAL / 'READY.json'):
        s.check(path, s.PINS[path])
        for filename, expected in s.read(path)['source_sha256'].items():
            if filename in sources and sources[filename] != expected:
                raise ValueError('inconsistent inherited source closure')
            sources[filename] = expected
    sources.update({str(path): expected for path, expected in s.PINS.items()})
    paths = list(s.ROOT.glob('*.py')) + list(s.ROOT.glob('*.md')) + list((s.ROOT / 'tests').glob('*.py'))
    paths += [s.ROOT / 'RECIPE.json', s.ROOT / 'CPU_TESTS.json', s.CAMPAIGN / 'test_training.py']
    sources.update({str(path): s.sha(path) for path in paths})
    input_hashes = {str(path): s.sha(path) for path in (s.ROOT / 'inputs').glob('*.json')}
    manifest = {'schema': s.ROOT.name, 'seed_master': s.SEED, 'source_sha256': sources, 'input_sha256': input_hashes,
                'planned_episodes': 184, 'optimizer_steps': 8, 'starting_weight_selected': False,
                'runtime': 'accepted local77df23b8, image8cfe, four slots', 'main_approval_scope': 'CPU preparation; launch/start decision retained by MAIN'}
    manifest['campaign_id'] = s.digest(manifest)
    for path, expected in {**sources, **input_hashes}.items():
        s.check(path, expected)
    s.write(s.ROOT / 'CAMPAIGN.json', manifest)
    s.verify_prepared()
    ready = {'status': 'CPU_PREPARED_WAITING_MAIN_START_BINDING', 'campaign_id': manifest['campaign_id'],
             'campaign_sha256': s.sha(s.ROOT / 'CAMPAIGN.json'), 'source_paths': len(sources),
             'input_paths': len(input_hashes), 'cpu_tests_sha256': s.sha(s.ROOT / 'CPU_TESTS.json'),
             'verify_argv': [str(s.NATIVE), str(s.ROOT / 'coordinator.py'), 'verify'],
             'launch_argv_template': [str(s.NATIVE), str(s.ROOT / 'coordinator.py'), 'run', '--start-binding', 'MAIN_FROZEN_START.json', '--output', str(s.ROOT / 'outputs/attempt-001')],
             'caps': {'work': 7080, 'inclusive': 7200, 'outer': 7230}, 'gpu_calls_in_preparation': 0,
             'prepared_epoch': time.time(), 'launch_authorized': False}
    s.write(s.ROOT / 'PREPARED.json', ready)
    print({'prepared_sha256': s.sha(s.ROOT / 'PREPARED.json'), 'campaign_sha256': ready['campaign_sha256'], 'status': ready['status']})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('inputs', 'seal'))
    (inputs if parser.parse_args().command == 'inputs' else seal)()
