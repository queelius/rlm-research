"""Authored CPU provider fixture over actual fresh an27 native RLM runtimes."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import time
import native as n
import protocol as p
import study as s


async def qualify(output):
    from aiohttp import web
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    tokenizer = s.tokenizer(); started = time.time()
    output.mkdir(parents=True, exist_ok=False)
    world = p.worlds()[0]; package = p.evidence(world, 'direct', [])
    rows = [dict(id='cpu-present', python=True, seed=981391901),
            dict(id='cpu-absent', python=False, seed=981391901),
            dict(id='cpu-unadvertised', python=False, seed=981391902)]
    calls = []; per_row = {}
    # Authored benign fixture; deliberately not a purchase-answer algorithm.
    code = 'from pathlib import Path\nassert Path("evidence.txt").read_text() == Path("context.txt").read_text()\nprint("JOIN_CPU_OBSERVATION", len(Path("query.txt").read_text()) > 0)\nchild = await rlm("Return only CPU_CHILD_NATIVE_SENTINEL")\nprint(child.answer)'
    action = '<tool_call>\n' + json.dumps(dict(name='ipython', arguments=dict(code=code))) + '\n</tool_call>'
    async def provider(request):
        body = await request.json(); identifier = request.headers.get(n.HEADER)
        if identifier not in {r['id'] for r in rows}:
            raise ValueError('CPU coordinate header missing: ' + str(identifier))
        turn = per_row.get(identifier, 0); per_row[identifier] = turn + 1
        text = tokenizer.decode(body['token_ids'])
        if identifier == 'cpu-present':
            if 'Return only CPU_CHILD_NATIVE_SENTINEL' in text and 'Evidence:' not in text:
                completion = 'CPU_CHILD_NATIVE_SENTINEL'
            elif turn == 0: completion = action
            else:
                if 'JOIN_CPU_OBSERVATION True' not in text or 'CPU_CHILD_NATIVE_SENTINEL' not in text:
                    raise ValueError('actual tool/child observation missing')
                completion = '[]'
        elif identifier == 'cpu-unadvertised': completion = action
        else: completion = '[]'
        ids = tokenizer.encode(completion, add_special_tokens=False) + [151645]
        calls.append(dict(coordinate=identifier, body=body, authored_completion=completion))
        return web.json_response(dict(request_id=f'CPU_ONLY_{len(calls)}', choices=[dict(
            token_ids=ids, finish_reason='stop', logprobs=dict(content=[dict(token=f'token_id:{t}', logprob=-.5) for t in ids]))]))
    async def models(request):
        return web.json_response(dict(data=[dict(id=s.MODEL['alias'], root=s.MODEL['path'], parent=None, max_model_len=8192)]))
    app = web.Application(); app.router.add_post('/inference/v1/generate', provider); app.router.add_get('/v1/models', models)
    runner = web.AppRunner(app); await runner.setup(); site = web.TCPSite(runner, '127.0.0.1', 0); await site.start()
    endpoint = dict(host='127.0.0.1', port=site._server.sockets[0].getsockname()[1], api_key_env='JOIN_CPU_FIXTURE_KEY')
    os.environ['JOIN_CPU_FIXTURE_KEY'] = 'cpu-fixture-not-a-provider-secret'
    results = []
    try:
        with n.installed(output, rows):
            env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.environment_config()))
            async with env.serving():
                async def one(row):
                    task = n.task(world, package, row)
                    episode = await asyncio.wait_for(env.run_slot(RunSlot(task), n.context(endpoint, row)), 120)
                    raw = episode.to_record(); s.write(output / (row['id'] + '.json'), raw)
                    results.append(dict(row=row, raw=raw))
                await asyncio.gather(*(one(row) for row in rows))
        s.write(output / 'PROVIDER_REQUESTS.json', calls)
        by_id = {v['row']['id']: v['raw'] for v in results}
        traces = {k: v['traces'][0] for k, v in by_id.items() if len(v.get('traces', [])) == 1}
        if set(traces) != set(by_id): raise ValueError('missing actual native trace')
        if per_row != {'cpu-present': 3, 'cpu-absent': 1, 'cpu-unadvertised': 1}:
            raise ValueError('unexpected actual native request counts: ' + str(per_row))
        if traces['cpu-present']['root_reply'] != '[]' or traces['cpu-absent']['root_reply'] != '[]':
            raise ValueError('native terminal fixture failed')
        def tools(trace): return [x for x in trace['nodes'] if x['message'].get('role') == 'tool']
        if len(tools(traces['cpu-present'])) != 1 or tools(traces['cpu-absent']) or tools(traces['cpu-unadvertised']):
            raise ValueError('native tool execution inventory failed')
        setup = [traces[x]['info']['join_setup']['file_sha256'] for x in ('cpu-present', 'cpu-absent')]
        if setup[0] != setup[1]: raise ValueError('paired actual file bytes differ')
        audits = [s.read(path) for path in (output / 'role-audit').glob('*-result.json')]
        first = {r['coordinate']['id']: r for r in audits if r['depth'] == 0 and len(r['native_request']['messages']) == 2}
        a, b = first['cpu-present']['native_request'], first['cpu-absent']['native_request']
        if a['messages'] != b['messages'] or not a.get('tools') or b.get('tools'):
            raise ValueError('actual native first-body contrast failed')
        import collect
        m = collect.metrics(); final_scores = {}
        for identifier, trace in traces.items():
            roles = {r['request_id']: r for r in audits if r['coordinate']['id'] == identifier}
            final, branch = m.final_capture(trace, roles)
            final_scores[identifier] = collect.terminal_score(trace, final, [], world['customers'])
        if final_scores['cpu-present']['reward'] != 1 or final_scores['cpu-absent']['reward'] != 1:
            raise ValueError('actual whole-native final scoring failed')
        if final_scores['cpu-unadvertised']['reward'] == 1:
            raise ValueError('unadvertised tool-shaped output incorrectly succeeds')
        if sum(r['depth'] == 1 for r in audits) != 1: raise ValueError('actual native child route missing')
        proof = dict(passed=True, native_calls=len(calls), actual_present_tool_observations=1,
                     actual_disabled_tool_observations=0, actual_files_and_messages_equal=True,
                     private_in_memory_override=True, installed_sources_mutated=False,
                     gpu_calls=0, model_service_calls=0, provider='authored CPU fixture',
                     synthetic_transport_logprobs_not_measurements=True, elapsed_seconds=time.time()-started,
                     actual_child_calls=1, actual_full_branch_final_scores=final_scores,
                     qualified_source_sha256={str(s.ROOT / name): s.sha(s.ROOT / name) for name in
                         ('native.py', 'protocol.py', 'study.py', 'join_taskset.py', 'collect.py', 'qualify_native.py')})
        s.write(output / 'RESULT.json', proof); print(proof, flush=True)
        return proof
    finally:
        await runner.cleanup(); os.environ.pop('JOIN_CPU_FIXTURE_KEY', None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); asyncio.run(qualify(args.output))
