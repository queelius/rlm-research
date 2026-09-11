import asyncio
import importlib.util
from pathlib import Path

import httpx
from openai import AsyncOpenAI

spec = importlib.util.spec_from_file_location(
    "native_models_typed", Path(__file__).with_name("driver_live_models.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_models_probe_parses_actual_sdk_generic_dictionary():
    async def check():
        requests = []

        def response(request):
            requests.append(request)
            return httpx.Response(200, json={"data": [{"id": "original"}]})

        async with AsyncOpenAI(
            base_url="http://fake.invalid/v1",
            api_key="cpu-test-only",
            max_retries=0,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(response)),
        ) as client:
            module.fix_models_typing(client)
            result = await client.get("/models", cast_to=dict)
        assert result == {"data": [{"id": "original"}]}
        assert len(requests) == 1 and requests[0].url.path == "/v1/models"

    asyncio.run(check())
