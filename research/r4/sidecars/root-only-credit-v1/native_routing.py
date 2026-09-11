"""Trusted request-local mixed-role TrainClient routing and exact native wire capture."""

import contextlib
import contextvars
import json
import time
import uuid

from credit_data import ROOT, file_hash, load

ROLE_SOURCE = ROOT.parent / "leaf-role-routing-v1/source/routing.py"
if file_hash(ROLE_SOURCE) != "8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f":
    raise ValueError("qualified rootless role overlay source changed")
role = load("root_credit_role_overlay", ROLE_SOURCE)
write_once = role.write_once


def route_native(body, headers, role_map, child):
    return role.route(body, headers, child, role_map)


@contextlib.contextmanager
def installed_hooks(binding, output):
    from verifiers.v1.clients.train import TrainClient
    from verifiers.v1.harnesses.rlm.harness import RLMHarness

    original_get, original_setup = TrainClient.get_response, RLMHarness.setup
    active = contextvars.ContextVar("root_credit_native_call", default=None)
    clients = []

    async def wire_request(request):
        record = active.get()
        if record is None or request.url.path != "/inference/v1/generate":
            return
        body = json.loads(request.content)
        if body["model"] != record["actual_alias"]:
            raise ValueError("native wire alias diverged from trusted role")
        for key, value in {"temperature": 0.5, "top_p": 1, "top_k": -1, "min_p": 0, "max_tokens": 2048}.items():
            if body["sampling_params"].get(key) != value:
                raise ValueError(f"actual native sampling differs: {key}")
        if "native_wire_request" in record:
            raise ValueError("unexpected native retry")
        record["native_wire_request"] = {"url": str(request.url), "body": body}

    async def wire_response(response):
        record = active.get()
        if record is not None and response.request.url.path == "/inference/v1/generate":
            await response.aread()
            record["native_wire_response"] = {"http_status": response.status_code, "body": response.text}

    async def setup(self, runtime):
        await original_setup(self, runtime)
        result = await runtime.run(["python", "-c", role.overlay_program()], {})
        write_once(output / "runtime-overlays" / f"{uuid.uuid4().hex}.json",
            {"runtime": runtime.name, "exit_code": result.exit_code, "stdout": result.stdout, "stderr": result.stderr})
        if result.exit_code:
            raise RuntimeError("owned rootless nano role instrumentation failed")

    async def get_response(self, dialect, body, sampling, session_id=None, turn=None, headers=None):
        record = {"session_id": session_id, "started": time.time(), "status": "not_routed"}
        identifier = uuid.uuid4().hex
        token = active.set(record)
        try:
            if self.config.renderer.model_dump(exclude_none=True) != {"name": "qwen3", "enable_thinking": True}:
                raise ValueError("native renderer contract changed")
            record.update(route_native(body, headers, binding["role_map"], binding["fixed_child"]))
            record["model_sha256"] = binding["models"][body["model"]]["adapter_sha256"]
            record["sampling"] = sampling.model_dump(mode="json", exclude_none=True)
            record["status"] = "routed"
            client = self.client._client
            if client not in clients:
                client.event_hooks["request"].append(wire_request)
                client.event_hooks["response"].append(wire_response)
                clients.append(client)
            write_once(output / "role-audit" / f"{identifier}-request.json", record)
            response = await original_get(self, dialect, body, sampling, session_id=session_id, turn=turn, headers=headers)
            record["native_response"] = response.model_dump(mode="json")
            record["status"] = "returned"
            if response.model != record["actual_alias"] or not record.get("native_wire_response"):
                raise ValueError("native returned alias/raw wire evidence missing")
            return response
        except BaseException as error:
            record.update(status="error", error_type=type(error).__name__, error=str(error))
            raise
        finally:
            record["ended"] = time.time()
            write_once(output / "role-audit" / f"{identifier}-result.json", record)
            active.reset(token)

    TrainClient.get_response, RLMHarness.setup = get_response, setup
    try:
        yield
    finally:
        TrainClient.get_response, RLMHarness.setup = original_get, original_setup
        for client in clients:
            client.event_hooks["request"].remove(wire_request)
            client.event_hooks["response"].remove(wire_response)
