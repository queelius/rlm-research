"""Exercise the actual inspected nano model-call body with the real HTTP SDK."""
import ast
import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from openai import AsyncOpenAI, InternalServerError

import overlay


def call_method(source):
    tree = ast.parse(source)
    method = next(node for node in ast.walk(tree)
                  if isinstance(node, ast.AsyncFunctionDef) and node.name == '_call_model')
    module = ast.Module(body=[method], type_ignores=[])
    async def call_with_retries(function, **kwargs):
        # Success-only comparison; the failure test asserts this path is absent.
        return await function(**kwargs)
    namespace = {'Any': object, 'TokenUsage': object,
        'model_call_headers': lambda rid: {'Idempotency-Key': rid, 'x-rlm-request-id': rid},
        'call_with_retries': call_with_retries,
        'extract_usage': lambda response: SimpleNamespace(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens)}
    exec(compile(module, '<inspected-operator-nano-call-body>', 'exec'), namespace)
    return namespace['_call_model']


async def exercise(source, status):
    requests = []
    async def respond(request):
        requests.append({'body': json.loads(request.content), 'headers': dict(request.headers)})
        if status != 200:
            return httpx.Response(status, json={'error': {'message': 'CPU fixture failure'}})
        return httpx.Response(200, json={'id': 'fixture', 'created': 0, 'object': 'chat.completion',
            'model': 'original', 'choices': [{'index': 0, 'finish_reason': 'stop',
            'message': {'role': 'assistant', 'content': 'exact text'}}],
            'usage': {'prompt_tokens': 13, 'completion_tokens': 3, 'total_tokens': 16}})
    client = AsyncOpenAI(api_key='cpu-fixture', base_url='http://fixture/v1', max_retries=2,
                         http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    failed = []
    engine = SimpleNamespace(client=client, model='original', depth=0, _invocation_id='inv',
        _semantic_edges=SimpleNamespace(start_request=lambda *a, **k: 'physical-id',
            fail_request=failed.append, finish_request=lambda rid: None),
        _active_tool_schemas=[{'type': 'function', 'function': {'name': 'ipython',
            'parameters': {'type': 'object', 'properties': {}}}}],
        _total_usage=SimpleNamespace(prompt_tokens=0, completion_tokens=0))
    try:
        result = await call_method(source)(engine, [{'role': 'user', 'content': 'unchanged'}])
        return requests, result, engine
    except InternalServerError:
        assert failed == ['physical-id']
        return requests, None, engine
    finally:
        await client.close()


def test_owned_overlay_makes_one_http_attempt_even_if_sdk_default_allows_retries():
    patched = overlay.patched_engine(overlay.NANO_ENGINE.read_text())
    assert 'await call_with_retries(' not in patched, 'inherited 315-second retry wrapper remains'
    requests, result, _ = asyncio.run(exercise(patched, 500))
    assert result is None and len(requests) == 1


def test_transport_amendment_preserves_model_request_body_response_and_usage():
    source = overlay.NANO_ENGINE.read_text()
    old, old_result, old_engine = asyncio.run(exercise(source, 200))
    new, new_result, new_engine = asyncio.run(exercise(overlay.patched_engine(source), 200))
    assert old[0]['body'] == new[0]['body']
    assert old_result[0].model_dump() == new_result[0].model_dump()
    assert vars(old_engine._total_usage) == vars(new_engine._total_usage)
    assert new[0]['headers']['x-mrcr-submit-phase'] == 'prefix'
