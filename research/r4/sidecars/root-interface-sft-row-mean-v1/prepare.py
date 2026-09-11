"""CPU-only fixed input crosswalk, coefficient audit and final source seal."""
import argparse
import json
import os
import random
import subprocess
import time
from collections import Counter

import study as s


def inputs():
    recipe = s.read(s.PRIOR / 'RECIPE.json')
    prepared = s.PRIOR / 'prepared-v2'
    for name in ('PUBLIC.json', 'HOST_GOLD.json', 'TRAINING_ROWS_FINAL.json', 'EVAL_PLAN_FINAL.json', 'EVAL_PROMPTS.json', 'NATIVE_TEMPLATE.json'):
        s.check(prepared / name, recipe['input_sha256'][str(prepared / name)])
    for path, expected in s.PINS.items():
        s.check(path, expected)
    rows = s.read(prepared / 'TRAINING_ROWS_FINAL.json')
    if len(rows) != 32 or Counter(row['kind'] for row in rows) != {'helper': 16, 'terminal': 16}:
        raise ValueError('exact32 unchanged rows required')
    ledger = s.read(s.ROOT / 'WEIGHTING_AND_SEED_AUDIT.json')
    batches = []
    for epoch in range(2):
        order = list(range(32))
        random.Random(981284002 + epoch).shuffle(order)
        for offset in (0, 16):
            batch = [rows[i] for i in order[offset:offset + 16]]
            expected = ledger['batches'][len(batches)]
            if [row['id'] for row in batch] != [row['id'] for row in expected['rows']]:
                raise ValueError('fixed effective-batch order changed')
            for row, weight in zip(batch, expected['rows']):
                if sum(t != -100 for t in row['labels'][1:]) != weight['target_tokens']:
                    raise ValueError('actual shifted target count changed')
            batches.append(expected)
    original = s.read(prepared / 'EVAL_PLAN_FINAL.json')
    plan = s.build_plan(original)
    old_prompts = {p['id']: p for p in s.read(prepared / 'EVAL_PROMPTS.json')}
    public = {c['id']: c for c in s.read(prepared / 'PUBLIC.json')}
    host = s.read(prepared / 'HOST_GOLD.json')
    st = s.stack()
    renderer = st.native.renderer()
    template = s.read(prepared / 'NATIVE_TEMPLATE.json')
    tools = json.loads(template['tools_ordered_json'])
    prompts = []
    for row in plan:
        old = old_prompts[row['source_coordinate_id']]
        context = public[row['context_id']]
        text = st.prior.prompt(context, row['family'])
        ids = renderer.render([template['system'], {'role': 'user', 'content': text}], tools=tools, add_generation_prompt=True).token_ids
        if text != old['prompt'] or ids != old['token_ids'] or len(ids) + 2048 > 8192:
            raise ValueError('exact native prompt changed or cannot fit; no crop')
        task = st.native.task(context, text, host[context['id']]['answers'][row['family']], row['id'])
        prompts.append({**old, 'id': row['id'], 'source_coordinate_id': row['source_coordinate_id'], 'task_hash': task.hash})
    if ledger['phase_order'] != list(s.PHASES) or any(v['collisions'] for v in ledger['seed_checks']):
        raise ValueError('approved seed/order audit changed')
    return {'PLAN.json': plan, 'PROMPTS.json': prompts,
            'ARM_PLAN.json': [{'arm': arm, 'coordinate': row} for arm in s.PHASES for row in plan],
            'AUDIT.json': {'unchanged_native_prompt_matches': len(prompts), 'training_rows': len(rows),
                          'training_target_exposures': sum(v['target_tokens'] for v in batches),
                          'batches': batches, 'gpu_calls': 0, 'no_new_model_probe': True,
                          'source_training_rows_sha256': s.sha(prepared / 'TRAINING_ROWS_FINAL.json'),
                          'seed_audit_sha256': s.sha(s.ROOT / 'WEIGHTING_AND_SEED_AUDIT.json')}}


def prepare():
    bundle = inputs()
    for name, value in bundle.items():
        s.write(s.ROOT / 'prepared' / name, value)
    selected = s.checkpoint(s.CONTROL, s.PRIOR_IDENTITY, s.CONTROL_SHA)
    original = s.read(s.PRIOR / 'RECIPE.json')
    control_files = {str(s.CONTROL / name): s.sha(s.CONTROL / name) for name in ('RESULT.json', 'SELECTION.json')}
    checkpoint = s.CONTROL / 'checkpoint-0004'
    control_files[str(checkpoint / 'state.json')] = selected['state_sha256']
    control_files.update({str(checkpoint / name): h for name, h in s.read(checkpoint / 'state.json')['files_sha256'].items()})
    bound = {**original['input_sha256'], **control_files,
             **{str(s.prior().START / name): h for name, h in original['starting_files_sha256'].items()}}
    s.write(s.ROOT / 'INPUTS.json', {'input_sha256': bound, 'control_selected': selected,
                                   'starting_adapter': str(s.prior().START), 'starting_sha256': s.prior().START_SHA})
    s.write(s.ROOT / 'RECIPE.json', {'schema': s.ROOT.name, 'original_recipe_sha256': s.sha(s.PRIOR / 'RECIPE.json'),
        'loss': 'mean_rows(mean_current_action_tokens(CE))', 'original_loss': 'sum_current_action_CE/sum_current_action_tokens',
        'training_seed': 981284002, 'epochs': 2, 'effective_batch': 16, 'microbatch': 1, 'updates': 4,
        'lr': 1e-4, 'weight_decay': 0, 'clip': 1, 'base_dtype': 'bfloat16', 'adapter_dtype': 'float32',
        'fresh_optimizer': True, 'selection': 'fixed final4', 'phase_order': list(s.PHASES),
        'work_seconds': 3180, 'inclusive_seconds': 3300, 'outer_seconds': 3330,
        'training_seconds': 600, 'trainer_process_seconds': 900, 'collection_seconds_each': 900,
        'source_training_rows_sha256': bundle['AUDIT.json']['source_training_rows_sha256'],
        'readout_episodes': 48, 'new_sampling_seed_master': 981300001, 'all_other_scientific_contracts': 'unchanged approved DESIGN'})
    s.write(s.ROOT / 'PREPARED.json', {'status': 'CPU_INPUTS_FROZEN', 'gpu_calls': 0,
        'input_sha256': {str(p): s.sha(p) for p in (s.ROOT / 'prepared').glob('*.json')}})
    print({'prepared_tasks': 24, 'paired_episodes': 48, 'gpu_calls': 0})


def seal():
    tests = []
    for name, python, files in [('native', s.NATIVE, ['test_readout.py', 'test_launch_prepare.py']),
                                ('training', s.TRAIN, ['test_loss.py'])]:
        argv = [str(python), '-m', 'pytest', '-q', *[str(s.ROOT / 'tests' / f) for f in files]]
        result = subprocess.run(argv, cwd=s.ROOT, env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1', 'OMP_NUM_THREADS': '1'},
                                capture_output=True, text=True, timeout=90)
        tests.append({'name': name, 'argv': argv, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            print(result.stdout, result.stderr)
            raise ValueError('focused CPU qualification failed; no READY')
    s.write(s.ROOT / 'CPU_TESTS.json', {'status': 'PASS', 'results': tests, 'gpu_calls': 0,
        'qualification': 'Tiny CPU only; no actual model/behavior likelihood claim',
        'red_evidence': 'All new wrappers first failed absent; changed-prefix fixture failed before guard; tool history preserved.'})
    source = dict((str(p), h) for p, h in s.PINS.items())
    for path in (s.PRIOR / 'READY.json', s.LOCAL / 'READY.json'):
        source.update(s.read(path)['source_sha256'])
    source.update({str(p): s.sha(p) for p in list(s.ROOT.glob('*.py')) + list(s.ROOT.glob('*.md')) + list((s.ROOT / 'tests').glob('*.py'))})
    source[str(s.ROOT / 'CPU_TESTS.json')] = s.sha(s.ROOT / 'CPU_TESTS.json')
    bound = s.read(s.ROOT / 'INPUTS.json')['input_sha256']
    bound.update(s.read(s.ROOT / 'PREPARED.json')['input_sha256'])
    bound.update({str(s.ROOT / name): s.sha(s.ROOT / name) for name in ('INPUTS.json', 'RECIPE.json', 'PREPARED.json')})
    for path, expected in {**source, **bound}.items():
        s.check(path, expected)
    ready = {'status': 'CPU_READY_FOR_MAIN_ACCEPTANCE', 'source_sha256': source, 'input_sha256': bound,
             'prepared_epoch': time.time(), 'gpu_calls': 0, 'launch_authorized_by_preparation': False,
             'argv': [str(s.NATIVE), str(s.ROOT / 'launch.py'), 'run', '--output', str(s.ROOT / 'outputs/attempt-001')],
             'verify_argv': [str(s.NATIVE), str(s.ROOT / 'launch.py'), 'verify'],
             'parent_outer_seconds': 3330, 'owned_inclusive_seconds': 3300, 'phases': list(s.PHASES)}
    ready['identity'] = s.digest(ready)
    s.write(s.ROOT / 'READY.json', ready)
    s.verify()
    print({'ready_sha256': s.sha(s.ROOT / 'READY.json'), 'identity': ready['identity'], 'gpu_calls': 0})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('inputs', 'seal'))
    (prepare if parser.parse_args().command == 'inputs' else seal)()
