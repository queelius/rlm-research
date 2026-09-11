"""Exact candidate, teacher-token and fixed-checkpoint identities."""
import copy
import functools
import hashlib
import importlib.util
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SCREEN = SIDE.parent / 'analyses/adaptive-success-trajectory-feasibility-2026-09-09'
ADAPTIVE = SIDE / 'root-adaptive-rlvr-v1'
ROW = SIDE / 'root-interface-sft-row-mean-v1'
_source = ROW / 'study.py'
if hashlib.sha256(_source.read_bytes()).hexdigest() != '94b88c11e6146c2563ceac6badd10fa6b9c623641e961381d3c2390f35a580dc':
    raise ValueError('qualified shared study source changed')
_spec = importlib.util.spec_from_file_location('success_shared_study', _source)
row = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(row)
read, sha, check, write, digest, load, aliases = row.read, row.sha, row.check, row.write, row.digest, row.load, row.aliases
PRIOR, LOCAL, CONTROL, NATIVE, TRAIN = row.PRIOR, row.LOCAL, row.CONTROL, row.NATIVE, row.TRAIN
CONTROL_SHA, CHILD_SHA, BASE_SHA = row.CONTROL_SHA, row.CHILD_SHA, row.BASE_SHA
START = CONTROL / 'checkpoint-0004'
TRAIN_SEED = 981308002


def validate_turn(turn):
    ids, labels, k = turn['input_ids'], turn['labels'], turn['prompt_length']
    count = len(ids) - k
    if (turn['role_depth'] != 0 or turn['credited'] is not True or turn['typed_wire_grammar'] is not False
            or not 0 < k < len(ids) <= 8192 or any(type(t) is not int or t < 0 for t in ids)
            or labels != [-100] * k + ids[k:] or turn['loss_mask'] != [0] * k + [1] * count
            or turn['usage_input_tokens'] != k or turn['usage_completion_tokens'] != count
            or len(turn['old_logprobs']) != count or any(not math.isfinite(x) for x in turn['old_logprobs'])):
        raise ValueError('not an exact physical root action suffix')
    return count


def teacher_episode(exported, candidate):
    coordinate = candidate['coordinate']
    if (candidate['confirmed_candidate'] is not True or candidate['aggregation'] != 'pass'
            or candidate['round'] not in range(1, 6) or coordinate['split'] != 'training'
            or coordinate['stratum'] != 'train' or exported['coordinate'] != coordinate
            or exported['episode_id'] != coordinate['id'] or not exported['trace_trainable']
            or exported['reward'] != 1 or exported['qualification_only']):
        raise ValueError('not a confirmed frozen training-only candidate')
    turns = copy.deepcopy(exported['turns'])
    if (len(turns) != candidate['root_calls'] or sum(validate_turn(t) for t in turns) != candidate['root_tokens']
            or len({t['source_node_index'] for t in turns}) != len(turns)):
        raise ValueError('candidate complete root-turn membership differs')
    for t in turns:
        t['id'] = coordinate['id'] + ':' + str(t['source_node_index'])
    return {'episode_id': coordinate['id'], 'coordinate': coordinate, 'round': candidate['round'], 'turns': turns}


def build_plan(original):
    first = {'validation': 981308101, 'query_transfer': 981308201, 'length_transfer': 981308301}
    counts = dict.fromkeys(first, 0)
    result = []
    for old in original:
        stratum = old['stratum']
        new = {**old, 'source_coordinate_id': old['id'], 'seed': first[stratum] + counts[stratum]}
        new.pop('id')
        new['id'] = digest(new)
        result.append(new)
        counts[stratum] += 1
    if counts != dict.fromkeys(first, 8):
        raise ValueError('exact24 readout coordinates required')
    return result


def validate_prompts(plan, prompts):
    original = read(PRIOR / 'prepared-v2/EVAL_PLAN_FINAL.json')
    frozen = {p['id']: p for p in read(PRIOR / 'prepared-v2/EVAL_PROMPTS.json')}
    if plan != build_plan(original) or len(prompts) != 24:
        raise ValueError('readout plan changed')
    for coord, prompt in zip(plan, prompts):
        old = frozen[coord['source_coordinate_id']]
        if (prompt['id'] != coord['id'] or prompt['prompt'] != old['prompt']
                or prompt['token_ids'] != old['token_ids'] or len(prompt['token_ids']) + 2048 > 8192):
            raise ValueError('native source prompt changed or cannot fit')


stack, prior = row.stack, row.prior


@functools.lru_cache(maxsize=1)
def verify():
    ready = read(ROOT / 'READY.json')
    if digest({k: v for k, v in ready.items() if k != 'identity'}) != ready['identity']:
        raise ValueError('new source manifest identity changed')
    for p, h in {**ready['source_sha256'], **ready['input_sha256']}.items():
        check(p, h)
    return ready


def phase_order():
    return tuple(read(ROOT / 'RECIPE.json')['phase_order'])


def control_selected():
    return row.checkpoint(CONTROL, row.PRIOR_IDENTITY, CONTROL_SHA)
