"""32 direct-source native interface roots, with physical-cost and NULL ledgers."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import time
import native as n
import protocol as p
import study as s


def metrics():
    return s.load('join_qualified_final_capture', s.SIDE / 'root-example-map-visibility-v1/metrics.py',
                  '0ef6a89ad3655afe71226878f0296802e6b8af62b5aa295eec23e3ed151c53d3')


def attempt_usage(records):
    accounting = []
    for record in records:
        body = (record.get('native_wire_response') or {}).get('body')
        if isinstance(body, str):
            try: body = json.loads(body)
            except ValueError: body = None
        accounting.append(dict(native_wire_response=dict(body=body)))
    return metrics().usage(accounting)


def terminal_score(trace, capture, gold, customers):
    response = (capture or {}).get('native_response') or {}; message = response.get('message') or {}
    reply = trace.get('root_reply')
    available = ((capture or {}).get('status') == 'returned' and response.get('finish_reason') in ('stop', 'length')
                 and not message.get('tool_calls') and isinstance(reply, str) and message.get('content') == reply)
    return {**p.score(reply, gold, customers, available=available), 'reply': reply,
            'finish_reason': response.get('finish_reason'), 'operational_success': int(available and p.score(reply, gold, customers)['reward'] == 1)}


def policy_failure_metadata(row, records):
    attempts = [r['request_id'] for r in records if not row['python'] and r.get('depth') == 0
                and r.get('status') == 'returned' and r.get('native_wire_request')
                and not r.get('native_request', {}).get('tools')
                and (r.get('native_response') or {}).get('message', {}).get('tool_calls')]
    return dict(observed_unadvertised_tool_attempt=bool(attempts), unadvertised_tool_request_ids=attempts,
                failure_class='policy_failure' if attempts else None)


async def dispatch(rows, one, deadline):
    queue = asyncio.Queue()
    for row in rows: queue.put_nowait(row)
    async def worker():
        while time.time() < deadline:
            try: row = queue.get_nowait()
            except asyncio.QueueEmpty: return
            try: await one(row)
            finally: queue.task_done()
    try:
        await asyncio.wait_for(asyncio.gather(*(worker() for _ in range(4))), max(.001, deadline-time.time()))
    except TimeoutError: return False
    return queue.empty()


def audit_records(output, identifier):
    requests = [s.read(path) for path in (output / 'role-audit').glob('*-request.json')]
    chosen = {r['request_id']: r for r in requests if r['coordinate']['id'] == identifier}
    for request_id in list(chosen):
        result = output / 'role-audit' / (request_id + '-result.json')
        if result.exists(): chosen[request_id] = s.read(result)
    return chosen


def trace_evidence(trace):
    programs, observations = [], []
    for index, node in enumerate(trace.get('nodes', [])):
        message = node.get('message') or {}
        if message.get('role') == 'tool': observations.append(dict(node=index, content=message.get('content')))
        for call in message.get('tool_calls') or []:
            if call.get('name') != 'ipython': continue
            args = call.get('arguments')
            try: code = (json.loads(args) if isinstance(args, str) else args)['code']
            except (ValueError, TypeError, KeyError): code = None
            programs.append(dict(node=index, code=code, raw_tool_call=call))
    return dict(programs=programs, observations=observations, actual_aggregation=None,
                actual_data_flow='requires code/observation audit; no generated code reexecution')


def first_prefix(world, package, row, tools, renderer):
    messages = [dict(role='system', content=p.SYSTEM), dict(role='user', content=p.prompt(world, package))]
    selected = tools if row['python'] else []
    rendered = renderer.render(messages, tools=selected or None, add_generation_prompt=True)
    if len(rendered.token_ids) + 2560 > 8192: raise ValueError('initial native input/output budget does not fit')
    return dict(messages=messages, tools=selected, tools_ordered_json=p.serialize(selected), token_ids=rendered.token_ids)


async def run(args):
    import httpx
    import owner
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    owner.validate_argv([str(s.NATIVE), str(s.ROOT / 'collect.py'), 'run', '--endpoint', str(args.endpoint),
                        '--output', str(args.output), '--deadline', str(args.deadline)])
    ready = s.verify(); endpoint = s.read(args.endpoint); s.service.validate_descriptor(endpoint, s.MODEL)
    worlds = s.read(s.ROOT / 'WORLDS.json'); by_world = {w['id']: w for w in worlds}
    plan = s.read(s.ROOT / 'PLAN.json')
    gold = s.read(s.ROOT / 'HOST_GOLD.json'); tools = json.loads(s.read(s.ROOT / 'NATIVE_TOOLS.json')['ordered_json'])
    tokenizer = s.tokenizer(); renderer = create_renderer(load_tokenizer(s.MODEL['path']), Qwen3RendererConfig(enable_thinking=True))
    args.output.mkdir(parents=True, exist_ok=False); started = time.time(); root_deadline = min(args.deadline - 60, started + 1140)
    s.write(args.output / 'RUN.json', dict(identity=ready['identity'], endpoint=endpoint, started_epoch=started,
                                          deadline=args.deadline, root_deadline=root_deadline, planned=32, acquisitions=0))
    s.write(args.output / 'PLANNED_NULL_ENDPOINTS.json', [p.null_row(row, 'preplanned') for row in plan])
    headers = {'Authorization': 'Bearer ' + os.environ[endpoint['api_key_env']]}
    async with httpx.AsyncClient(headers=headers, trust_env=False, timeout=30) as client:
        response = await client.get(f'http://{endpoint["host"]}:{endpoint["port"]}/v1/models')
        response.raise_for_status(); s.service.validate_models(response.json(), s.MODEL)
        s.write(args.output / 'LIVE_IDENTITY.json', dict(models=response.json(), endpoint=endpoint))
    packages = {(w['id'], order, arm): p.evidence(p.ordered_world(w,order), arm, []) for w in worlds for order in p.ORDERS for arm in p.REPRESENTATIONS}
    m = metrics(); results = {}; out = args.output / 'native'; out.mkdir()
    async def one(row):
        world = p.ordered_world(by_world[row['world_id']],row['record_order']); package = packages[(world['id'], row['record_order'], row['representation'])]
        result = p.null_row(row, 'native endpoint not returned'); result['started_epoch'] = time.time()
        result['acquisition_ids'] = package['acquisition_ids']
        try:
            if not package['available']:
                result.update(unavailable_reason=package['reason'], cause='source_extraction_gate', source_available=False); return
            result['source_available'] = True
            expected = first_prefix(world, package, row, tools, renderer)
            s.write(out / 'prepared' / (row['id'] + '.json'), dict(coordinate=row, package=package, expected=expected))
            task = n.task(world, package, row)
            raw = (await asyncio.wait_for(env.run_slot(RunSlot(task), n.context(endpoint, row)), min(120, max(.001, root_deadline-time.time())))).to_record()
            s.write(out / 'episodes' / (row['id'] + '.json'), raw)
            trace = raw['traces'][0] if len(raw.get('traces', [])) == 1 else {}
            roles = audit_records(out, row['id'])
            root_calls = sorted([r for r in roles.values() if r['depth'] == 0], key=lambda x: x['started_epoch'])
            if not root_calls: raise ValueError('no retained actual native root request')
            first = root_calls[0]
            if first['native_request']['messages'] != expected['messages'] or first['native_tools_ordered_json'] != expected['tools_ordered_json'] or first.get('native_wire_request', {}).get('body', {}).get('token_ids') != expected['token_ids']:
                raise ValueError('first actual native request differs from frozen root prefix')
            final, nodes = m.final_capture(trace, roles)
            result.update(terminal_score(trace, final, gold[world['id']], world['customers']), completed=True,
                          first_native_prefix_verified=True, final_node_indices=nodes,
                          final_request_id=final['request_id'] if final else None, trace_errors=trace.get('errors'),
                          episode_errors=raw.get('errors'), setup_attestation=trace.get('info', {}).get('join_setup'),
                          evidence=trace_evidence(trace))
            if not result['available']: result['cause'] = 'no_native_final_see_actual_trace'
        except asyncio.CancelledError:
            result.update(cause='inclusive_work_deadline', unavailable_reason='cancelled before native final'); raise
        except Exception as error:
            result.update(error=dict(type=type(error).__name__, message=str(error)), cause='native_run_or_capture_failure')
        finally:
            roles = audit_records(out, row['id']); physical = [r for r in roles.values() if r.get('native_wire_request')]
            policy = policy_failure_metadata(row, list(roles.values())); result.update(policy)
            if policy['observed_unadvertised_tool_attempt']:
                result['operational_success'] = 0
                if not result['available']: result['cause'] = 'observed_unadvertised_tool_attempt'
            result.update(ended_epoch=time.time(), physical_attempts=len(physical), returned_completions=sum(r.get('status') == 'returned' for r in physical),
                          new_usage=attempt_usage(physical), new_child_attempts=sum(r['depth'] > 0 for r in physical),
                          native_request_ids=list(roles), elapsed_seconds=time.time()-result['started_epoch'])
            s.write(args.output / 'rows' / (row['id'] + '.json'), result); results[row['id']] = result
    with n.installed(out, plan):
        env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.environment_config()))
        async with env.serving(): await dispatch(plan, one, root_deadline)
    for row in plan:
        if row['id'] not in results:
            result = p.null_row(row, 'unrun at inclusive work deadline'); result['cause'] = 'unrun_work_cap'
            result['acquisition_ids'] = packages[(row['world_id'], row['record_order'], row['representation'])]['acquisition_ids']
            s.write(args.output / 'rows' / (row['id'] + '.json'), result); results[row['id']] = result
    values = [results[r['id']] for r in plan]
    zero = m.usage([])
    native_usage = dict(calls=sum(r.get('new_usage', zero)['calls'] for r in values),
        known={k: sum(r.get('new_usage', zero)['known'][k] for r in values) for k in zero['known']},
        unknown={k: sum(r.get('new_usage', zero)['unknown'][k] for r in values) for k in zero['unknown']})
    s.write(args.output / 'COST_LEDGER.json', dict(all_new_physical=native_usage,
        actual_unique_acquisition_attempts=0, planned_hypothetical_acquisition_charges=0,
        returned_native_completions=sum(r.get('returned_completions', 0) for r in values),
        attempted_requests_not_necessarily_sampled_or_billed=True, provider_billing='unknown/not measured',
        host_context_preparation='CPU serialization/rendering ledger in frozen INPUT_PROVENANCE.json'))
    cells = {}
    for rep in p.REPRESENTATIONS:
        for enabled in (True,):
            group = [r for r in values if r['coordinate']['representation'] == rep and r['coordinate']['python'] == enabled]
            cells[rep+'/'+str(enabled)] = dict(planned=len(group), available=sum(r['available'] for r in group),
                correct=sum(r['reward'] == 1 for r in group), operational_success=sum(r['operational_success'] for r in group))
    s.write(args.output / 'SUMMARY.json', dict(cells=cells, rows=values, acquisitions=[], world_clusters=8,
                 costs='Physical native root/optional-child requests and observed tokens/time; no acquisition; provider billing unknown'))
    status = dict(planned=32, recorded=len(values), available=sum(r['available'] for r in values), correct=sum(r['reward'] == 1 for r in values),
                  physical_root_pipeline_attempts=sum(r.get('physical_attempts', 0) for r in values),
                  complete=len(values) == 32, all_native_finals_available=all(r['available'] for r in values), elapsed_seconds=time.time()-started)
    s.write(args.output / 'STATUS.json', status)
    s.write(args.output / 'OUTPUT_INVENTORY.json', {str(path): s.sha(path) for path in args.output.rglob('*.json')})
    return status


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=('run',))
    for flag in ('endpoint', 'output'): parser.add_argument('--'+flag, type=Path, required=True)
    parser.add_argument('--deadline', type=float, required=True); args = parser.parse_args()
    print(asyncio.run(run(args)))
