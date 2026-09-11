"""Frozen native slots; parent-controlled service and strict current-weight binding."""
import argparse
import asyncio
import functools
import os
import time
from pathlib import Path

import native as n
import study as s
from common import c, starting_decision


def binding_for(policy):
    c.authenticate_policy(policy)
    original = s.read(s.SIDE / 'leaf-role-routing-v1/BOUND_WEIGHTS.json')
    child_alias = 'strict-rlm-qwen3-4b-role-sft-selected-v1'
    child = original['models'][child_alias]
    if child['adapter_sha256'] != s.CHILD_SHA:
        raise ValueError('fixed child changed')
    root_alias = f'strict-rlm-qwen3-4b-adaptive-root-{policy["step"]}-v1'
    path, decision, initial = starting_decision()
    return {**original, 'models': {root_alias: {k: policy[k] for k in ('path', 'adapter_sha256', 'config_sha256')}, child_alias: child},
            'role_map': {'root': root_alias, 'children': [child_alias]}, 'fixed_child': child_alias,
            'campaign_policy': policy, 'campaign_id': s.verify_prepared()['campaign_id'],
            'starting_binding': {'path': str(path), 'sha256': s.sha(path), 'kind': decision['kind'], 'policy0': initial},
            'adaptive_root_credit': {'root_unconstrained': True, 'fixed_child_typed': True, 'child_credit': False}}


def planned(phase):
    plans = s.read(s.ROOT / 'inputs/PLANS.json')
    if phase.startswith('round-'):
        return plans['training'][str(int(phase.split('-')[1]))]
    if phase.startswith('validation-'):
        return plans['validation']
    if phase in ('transfer-0', 'transfer-8'):
        return plans['transfer']
    raise ValueError('phase outside the fixed schedule')


def validate_descriptor(binding, descriptor, binding_sha, base_sha):
    root = binding['models'][binding['role_map']['root']]
    if (descriptor['model_alias'] != binding['role_map']['root']
            or descriptor['adapter'] != {'path': root['path'], 'model_sha256': root['adapter_sha256'], 'config_sha256': root['config_sha256']}
            or descriptor['role_binding_sha256'] != binding_sha
            or descriptor['base_model']['manifest_sha256'] != base_sha):
        raise ValueError('actual service descriptor differs from current policy/base/config')


def prepare_spec(phase, binding_path, endpoint_path, destination, cap, generation=None):
    spec = {'schema': s.ROOT.name, 'scientific': True, 'phase': phase, 'plan': planned(phase),
            'campaign_sha256': s.sha(s.ROOT / 'CAMPAIGN.json'), 'generation': generation,
            'binding_path': str(binding_path), 'binding_sha256': s.sha(binding_path), 'binding': s.read(binding_path),
            'endpoint_path': str(endpoint_path), 'endpoint_sha256': s.sha(endpoint_path), 'descriptor': s.read(endpoint_path),
            'cap_seconds': cap, 'workers': 4, 'environment': n.stack().interface.e.environment_config(),
            'runtime_ready_sha256': s.PINS[s.LOCAL / 'READY.json'],
            'serving_evidence': n.stack().native.e.capture.recursive.serving_evidence(endpoint_path.parent / 'inference.log')}
    s.write(destination, spec)
    return verify_spec(destination)


@functools.lru_cache(maxsize=None)
def verify_spec(path):
    campaign = s.verify_prepared()
    spec = s.read(path)
    if (spec['schema'] != s.ROOT.name or spec['scientific'] is not True
            or spec['campaign_sha256'] != s.sha(s.ROOT / 'CAMPAIGN.json')
            or spec['plan'] != planned(spec['phase']) or spec['workers'] != 4
            or spec['environment'] != n.stack().interface.e.environment_config()
            or spec['runtime_ready_sha256'] != s.PINS[s.LOCAL / 'READY.json']):
        raise ValueError('capture differs from frozen adaptive campaign')
    s.check(spec['binding_path'], spec['binding_sha256'])
    s.check(spec['endpoint_path'], spec['endpoint_sha256'])
    binding, descriptor = spec['binding'], spec['descriptor']
    if (binding != s.read(spec['binding_path']) or descriptor != s.read(spec['endpoint_path'])
            or binding != binding_for(binding['campaign_policy'])):
        raise ValueError('capture descriptor/current-start binding differs')
    validate_descriptor(binding, descriptor, spec['binding_sha256'], s.read(s.ROOT / 'RECIPE.json')['base_manifest_sha256'])
    n.stack().native.e.capture.recursive.validate_serving_evidence(spec['serving_evidence'])
    if spec['generation'] is not None:
        g, policy = spec['generation'], binding['campaign_policy']
        c.check_generation(g, policy, policy['step'])
        if g['campaign_id'] != campaign['campaign_id'] or g['coordinate_plan_sha256'] != s.digest(spec['plan']):
            raise ValueError('stale generation or altered plan')
    return spec


async def dispatch(plan, one, deadline):
    queue = asyncio.Queue()
    for row in plan:
        queue.put_nowait(row)
    async def worker():
        while time.time() < deadline:
            try:
                row = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            try:
                await one(row)
            finally:
                queue.task_done()
    workers = [asyncio.create_task(worker()) for _ in range(4)]
    try:
        await asyncio.wait_for(asyncio.gather(*workers), max(.001, deadline - time.time()))
        return None
    except TimeoutError:
        return 'collection_wall_cap'
    finally:
        for task in workers:
            if not task.done():
                task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)


async def collect(spec_path, output, deadline):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    import httpx
    spec = verify_spec(spec_path)
    output.mkdir(parents=True, exist_ok=False)
    s.write(output / 'SPEC.json', spec)
    started = time.time()
    deadline = min(deadline, started + spec['cap_seconds'])
    descriptor, binding = spec['descriptor'], spec['binding']
    url = f'http://{descriptor["host"]}:{descriptor["port"]}/v1'
    with httpx.Client(trust_env=False, timeout=15, headers={'Authorization': 'Bearer ' + os.environ[descriptor['api_key_env']]}) as client:
        response = client.get(url + '/models')
        response.raise_for_status()
        cards = {v['id']: v for v in response.json()['data']}
    for alias, model in binding['models'].items():
        if cards.get(alias, {}).get('root') != model['path'] or cards[alias].get('parent') != descriptor['base_model']['path']:
            raise ValueError('live /models alias/adapter/base mismatch')
    s.write(output / 'LIVE_MODELS.json', {'models': cards, 'checked_epoch': time.time()})
    endpoint = {'url': url, 'model': binding['role_map']['root'], 'renderer_model': descriptor['base_model']['path'],
                'api_key_env': descriptor['api_key_env']}
    public, gold = s.data()
    public = {v['id']: v for v in public}
    tasks, st = s.read(s.ROOT / 'inputs/TASKS.json'), n.stack()
    with s.aliases({'study': st.prior, 'interface': st.interface}):
        interface = st.local.configure_interface(output)
    rows, order = [], []
    async def one(row):
        order.append(row['id'])
        result = {'coordinate': row, 'started_epoch': time.time(), 'start_order': len(order) - 1, 'episode_path': None, 'error': None}
        try:
            context = public[row['context_id']]
            task = st.native.task(context, tasks[row['task_name']]['prompt'], gold[context['id']]['answers'][row['family']], row['task_name'])
            if task.hash != tasks[row['task_name']]['task_hash']:
                raise ValueError('actual frozen task identity differs before call')
            raw = (await env.run_slot(RunSlot(task), interface.e.make_context(endpoint, row))).to_record()
            path = output / 'episodes' / (row['id'] + '.json')
            s.write(path, raw)
            result.update(task_hash=task.hash, episode_path=str(path), episode_sha256=s.sha(path))
        except asyncio.CancelledError:
            result['censored'] = 'affected incomplete coordinate at cap'
            raise
        except Exception as error:
            result['error'] = {'type': type(error).__name__, 'message': str(error)}
        finally:
            result['ended_epoch'] = time.time()
            s.write(output / 'rows' / (row['id'] + '.json'), result)
            rows.append(result)
    with interface.installed(binding, output, spec['plan'], public):
        env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(spec['environment']))
        async with env.serving():
            stop = await dispatch(spec['plan'], one, deadline)
    missing = [r['id'] for r in spec['plan'] if r['id'] not in {v['coordinate']['id'] for v in rows}]
    if missing and stop is None:
        stop = 'deadline_before_all_slots'
    s.write(output / 'STATUS.json', {'recorded': len(rows), 'planned': len(spec['plan']), 'stop_reason': stop,
                                    'not_started': missing, 'started_epoch': started, 'ended_epoch': time.time(),
                                    'physical_attempts': len(list((output / 'typed-audit').glob('*-request.json')))})
    return 0 if stop is None and not missing else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--deadline', type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(collect(args.spec, args.output, args.deadline)))
