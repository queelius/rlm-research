"""Actual mixed24 native/export/replay/trainer-preflight compatibility fixture."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import time

from aiohttp import web
import httpx

import warm_collect_v2 as collect
import warm_common as common
import warm_export_v2 as export
import warm_native_v2 as native
import warm_study as study


def test_actual_mixed24_export_native_replay_and_trainer_preflight(tmp_path, monkeypatch):
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU_FIXTURE_NOT_CREDENTIAL")

    async def fixture():
        binding = collect.binding_for(study.fixed_start())
        root = binding["models"][binding["role_map"]["root"]]
        base = study.read(study.ROOT / "RECIPE.json")
        plan = study.candidate_plan(1)
        public, host = study.data()
        gold = {row["seed"]: host[row["context_id"]]["answers"][row["family"]] for row in plan}
        tokenizer = native.stack().native.renderer()._tokenizer
        calls = []

        async def provider(request):
            body = await request.json()
            assert body["model"] == binding["role_map"]["root"]
            seed = body["sampling_params"]["seed"]
            answer = gold[seed] if plan[[r["seed"] for r in plan].index(seed)]["repeat"] < 4 else gold[seed] + 997
            reply = f"Answer: {answer}"
            ids = tokenizer.encode(reply, add_special_tokens=False) + [151645]
            calls.append({"seed": seed, "prompt": body["token_ids"], "completion": ids})
            return web.json_response({
                "request_id": f"WARMV2AUTH_{len(calls)}",
                "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids)},
                "choices": [{"token_ids": ids, "finish_reason": "stop",
                             "logprobs": {"content": [{"token": f"token_id:{value}",
                                                          "logprob": -0.5} for value in ids]}}],
            })

        async def models(_request):
            return web.json_response({"data": [
                {"id": alias, "root": model["path"], "parent": base["base_model"],
                 "max_model_len": 8192} for alias, model in binding["models"].items()]})

        app = web.Application()
        app.router.add_post("/inference/v1/generate", provider)
        app.router.add_get("/v1/models", models)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        stage = tmp_path / "service"
        study.write(stage / "BINDING.json", binding)
        descriptor = {
            "host": "127.0.0.1", "port": port,
            "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY",
            "model_alias": binding["role_map"]["root"],
            "adapter": {"path": root["path"], "model_sha256": root["adapter_sha256"],
                        "config_sha256": root["config_sha256"]},
            "role_binding_sha256": study.sha(stage / "BINDING.json"),
            "base_model": {"path": base["base_model"],
                           "manifest_sha256": base["base_manifest_sha256"]},
        }
        study.write(stage / "service/endpoint-original.json", descriptor)
        (stage / "service/inference.log").write_text("{'logprobs_mode': 'processed_logprobs'}\n")
        generation = common.generation(1, study.fixed_start())
        collect.prepare_spec("window-1", stage / "BINDING.json",
                             stage / "service/endpoint-original.json", stage / "SPEC.json",
                             360, generation)
        cards = [{"id": alias, "root": model["path"], "parent": base["base_model"],
                  "max_model_len": 8192} for alias, model in binding["models"].items()]
        class ModelResponse:
            def raise_for_status(self):
                return None
            def json(self):
                return {"data": cards}
        monkeypatch.setattr(httpx.Client, "get", lambda *_args, **_kwargs: ModelResponse())
        try:
            code = await collect.collect(stage / "SPEC.json", tmp_path / "rollout", time.time() + 360)
        finally:
            await runner.cleanup()
        assert code == 0 and len(calls) == 24
        manifest = export.export_attempt(tmp_path / "rollout", tmp_path / "export")
        assert manifest["complete"] and manifest["training_group_episodes"] == 24
        rows = study.read(tmp_path / "export/EPISODES.json")
        assert {row["reward"] for row in rows} == {0, 1}
        assert all(row["trace_trainable"] and row["turns"] for row in rows)
        assert all(len(turn["old_logprobs"]) > 0 for row in rows for turn in row["turns"])
        return generation

    generation = asyncio.run(fixture())
    native_result = subprocess.run(
        [str(study.NATIVE), str(study.ROOT / "warm_native_v2.py"), "verify-export",
         "--output", str(tmp_path / "export")], check=True, text=True, capture_output=True,
        timeout=180, env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    assert json.loads(native_result.stdout)["replayed"] == 24
    study.write(tmp_path / "GENERATION.json", generation)
    trainer = subprocess.run(
        [str(study.TRAIN), str(study.ROOT / "warm_train_v2.py"), "--group",
         str(tmp_path / "export/GROUP.json"), "--generation", str(tmp_path / "GENERATION.json"),
         "--preflight", "--deadline", str(time.time() + 180)],
        check=True, text=True, capture_output=True, timeout=240,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    result = json.loads(trainer.stdout)
    assert result["candidate_window"] == 1
    assert result["native_replay"]["replayed"] == 24
