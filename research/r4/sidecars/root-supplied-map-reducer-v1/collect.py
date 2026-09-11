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

ACQUISITION_CODE = ('import json\nfrom rlm.api import run as rlm\n'
                    'from batch_contract import request_for\n'
                    'records = json.load(open("records.json"))\n'
                    'child = await rlm(request_for(records))\nprint(child.answer)')


def audits(directory, coordinate):
    return [value for path in (directory / 'typed-audit').glob('*-result.json')
            if (value := s.read(path))['coordinate']['id'] == coordinate]


def endpoint(binding, descriptor):
    return {**s.stack().native.e.old.planned_endpoint(binding),
            'url': f'http://{descriptor["host"]}:{descriptor["port"]}/v1',
            'api_key_env': descriptor['api_key_env']}


async def acquire(context, ci, binding, descriptor, directory, deadline):
    """One native c32 acquisition; scripted wrapper never denotes sampled root behavior."""
    import httpx
    from aiohttp import web
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    directory.mkdir(parents=True, exist_ok=False)
    n = s.stack().native
    tokenizer = n.renderer()._tokenizer
    coordinate = dict(id='acquire-' + context['id'], context_id=context['id'],
                      context_window_id=98133000 + ci, arm='typed', family='acquisition',
                      seed=981334101 + ci, temperature=.5, client_path='train')
    root_calls = child_calls = physical = 0
    started = time.time()
    result = dict(context_id=context['id'], coordinate=coordinate, status='unavailable', labels=None,
                  authored_root_not_policy=True, started_epoch=started)
    headers = {'Authorization': 'Bearer ' + os.environ[descriptor['api_key_env']]}
    async with httpx.AsyncClient(trust_env=False, timeout=120, headers=headers) as client:
        async def provider(request):
            nonlocal root_calls, child_calls, physical
            body = await request.json()
            physical += 1
            index = physical
            record = dict(body=body, started_epoch=time.time(), context_id=context['id'])
            try:
                if body['model'] == binding['fixed_child']:
                    child_calls += 1
                    record['origin'] = 'actual native c32'
                    response = await client.post(f'http://{descriptor["host"]}:{descriptor["port"]}/inference/v1/generate', json=body)
                    record.update(response=response.json(), status=response.status_code)
                    response.raise_for_status()
                    return web.json_response(response.json())
                if body['model'] != binding['role_map']['root']:
                    raise ValueError('unknown acquisition model')
                root_calls += 1
                if root_calls > 2:
                    raise ValueError('extra authored root call; no repair')
                answer = n.tool_action(ACQUISITION_CODE) if root_calls == 1 else 'Answer: 0'
                ids = tokenizer.encode(answer, add_special_tokens=False) + [151645]
                payload = {'request_id': f'AUTHORED_NOT_POLICY_{index}', 'choices': [{'token_ids': ids,
                           'finish_reason': 'stop', 'logprobs': {'content': [
                               {'token': f'token_id:{i}', 'logprob': 0.0} for i in ids]}}]}
                record.update(origin='authored wrapper, synthetic likelihoods NOT RL/SFT', response=payload, status=200)
                return web.json_response(payload)
            except BaseException as error:
                record['error'] = dict(type=type(error).__name__, message=str(error))
                raise
            finally:
                record['ended_epoch'] = time.time()
                s.write(directory / 'physical' / f'{index:04d}.json', record)

        app = web.Application()
        app.router.add_post('/inference/v1/generate', provider)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', 0)
        await site.start()
        actual_endpoint = {**endpoint(binding, descriptor),
                           'url': f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1'}
        try:
            interface = s.interface(directory)
            prompt = 'Acquire the full public-record category map using the typed child interface. This is an authored acquisition wrapper, not a learned root readout.'
            task = s.task(context, prompt, 0, coordinate)
            with interface.installed(binding, directory, [coordinate], {context['id']: context}):
                env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
                async with env.serving():
                    raw = (await asyncio.wait_for(env.run_slot(RunSlot(task), interface.e.make_context(actual_endpoint, coordinate)),
                                                   min(120, max(0, deadline - time.time())))).to_record()
            s.write(directory / 'EPISODE_AUTHORED_NOT_POLICY.json', raw)
            trace = raw['traces'][0]
            observations = [node['message']['content'] for node in trace['nodes'] if node.get('message', {}).get('role') == 'tool']
            if not trace.get('ok') or not trace.get('is_completed') or child_calls != 1 or root_calls != 2 or len(observations) != 1:
                raise ValueError('acquisition not one authentic completed child/map observation')
            labels = metrics.validate_map(observations[0], [r['id'] for r in context['records']])
            result.update(status='available', labels=labels,
                          episode_sha256=s.sha(directory / 'EPISODE_AUTHORED_NOT_POLICY.json'))
        except Exception as error:
            result['error'] = dict(type=type(error).__name__, message=str(error))
        finally:
            await runner.cleanup()
            result.update(ended_epoch=time.time(), actual_child_requests=child_calls, authored_root_requests=root_calls,
                          physical_records=[str(p) for p in (directory / 'physical').glob('*.json')],
                          native_audits=audits(directory, coordinate['id']))
            result['actual_child_usage'] = metrics.usage([r for r in result['native_audits'] if r['depth'] > 0])
            s.write(directory / 'MAP.json', result)
    return result


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
    deadline = min(args.deadline, started + 1200)
    public = s.read(s.ROOT / 'inputs/PUBLIC.json')
    host = s.read(s.ROOT / 'inputs/HOST_GOLD.json')
    plan = s.read(s.ROOT / 'inputs/PLAN.json')
    prompts = {r['id']: r for r in s.read(s.ROOT / 'inputs/PROMPTS.json')}
    s.write(args.output / 'INPUTS.json', dict(identity=ready['identity'], binding=binding, descriptor=descriptor,
            models=cards, started_epoch=started, shared_deadline=deadline, plan=plan))
    s.write(args.output / 'PLANNED_NULL_ENDPOINTS.json',
            [dict(coordinate=row, reward=None, status='planned; authoritative observed row supersedes this placeholder')
             for row in plan])
    maps = {}
    for ci, context in enumerate(public):
        if time.time() >= deadline:
            maps[context['id']] = dict(status='unavailable', labels=None, reason='unrun at shared deadline')
        else:
            maps[context['id']] = await acquire(context, ci, binding, descriptor, args.output / 'acquisitions' / context['id'], deadline)
    s.write(args.output / 'MAPS_READY.json', dict(maps=maps, map_files_sha256={str(p): s.sha(p)
            for p in (args.output / 'acquisitions').rglob('*.json')}, acquired_before_readout=True,
            gold_admission_selection=False, shared_acquisition_cost=True))
    output = args.output / 'readout'
    output.mkdir()
    interface = s.interface(output)
    contexts = {c['id']: c for c in public}
    results = {}
    actual_endpoint = endpoint(binding, descriptor)

    async def one(row):
        context = contexts[row['context_id']]
        gold = host[context['id']]['answers'][row['family']]
        labels = ({k: s.source().LABELS[v] for k, v in host[context['id']]['labels'].items()}
                  if row['map_source'] == 'dataset_oracle' else maps[context['id']]['labels'])
        result = dict(coordinate=row, gold=gold, started_epoch=time.time(), reward=None)
        try:
            if labels is None:
                result.update(unavailable_reason='native_map_acquisition_unavailable', completed=False)
                return
            prompt = prompts[row['id']]
            task = s.task(context, prompt['prompt'], gold, row, labels)
            if task.hash != prompt['task_hash']:
                raise ValueError('prepared native task hash changed')
            raw = (await asyncio.wait_for(env.run_slot(RunSlot(task), interface.e.make_context(actual_endpoint, row)),
                                           min(180, max(0, deadline - time.time())))).to_record()
            path = output / 'episodes' / (row['id'] + '.json')
            s.write(path, raw)
            trace = raw['traces'][0] if len(raw.get('traces', [])) == 1 else {}
            physical = audits(output, row['id'])
            roots = sorted((v for v in physical if v['depth'] == 0), key=lambda v: v['started_epoch'])
            if roots and roots[0].get('native_wire_request'):
                body = roots[0]['native_wire_request']['body']
                if body['token_ids'] != prompt['token_ids'] or body['model'] != binding['role_map']['root']:
                    raise ValueError('first actual native root prompt/model differs')
                result['first_wire_token_ids_equal'] = True
            result.update(metrics.score(trace, bool(roots) and roots[-1].get('status') == 'returned', gold))
            users = context['query_users'][:1] if row['family'] == 'single_user' else context['query_users']
            relevant = [r['id'] for r in context['records'] if r['user'] in users]
            result.update(evidence=metrics.evidence(trace, labels, relevant, s.source().LABELS[context['target']]),
                          episode_path=str(path), episode_sha256=s.sha(path),
                          extra_child_requests=sum(v['depth'] > 0 for v in physical),
                          native_audits=physical, usage=metrics.usage(physical), supplied_map_sha256=protocol.digest(labels))
        except asyncio.CancelledError:
            result.update(unavailable_reason='cancelled at shared deadline', completed=False)
            raise
        except Exception as error:
            result.update(error=dict(type=type(error).__name__, message=str(error)), completed=False)
        finally:
            result['ended_epoch'] = time.time()
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
            result = dict(coordinate=row, reward=None, completed=False, unavailable_reason='unrun at cap')
            s.write(output / 'rows' / (row['id'] + '.json'), result)
            results[row['id']] = result
    terminal = dict(planned=32, recorded=len(results), available=sum(r.get('reward') is not None for r in results.values()),
                    correct=sum(r.get('reward') == 1 for r in results.values()), elapsed_seconds=time.time() - started,
                    cells={source + ('_helper' if helper else '_python'): [r['id'] for r in plan
                           if (r['map_source'], r['reducer']) == (source, helper)]
                           for source in ('native_c32', 'dataset_oracle') for helper in (False, True)},
                    reduction_analysis='manual native code/observation audit required; scalar agreement is not reduction proof')
    s.write(args.output / 'TERMINAL.json', terminal)
    s.write(args.output / 'OUTPUT_INVENTORY.json', {str(p): s.sha(p) for p in args.output.rglob('*.json')})
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('binding', 'endpoint', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--deadline', type=float, required=True)
    raise SystemExit(asyncio.run(collect(parser.parse_args())))
