"""Real TrainClient/rendering, synthetic transport only. No sockets, GPU, scores or episodes."""

import asyncio
import json
from unittest.mock import patch

import httpx
from openai import AsyncOpenAI

from driver import ROOT, make_client, native_call, read, renderer_for, request_for_alias, validate_token_evidence, verify_spec, write_once


async def main():
    spec = verify_spec()
    endpoint = {**spec["original_identity"], "host": "127.0.0.1", "port": 1,
                "api_key_env": "MRCR_CPU_FIXTURE_KEY", "model_alias": "CPU_ONLY_SYNTHETIC_FIXTURE"}
    renderer = renderer_for(endpoint["base_model"]["path"])
    completion_ids = renderer._tokenizer.encode("CPU_ONLY_FIXTURE.") + [151645]
    seen = []

    def transport(request):
        if request.method == "GET" and request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": endpoint["model_alias"], "max_model_len": 8192}]})
        assert request.method == "POST" and request.url.path == "/inference/v1/generate"
        body = json.loads(request.content)
        seen.append(body)
        return httpx.Response(200, json={"request_id": "CPU_ONLY_SYNTHETIC_FIXTURE", "choices": [{
            "token_ids": completion_ids, "finish_reason": "stop", "logprobs": {"content": [
                {"token": f"token_id:{token}", "logprob": -0.5} for token in completion_ids
            ]},
        }]})

    def build(config):
        return AsyncOpenAI(base_url=config.base_url, api_key="CPU_ONLY_FIXTURE", max_retries=0,
                           http_client=httpx.AsyncClient(transport=httpx.MockTransport(transport)))

    with patch("verifiers.v1.clients.train.build_async_openai", build):
        client = make_client(endpoint)
        try:
            details = []
            for item in read(ROOT / "inputs/requests.json"):
                body = request_for_alias(item["request"], endpoint["model_alias"])
                response = await native_call(client, body)
                tokens = response.model_dump(mode="json")["tokens"]
                counts = validate_token_evidence(tokens)
                assert tokens["prompt_ids"] == item["prompt_ids"]
                assert tokens["completion_ids"] == completion_ids
                assert tokens["completion_logprobs"] == [-0.5] * len(completion_ids)
                assert response.finish_reason == "stop" and not response.message.tool_calls
                wire = seen[-1]
                assert wire["token_ids"] == item["prompt_ids"]
                assert set(wire) == {"model", "token_ids", "sampling_params"}
                for key, value in spec["sampling"].items():
                    assert wire["sampling_params"][key] == value
                assert wire["sampling_params"]["logprobs"] == 1
                assert wire["sampling_params"]["seed"] == item["request"]["seed"]
                details.append({"row_id": item["coordinate"]["row_id"], "prompt_tokens": counts[0],
                                "synthetic_fixture_tokens": counts[1], "full_prompt_exact": True})
        finally:
            await client.close()
    result = {"schema": "cpu-only-native-wire-probe-v1", "spec_id": spec["spec_id"],
              "network_transport": "httpx.MockTransport; no sockets", "gpu_calls": 0,
              "real_TrainClient_and_Qwen3Renderer": True, "requests_verified": len(seen),
              "synthetic_logprobs_not_measurements": True, "details": details}
    write_once(ROOT / "CPU_PROBE.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
