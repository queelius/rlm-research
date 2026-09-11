"""Real owned rootless/native two-call proof; provider tokens are CPU fixtures only."""
import argparse
import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path

from aiohttp import web

import driver
import study


async def qualify(output, prefix_calls=1):
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    output.mkdir(parents=True, exist_ok=False)
    descriptor = study.read(study.ROOT.parent / 'leaf-role-routing-v1/service-attempt-001/endpoint-original.json')
    tokenizer = create_renderer(load_tokenizer(descriptor['base_model']['path']),
        Qwen3RendererConfig(enable_thinking=True))._tokenizer
    candidate = 'CPU: α\nline\\two'
    requests = []
    async def provider(request):
        body = await request.json()
        requests.append(body)
        prompt = tokenizer.decode(body['token_ids'])
        assert study.SYSTEM_CONTRACT in prompt, 'actual native system contract is absent'
        if len(requests) <= prefix_calls:
            assert '/context.txt' in prompt and 'submit_text' in prompt
            code = "context_data=open('/context.txt',encoding='utf-8').read()\nassert len(context_data)>0\n"
            code += ('submit_text(' + repr(candidate) + ')') if len(requests) == prefix_calls else "print('CPU inspection')"
            text = '</think>\n<tool_call>\n' + json.dumps({'name': 'ipython', 'arguments': {'code': code}}) + '\n</tool_call>'
        else:
            assert len(requests) == prefix_calls + 1, 'unexpected retry or extra model call'
            assert 'Return the exact value of answer_utf8' in prompt
            assert json.dumps({'answer_utf8': candidate}, ensure_ascii=False) in prompt
            text = '</think>\n' + candidate
        ids = tokenizer.encode(text, add_special_tokens=False) + [151645]
        return web.json_response({'request_id': f'CPU_ONLY_{len(requests)}', 'choices': [{
            'token_ids': ids, 'finish_reason': 'stop', 'logprobs': {'content': [
                {'token': f'token_id:{token}', 'logprob': -0.5} for token in ids]}}]})

    async def models(request):
        return web.json_response({'data': [{'id': descriptor['model_alias'], 'max_model_len': 8192}]})

    app = web.Application()
    app.router.add_post('/inference/v1/generate', provider)
    app.router.add_get('/v1/models', models)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    endpoint = {**descriptor, 'url': f'http://127.0.0.1:{port}/v1',
                'observed_max_model_len': 8192,
                'api_key_env': 'MRCR_COMMIT_CPU_FIXTURE_KEY'}
    os.environ['MRCR_COMMIT_CPU_FIXTURE_KEY'] = 'cpu-fixture-not-a-provider-secret'
    os.environ['PATH'] = str(study.ROOT / 'bin') + os.pathsep + os.environ.get('PATH', '')
    os.environ.setdefault('VERIFIERS_CACHE_DIR', '/project/alex_phd/cache/verifiers-prime')
    environment = SingleAgentEnv(SingleAgentEnvConfig.model_validate(driver.environment_config()))
    tasks = {task.data.name: task for task in environment.taskset}
    case = study.read(study.ROOT / 'inputs/PUBLIC.json')['cases'][0]
    try:
        async with environment.serving():
            row = await driver.run_case(environment, tasks[case['task_name']], endpoint, case,
                                        output / 'case-0', 250)
        study.write_once(output / 'PROVIDER_REQUESTS.json', requests)
        pair = (row['captured'] or {}).get('pair')
        assert pair is not None, 'real REPL candidate did not reach paired finalizer'
        assert pair['candidate'] == candidate and pair['restatement']['text'] == candidate
        assert pair['restatement']['valid_terminal']
        assert base64.b64decode(pair['candidate_utf8_base64']) == candidate.encode()
        assert len(requests) == len(row['calls']) == prefix_calls + 1
        assert [call['phase'] for call in row['calls']] == ['prefix'] * prefix_calls + ['restatement']
        assert all(call['status'] == 'returned' and call['nano_request_id'] for call in row['calls'])
        assert study.classify_restatement(pair, row['calls'])['classification'] == 'byte_faithful_copy'
        assert row['calls'][-1]['generation_budget']['prompt_tokens'] == len(requests[-1]['token_ids'])
        assert all(call['response']['tokens']['prompt_ids'] == request['token_ids']
                   for call, request in zip(row['calls'], requests, strict=True))
        assert row['captured']['host_project_visible'] is False
        assert row['captured']['host_home_visible'] is False
        result = {'real_owned_rootless_runtime': True, 'real_REPL_submission_and_finalizer': True,
            'real_TrainClient_and_native_renderer': True, 'physical_provider_calls': prefix_calls + 1,
            'shared_prefix_calls': prefix_calls,
            'exact_candidate_bytes_sha256': hashlib.sha256(candidate.encode()).hexdigest(),
            'prefix_and_restatement_byte_fidelity': True, 'gpu_calls': 0,
            'provider': 'CPU deterministic fixture only', 'synthetic_logprobs_not_measurements': True,
            'logical_prompt_tokens': sum(call['logical_input_tokens'] for call in row['calls']),
            'action_tokens': sum(call['action_tokens'] for call in row['calls']),
            'executed_overlay': row['captured']['overlay']}
        study.write_once(output / 'RESULT.json', result)
        print(json.dumps(result), flush=True)
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prefix-calls', type=int, choices=[1, 5], default=1)
    args = parser.parse_args()
    asyncio.run(qualify(args.output, args.prefix_calls))
