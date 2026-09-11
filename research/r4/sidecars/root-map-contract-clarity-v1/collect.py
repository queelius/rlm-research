"""MAIN-owned native collector; no model-service launch, no host sampled-code execution."""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path

import metrics
import protocol
import study as s

def audits(directory, coordinate):
    typed = [s.read(p) for p in (directory / 'typed-audit').glob('*-request.json')]
    ids = {v['request_id'] for v in typed if v['coordinate']['id'] == coordinate}
    result = {v['request_id']: v for p in (directory / 'role-audit').glob('*-result.json')
              if (v := s.read(p))['request_id'] in ids}
    for p in (directory / 'role-audit').glob('*-request.json'):
        v = s.read(p)
        if v['request_id'] in ids and v['request_id'] not in result:
            result[v['request_id']] = {**v, 'status': 'no retained result', 'native_response': None}
    return list(result.values())


def endpoint(binding, descriptor):
    return {**s.stack().native.e.old.planned_endpoint(binding),
            'url': f'http://{descriptor["host"]}:{descriptor["port"]}/v1',
            'api_key_env': descriptor['api_key_env']}


async def collect(args):
    import httpx
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    ready = s.verify()
    import runtime_binding
    runtime_binding.adapt()
    binding, descriptor = s.read(args.binding), s.read(args.endpoint)
    if binding != s.read(s.ROOT / 'inputs/BINDING.json'):
        raise ValueError('fixed root/child binding differs')
    validator = s.source().plan.private('binding.py', view=s.source().plan.old)
    validator.validate_descriptor(binding, descriptor, s.sha(args.binding))
    headers = {'Authorization': 'Bearer ' + os.environ[descriptor['api_key_env']]}
    async with httpx.AsyncClient(trust_env=False, timeout=15, headers=headers) as client:
        response = await client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models')
        response.raise_for_status()
        cards = {c['id']: c for c in response.json()['data']}
    for alias, model in binding['models'].items():
        if cards.get(alias, {}).get('root') != model['path'] or cards[alias].get('parent') != descriptor['base_model']['path']:
            raise ValueError('actual model cards differ')
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    deadline = min(args.deadline, started + 1650)
    public = s.read(s.ROOT / 'inputs/PUBLIC.json')
    host = s.read(s.ROOT / 'inputs/HOST_GOLD.json')
    plan = s.read(s.ROOT / 'inputs/PLAN.json')
    prompts = {r['id']: r for r in s.read(s.ROOT / 'inputs/PROMPTS.json')}
    s.write(args.output / 'INPUTS.json', dict(identity=ready['identity'], binding=binding, descriptor=descriptor,
            models=cards, started_epoch=started, shared_deadline=deadline, plan=plan))
    s.write(args.output / 'PLANNED_NULL_ENDPOINTS.json',
            [dict(coordinate=row, reward=None, status='planned; authoritative observed row supersedes this placeholder')
             for row in plan])
    maps = s.read(s.ROOT / 'inputs/MAPS.json')
    s.write(args.output / 'REUSED_MAPS.json', dict(maps=maps, acquisitions_new=0,
            acquisition_source_sha256=s.sha(s.ROOT / 'inputs/MAP_PROVENANCE.json'),
            acquired_before_this_study=True, gold_admission_selection=False,
            per_endpoint_full_cost='entire relevant acquisition, not amortized; reused not newly paid'))
    output = args.output / 'readout'
    output.mkdir()
    interface = s.interface(output)
    contexts = {c['id']: c for c in public}
    results = {}
    actual_endpoint = endpoint(binding, descriptor)

    async def one(row):
        context = contexts[row['context_id']]
        gold = host[context['id']]['answers'][row['family']]
        supplied = maps[context['id']]
        labels = supplied['labels']
        map_bytes = supplied['file_text'].encode('utf-8')
        result = dict(coordinate=row, gold=gold, started_epoch=time.time(), reward=None, available=False,
                      supplied_map_sha256=supplied['file_sha256'])
        try:
            prompt = prompts[row['id']]
            task = s.task(context, prompt['prompt'], gold, row, map_bytes)
            if task.hash != prompt['task_hash']:
                raise ValueError('prepared native task hash changed')
            raw = (await asyncio.wait_for(env.run_slot(RunSlot(task), interface.e.make_context(actual_endpoint, row)),
                                           min(180, max(0, deadline - time.time())))).to_record()
            path = output / 'episodes' / (row['id'] + '.json')
            s.write(path, raw)
            trace = raw['traces'][0] if len(raw.get('traces', [])) == 1 else {}
            physical = audits(output, row['id'])
            roles = {v['request_id']: v for v in physical}
            roots = [roles[v['acp']['request_id']] for v in trace['calls']
                     if roles[v['acp']['request_id']]['depth'] == 0]
            if not roots:
                raise ValueError('no physical root request')
            body = roots[0]['native_wire_request']['body']
            if body['token_ids'] != prompt['token_ids'] or body['model'] != binding['role_map']['root']:
                raise ValueError('first actual native root prompt/model differs')
            result['first_wire_token_ids_equal'] = True
            final, node_ids = metrics.final_capture(trace, roles)
            result.update(metrics.score(trace, final, gold))
            users = context['query_users'][:1] if row['family'] == 'single_user' else context['query_users']
            relevant = [r['id'] for r in context['records'] if r['user'] in users]
            result.update(evidence=metrics.evidence(trace, node_ids, labels, relevant,
                                                   s.source().LABELS[context['target']], result['available']),
                          episode_path=str(path), episode_sha256=s.sha(path),
                          final_physical_request_id=final['request_id'] if final else None,
                          final_branch_node_indices=node_ids)
        except asyncio.CancelledError:
            result.update(unavailable_reason='cancelled at shared deadline', completed=False)
            raise
        except Exception as error:
            result.update(error=dict(type=type(error).__name__, message=str(error)), completed=False,
                          reward=None, available=False)
        finally:
            physical = audits(output, row['id'])
            result.update(ended_epoch=time.time(), native_audits=physical,
                          extra_child_requests=sum(v['depth'] > 0 for v in physical),
                          cost=metrics.pipeline_cost(metrics.usage(physical), supplied['actual_child_usage']),
                          reused_authored_wrapper=supplied['authored_wrapper'])
            s.write(output / 'rows' / (row['id'] + '.json'), result)
            results[row['id']] = result

    with interface.installed(binding, output, plan, contexts):
        env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
        async with env.serving():
            queue = asyncio.Queue()
            for row in plan:
                queue.put_nowait(row)
            async def worker():
                while time.time() < deadline:
                    try:
                        row = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        return
                    await one(row)
            try:
                await asyncio.wait_for(asyncio.gather(*(worker() for _ in range(4))), max(0, deadline - time.time()))
            except TimeoutError:
                pass
    for row in plan:
        if row['id'] not in results:
            result = dict(coordinate=row, reward=None, available=False, completed=False, unavailable_reason='unrun at cap',
                          cost=metrics.pipeline_cost(metrics.usage([]), maps[row['context_id']]['actual_child_usage']),
                          reused_authored_wrapper=maps[row['context_id']]['authored_wrapper'])
            s.write(output / 'rows' / (row['id'] + '.json'), result)
            results[row['id']] = result
    terminal = dict(planned=96, recorded=len(results), available=sum(r.get('reward') is not None for r in results.values()),
                    correct=sum(r.get('reward') == 1 for r in results.values()), elapsed_seconds=time.time() - started,
                    new_map_acquisitions=0, reused_context_acquisitions=4,
                    cells={f'schema_{int(schema)}_map_contract_{int(map_contract)}': [r['id'] for r in plan
                           if (r['schema'], r['map_contract']) == (schema, map_contract)]
                           for schema in (False, True) for map_contract in (False, True)},
                    reduction_analysis='manual native code/observation audit required; scalar agreement is not reduction proof')
    s.write(args.output / 'TERMINAL.json', terminal)
    s.write(args.output / 'OUTPUT_INVENTORY.json', {str(p): s.sha(p) for p in args.output.rglob('*.json')})
    return 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    for name in ('binding', 'endpoint', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--deadline', type=float, required=True)
    return parser.parse_args(argv)


if __name__ == '__main__':
    raise SystemExit(asyncio.run(collect(parse_args())))
