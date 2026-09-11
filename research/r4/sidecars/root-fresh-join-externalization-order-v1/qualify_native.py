"""Authored CPU-only native two-interface/file/root/child/final qualification."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time
import collect as c
import native as n
import protocol as p
import study as s


async def qualify(output):
    from aiohttp import web
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    output.mkdir(parents=True, exist_ok=False); started = time.time()
    tokenizer = s.tokenizer()
    renderer = create_renderer(load_tokenizer(s.MODEL['path']), Qwen3RendererConfig(enable_thinking=True))
    world = p.ordered_world(p.worlds()[0],'random')
    rows = [dict(id='cpu-external-'+arm, python=True, seed=981591901, representation=arm) for arm in p.REPRESENTATIONS]
    packages = {r['id']: p.evidence(world, r['representation'], []) for r in rows}
    calls, counts, results = [], {}, {}
    def action(row):
        package = packages[row['id']]
        code = 'from pathlib import Path\nimport hashlib\n'
        for name, value in {'evidence.dat':package['files']['evidence.dat'], 'context.txt':package['text'], 'query.txt':p.query(world)}.items():
            code += f'assert hashlib.sha256(Path({name!r}).read_bytes()).hexdigest() == {hashlib.sha256(value.encode()).hexdigest()!r}\n'
        code += 'print("INTERFACE_CPU_OK")'
        if row['representation'] == 'E':
            code += '\nchild = await rlm("Return only INTERFACE_CHILD_SENTINEL")\nprint(child.answer)'
        return '<tool_call>\n' + json.dumps(dict(name='ipython', arguments=dict(code=code))) + '\n</tool_call>'
    async def provider(request):
        body = await request.json(); identifier = request.headers[n.HEADER]
        row = next(r for r in rows if r['id'] == identifier)
        text = tokenizer.decode(body['token_ids']); turn = counts.get(identifier, 0); counts[identifier] = turn+1
        if 'Return only INTERFACE_CHILD_SENTINEL' in text and 'Evidence:' not in text:
            completion = 'INTERFACE_CHILD_SENTINEL'
        elif turn == 0: completion = action(row)
        else:
            if 'INTERFACE_CPU_OK' not in text: raise ValueError('missing actual file observation')
            completion = '[]'
        ids = tokenizer.encode(completion, add_special_tokens=False) + [151645]
        calls.append(dict(coordinate=identifier, body=body, authored_completion=completion))
        return web.json_response(dict(request_id=f'CPU_INTERFACE_{len(calls)}', choices=[dict(
            token_ids=ids, finish_reason='stop', logprobs=dict(content=[dict(token=f'token_id:{t}', logprob=-.5) for t in ids]))]))
    app = web.Application(); app.router.add_post('/inference/v1/generate', provider)
    runner = web.AppRunner(app); await runner.setup(); site = web.TCPSite(runner, '127.0.0.1', 0); await site.start()
    endpoint = dict(host='127.0.0.1', port=site._server.sockets[0].getsockname()[1], api_key_env='INTERFACE_CPU_KEY')
    os.environ['INTERFACE_CPU_KEY'] = 'authored-fixture-not-provider-secret'
    try:
        with n.installed(output, rows):
            env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.environment_config()))
            async with env.serving():
                async def one(row):
                    raw = (await asyncio.wait_for(env.run_slot(RunSlot(n.task(world, packages[row['id']], row)), n.context(endpoint, row)), 120)).to_record()
                    s.write(output / (row['id']+'.json'), raw); results[row['id']] = raw
                await asyncio.gather(*(one(row) for row in rows))
        s.write(output / 'PROVIDER_REQUESTS.json', calls)
        if counts != {'cpu-external-I': 2, 'cpu-external-E': 3}:
            raise ValueError('unexpected authored native calls: '+str(counts))
        inventories, checks = set(), []
        for row in rows:
            raw = results[row['id']]
            if len(raw['traces']) != 1: raise ValueError('missing native trace')
            trace = raw['traces'][0]; roles = c.audit_records(output, row['id'])
            roots = sorted([v for v in roles.values() if v['depth'] == 0], key=lambda x: x['started_epoch'])
            first = roots[0]; tools = json.loads(first['native_tools_ordered_json']); inventories.add(first['native_tools_ordered_json'])
            expected = c.first_prefix(world, packages[row['id']], row, tools, renderer)
            if first['native_request']['messages'] != expected['messages'] or first['native_wire_request']['body']['token_ids'] != expected['token_ids']:
                raise ValueError('actual interface prefix differs')
            observations = [x['message']['content'] for x in trace['nodes'] if x['message'].get('role') == 'tool']
            if len(observations) != 1 or 'INTERFACE_CPU_OK' not in observations[0] or 'AssertionError' in observations[0]:
                raise ValueError('actual file byte assertion/observation failed')
            if row['representation'] == 'E' and 'INTERFACE_CHILD_SENTINEL' not in observations[0]:
                raise ValueError('actual optional child observation absent')
            final, branch = c.metrics().final_capture(trace, roles)
            score = c.terminal_score(trace, final, [], world['customers'])
            if score['reward'] != 1: raise ValueError('actual native final not authenticated')
            checks.append(dict(row=row, expected_prefix_sha256=s.digest(expected['token_ids']),
                setup=trace['info']['join_setup'], final_score_against_fixture_only=score, final_branch=branch))
        if len(inventories) != 1: raise ValueError('tool inventory differs by arm')
        audits = [s.read(f) for f in (output/'role-audit').glob('*-result.json')]
        if sum(a['depth'] == 1 for a in audits) != 1: raise ValueError('expected one native child')
        proof = dict(passed=True, native_calls=len(calls), actual_child_calls=1, checks=checks,
            ordered_tools_json=next(iter(inventories)), gpu_calls=0, model_service_calls=0,
            provider='authored CPU fake; synthetic likelihoods and answers are not scientific measurements',
            elapsed_seconds=time.time()-started, qualified_source_sha256={str(s.ROOT/name): s.sha(s.ROOT/name)
                for name in ('study.py','protocol.py','native.py','join_taskset.py','collect.py','qualify_native.py')})
        s.write(output/'RESULT.json', proof); print(dict(passed=True,native_calls=len(calls)), flush=True)
    finally:
        await runner.cleanup(); os.environ.pop('INTERFACE_CPU_KEY',None)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    asyncio.run(qualify(parser.parse_args().output))
