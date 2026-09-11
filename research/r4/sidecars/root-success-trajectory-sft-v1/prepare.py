"""CPU-only exact native teacher export, fixed readout crosswalk and final seal."""
import argparse
import functools
import hashlib
import json
import os
import random
import subprocess
import time
import traceback
import uuid
from collections import Counter
from pathlib import Path
import study as s
import binding as b

PROOF = {}


@functools.lru_cache(maxsize=None)
def hash_once(path):
    value = s.sha(path)
    PROOF[str(path)] = value
    return value


@functools.lru_cache(maxsize=None)
def read_once(path):
    hash_once(Path(path))
    return s.read(path)


def authenticate(path, expected):
    if hash_once(Path(path)) != expected:
        raise ValueError('candidate proof/source changed: ' + str(path))


def export_teachers():
    authenticate(s.SCREEN / 'SEAL.json', 'bc2529d41a582cce062994853f1b79bd35b4df6527162425570f3f3fc3577770')
    seal = read_once(s.SCREEN / 'SEAL.json')
    for name, expected in seal['artifact_sha256'].items():
        authenticate(s.SCREEN / name, expected)
    source_hashes = {**read_once(s.SCREEN / 'SOURCES.json'), **read_once(s.SCREEN / 'STATIC_REVIEW_SOURCES.json')}
    candidates = read_once(s.SCREEN / 'CANDIDATES.json')
    selected = {r['coordinate']['id']: r for r in candidates['rows'] if r['confirmed_candidate']}
    if set(selected) != set(candidates['confirmed_coordinate_ids']) or len(selected) != 27:
        raise ValueError('exact candidate seal membership differs')
    campaign_path = s.ADAPTIVE / 'CAMPAIGN.json'
    authenticate(campaign_path, '51afee1b3753e5060955d205c1b923393f35af1550f23c4c536b12593c5fe4a1')
    campaign = read_once(campaign_path)
    for path, expected in {**campaign['source_sha256'], **campaign['input_sha256']}.items():
        authenticate(Path(path), expected)
    study_path = s.ADAPTIVE / 'study.py'
    adaptive = s.load('success_export_exact_adaptive_study', study_path, campaign['source_sha256'][str(study_path)])
    with s.aliases({'study': adaptive}):
        native = s.load('success_export_exact_native', s.ADAPTIVE / 'native.py', campaign['source_sha256'][str(s.ADAPTIVE / 'native.py')])
    # Private read/hash memoization only; the qualified native/typed checks run unchanged.
    adaptive.read, adaptive.sha = read_once, hash_once
    native.stack().exporter.read = read_once
    native.stack().exporter.file_hash = hash_once
    public = {c['id']: c for c in read_once(s.PRIOR / 'prepared-v2/PUBLIC.json')}
    plans = read_once(s.ADAPTIVE / 'inputs/PLANS.json')['training']
    corpus, provenance = [], []
    for number in range(1, 6):
        directory = s.ADAPTIVE / f'outputs/attempt-001/round-{number:02}'
        collection = directory / 'collection/rollout'
        exported = directory / 'collection/export'
        for path in (directory / 'COMMIT.json', directory / 'GENERATION.json', collection / 'STATUS.json', collection / 'SPEC.json', exported / 'MANIFEST.json'):
            authenticate(path, source_hashes[str(path)])
        spec = read_once(collection / 'SPEC.json')
        manifest = read_once(exported / 'MANIFEST.json')
        if spec['plan'] != plans[str(number)] or not read_once(collection / 'STATUS.json')['stop_reason'] is None:
            raise ValueError('not the frozen completed training round')
        for name, expected in manifest['artifact_sha256'].items():
            authenticate(exported / name, expected)
        for old in read_once(exported / 'EPISODES.json'):
            identifier = old['episode_id']
            if identifier not in selected:
                continue
            candidate = selected[identifier]
            if candidate['round'] != number or public[old['coordinate']['context_id']]['stratum'] != 'train':
                raise ValueError('candidate source round/split differs')
            record_path = collection / 'rows' / (identifier + '.json')
            authenticate(record_path, manifest['source_record_sha256'][identifier])
            record = read_once(record_path)
            raw_path = Path(candidate['raw_path'])
            authenticate(raw_path, candidate['raw_sha256'])
            if str(raw_path) != record['episode_path'] or candidate['raw_sha256'] != record['episode_sha256']:
                raise ValueError('candidate raw path differs')
            raw = read_once(raw_path)
            roots, evidence = native.exact_turns(raw, collection, spec['binding'])
            if roots != old['turns'] or evidence != old['all_role_evidence']:
                raise ValueError('native physical reconstruction differs from frozen export')
            for turn in evidence:
                for path_key, hash_key, obj in [('source_audit_path', 'source_audit_sha256', turn['role_audit']),
                                                 ('typed_audit_path', 'typed_audit_sha256', turn)]:
                    p = Path(obj[path_key])
                    authenticate(p, obj[hash_key])
                    authenticate(p, source_hashes[str(p)])
                if turn['sampling']['seed'] != candidate['coordinate']['seed']:
                    raise ValueError('teacher physical sampling identity changed')
            corpus.append(s.teacher_episode(old, candidate))
            provenance.append(dict(episode_id=identifier, raw_path=str(raw_path), raw_sha256=candidate['raw_sha256'],
                generation_id=old['generation_id'], original_teacher_root_sha256=roots[0]['role_audit']['model_sha256'],
                native_root_turns=len(roots), child_turns=len(evidence) - len(roots), physical_reconstruction_equal=True))
    corpus.sort(key=lambda e: e['episode_id'])
    if (len(corpus), sum(len(e['turns']) for e in corpus), sum(s.validate_turn(t) for e in corpus for t in e['turns'])) != (27, 114, 15256):
        raise ValueError('confirmed corpus totals differ')
    if len({s.digest([t['input_ids'][t['prompt_length']:] for t in e['turns']]) for e in corpus}) != 27:
        raise ValueError('whole action sequence duplicate; approved no-dedup premise differs')
    return corpus, provenance, public


def prepare():
    started = time.time()
    corpus, proof, public = export_teachers()
    plan = s.build_plan(s.read(s.PRIOR / 'prepared-v2/EVAL_PLAN_FINAL.json'))
    frozen = {p['id']: p for p in s.read(s.PRIOR / 'prepared-v2/EVAL_PROMPTS.json')}
    st = s.stack()
    renderer = st.native.renderer()
    template = s.read(s.PRIOR / 'prepared-v2/NATIVE_TEMPLATE.json')
    tools = json.loads(template['tools_ordered_json'])
    host = s.read(s.PRIOR / 'prepared-v2/HOST_GOLD.json')
    prompts = []
    for coordinate in plan:
        old = frozen[coordinate['source_coordinate_id']]
        context = public[coordinate['context_id']]
        text = st.prior.prompt(context, coordinate['family'])
        token_ids = renderer.render([template['system'], {'role': 'user', 'content': text}], tools=tools, add_generation_prompt=True).token_ids
        if text != old['prompt'] or token_ids != old['token_ids']:
            raise ValueError('actual complete native prompt differs')
        task = st.native.task(context, text, host[context['id']]['answers'][coordinate['family']], coordinate['id'])
        prompts.append({**old, 'id': coordinate['id'], 'source_coordinate_id': coordinate['source_coordinate_id'], 'task_hash': task.hash})
    s.validate_prompts(plan, prompts)
    train_groups = {g for e in corpus for g in public[e['coordinate']['context_id']]['group_ids']}
    readout_groups = {g for r in plan for g in public[r['context_id']]['group_ids']}
    if train_groups & readout_groups:
        raise ValueError('source-group train/readout overlap')
    command = ['rg', '-l', '--glob', '*.json', '--glob', '*.py', '--glob', '*.md', '--glob', '!**/outputs/**',
        '--glob', '!**/service*/**', '--glob', '!**/qualification*/**', '--glob', '!**/prepared*/**',
        '--glob', '!root-success-trajectory-sft-v1/**', '981308[0-9]{3}',
        str(s.SIDE), str(s.SIDE.parent / 'ideas'), str(s.SIDE.parent / 'operations/2026-09-09-proceed')]
    scan = subprocess.run(command, text=True, capture_output=True, timeout=30)
    hits = [p for p in scan.stdout.splitlines() if not p.startswith(str(s.ROOT) + '/')]
    if scan.returncode not in (0, 1) or hits:
        raise ValueError('bounded seed namespace collision: ' + repr(hits))
    phases = sorted(['baseline', 'success_sft', 'rl7'], key=lambda arm: hashlib.sha256(('981308001:' + arm).encode()).hexdigest())
    control, rl7 = s.control_selected(), b.rl7_selected()
    rlstate = s.read(Path(rl7['checkpoint']) / 'state.json')
    external = {str(p): s.sha(p) for p in b.RL_PINS}
    for chosen, parent in [(control, s.CONTROL), (rl7, b.RL_ROUND / 'training')]:
        cp = Path(chosen['checkpoint'])
        external[str(cp / 'state.json')] = s.sha(cp / 'state.json')
        external.update({str(cp / name): h for name, h in s.read(cp / 'state.json')['files_sha256'].items()})
        for name in ('RESULT.json',):
            external[str(parent / name)] = s.sha(parent / name)
    external[str(s.CONTROL / 'SELECTION.json')] = s.sha(s.CONTROL / 'SELECTION.json')
    for name, expected in [('INPUTS.json', rlstate['input_file_sha256']), ('correction-capture.json', rlstate['correction_capture_sha256'])]:
        external[str(b.RL_ROUND / 'training' / name)] = expected
    rlinput = rlstate['input_identity']['input_binding']
    external[rlinput['group_path']] = rlinput['group_sha256']
    external[str(Path(rlinput['group_path']).parent / 'MANIFEST.json')] = rlinput['export_manifest_sha256']
    recipe = dict(schema=s.ROOT.name, training_seed=s.TRAIN_SEED, master_seed=981308001, updates=8,
        loss='mean_episode(mean_root_turn(mean_physical_action_CE))', learning_rate=2e-5, weight_decay=0.,
        betas=[.9, .999], eps=1e-8, clip=1., base_dtype='bfloat16', adapter_dtype='float32', rank=8,
        starting_adapter_sha256=s.CONTROL_SHA, fresh_adam=True, phase_order=phases, fixed_child_sha256=s.CHILD_SHA,
        selection='fixed success-SFT final8; RL7 exact last-saved after original STOP, not final8',
        episode_exposures=216, root_turn_exposures=912, target_token_exposures=122048,
        training_seconds=1200, work_seconds=4380, inclusive_seconds=4500, outer_seconds=4530, collection_seconds_each=900,
        paired_readout_episodes=72, no_deduplication=True, no_sampled_code_execution=True)
    turns = [t for e in corpus for t in e['turns']]
    orders = []
    for step in range(8):
        order = list(range(27))
        random.Random(s.TRAIN_SEED + step).shuffle(order)
        orders.append([corpus[i]['episode_id'] for i in order])
    audit = dict(episodes=27, root_turns=114, action_tokens=15256, physical_native_matches=114,
        max_sequence_tokens=max(len(t['input_ids']) for t in turns), max_prompt_tokens=max(t['prompt_length'] for t in turns),
        prompt_tokens=sum(t['prompt_length'] for t in turns), physical_stop_token_counts=dict(Counter(t['input_ids'][-1] for t in turns)),
        injected_stop_tokens=0, retokenized_tokens=0, native_readout_prompt_matches=24,
        source_group_overlap=0, candidate_source_groups=len(train_groups), readout_source_groups=len(readout_groups),
        episode_orders=orders, deduplicated_episodes=0, teacher_provenance=proof,
        weighting=[dict(episode_id=e['episode_id'], turn_id=t['id'], action_tokens=len(t['old_logprobs']),
                        nominal_coefficient=1 / (27 * len(e['turns']) * len(t['old_logprobs']))) for e in corpus for t in e['turns']],
        seed_scan=dict(argv=command, scope='named source/spec namespaces only; outputs/prepared/qualifications excluded',
                       collisions=hits, returncode=scan.returncode, phase_order=phases), gpu_calls=0,
        inherited_native_qualification='unchanged authenticated adaptive collector/native/typed source closure; all real114 roots reconstructed',
        elapsed_seconds=time.time() - started)
    for name, value in [('EPISODES.json', corpus), ('PLAN.json', plan), ('PROMPTS.json', prompts), ('AUDIT.json', audit)]:
        s.write(s.ROOT / 'prepared' / name, value)
    s.write(s.ROOT / 'RECIPE.json', recipe)
    s.write(s.ROOT / 'INPUTS.json', dict(input_sha256={**PROOF, **external}, control=control, rl7=rl7,
        native_proof='qualified exact_turns equals original complete27 exports; no likelihood fabrication'))
    s.write(s.ROOT / 'PREPARED.json', dict(status='CPU_INPUTS_FROZEN', gpu_calls=0,
        input_sha256={str(p): s.sha(p) for p in (s.ROOT / 'prepared').glob('*.json')}))
    print({'prepared': True, 'episodes': 27, 'root_turns': 114, 'targets': 15256, 'readout': 72, 'phase_order': phases}, flush=True)


def seal():
    tests = []
    for name, python, files in [('native', s.NATIVE, ['test_inputs.py', 'test_binding.py']), ('training', s.TRAIN, ['test_train.py'])]:
        argv = [str(python), '-m', 'pytest', '-q', *[str(s.ROOT / 'tests' / f) for f in files]]
        result = subprocess.run(argv, cwd=s.ROOT, env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1',
            'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'}, capture_output=True, text=True, timeout=90)
        tests.append(dict(name=name, argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        if result.returncode:
            s.write(s.ROOT / ('FAILED_TESTS-' + uuid.uuid4().hex + '.json'), tests)
            raise ValueError('focused CPU test failed; no READY')
    s.write(s.ROOT / 'CPU_TESTS.json', dict(status='PASS', results=tests, gpu_calls=0,
        red_evidence='8 new focused tests observed failing absent implementation; actual tiny CPU update/checkpoint/resume passes',
        warning='Tiny in-memory PEFT model has no on-disk base config; save warns vocabulary assumed unchanged. No real-model assertion.'))
    inherited = s.read(s.ROW / 'READY.json')
    source = {**inherited['source_sha256'], str(s.ROW / 'READY.json'): s.sha(s.ROW / 'READY.json')}
    source.update({str(p): s.sha(p) for p in list(s.ROOT.glob('*.py')) + list(s.ROOT.glob('*.md')) + list((s.ROOT / 'tests').glob('*.py'))})
    source[str(s.ROOT / 'CPU_TESTS.json')] = s.sha(s.ROOT / 'CPU_TESTS.json')
    bound = {**s.read(s.ROOT / 'INPUTS.json')['input_sha256'], **s.read(s.ROOT / 'PREPARED.json')['input_sha256']}
    bound.update({str(s.ROOT / p): s.sha(s.ROOT / p) for p in ('INPUTS.json', 'RECIPE.json', 'PREPARED.json')})
    for path, expected in {**source, **bound}.items():
        s.check(path, expected)
    ready = dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE', source_sha256=source, input_sha256=bound,
        prepared_epoch=time.time(), gpu_calls=0, launch_authorized_by_preparation=False,
        argv=[str(s.NATIVE), str(s.ROOT / 'launch.py'), 'run', '--output', str(s.ROOT / 'outputs/attempt-001')],
        verify_argv=[str(s.NATIVE), str(s.ROOT / 'launch.py'), 'verify'], parent_outer_seconds=4530,
        owned_inclusive_seconds=4500, phases=s.phase_order())
    ready['identity'] = s.digest(ready)
    s.write(s.ROOT / 'READY.json', ready)
    s.verify()
    print({'ready_sha256': s.sha(s.ROOT / 'READY.json'), 'identity': ready['identity'], 'gpu_calls': 0})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('inputs', 'seal'))
    try:
        (prepare if parser.parse_args().command == 'inputs' else seal)()
    except BaseException as error:
        s.write(s.ROOT / ('PREPARATION_FAILURE-' + uuid.uuid4().hex + '.json'), dict(type=type(error).__name__,
            message=str(error), traceback=traceback.format_exc(), source_sha256={str(p): s.sha(p) for p in s.ROOT.glob('*.py')}))
        raise
