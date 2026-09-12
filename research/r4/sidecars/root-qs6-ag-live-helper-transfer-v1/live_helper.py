"""Exactly one live full16-to-four-B4 acquisition; no gold, query or reducer access."""

import asyncio
import contextlib
import copy
import itertools
import json
import time

import protocol
import study


async def acquire(context_records, request_text, frozen_requests, endpoint, output, coordinate_id,
                  query_index, tokenizer, deadline, send=None):
    if not protocol.match_request(request_text, context_records):
        raise ValueError("unsupported helper request: exact ordered full16 contract required")
    decoder = study.sources()[3]
    send = send or decoder.send
    maps, calls = [], []
    for bi, template in enumerate(frozen_requests):
        row = copy.deepcopy(template)
        row["call_id"] = study.digest([coordinate_id, "physical-B4", bi])
        row["body"]["sampling_params"]["seed"] += query_index * 4
        # Frozen JSON readers preserve wire order; explicit assertion guards future serialization.
        schema = json.loads(row["schema_ordered_json"])
        row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
        if list(schema["properties"]) != row["ids"] or schema["required"] != row["ids"]:
            raise ValueError("frozen ordered B4 schema differs")
        if len(row["body"]["token_ids"]) + 1024 > 8192:
            raise ValueError("input plus completion exceeds actual service context cap")
        call = await asyncio.to_thread(send, endpoint, row, tokenizer, output, deadline)
        call["coordinate_id"] = coordinate_id
        study.write_x(output / "helper-calls" / (row["call_id"] + ".json"), call)
        calls.append(call)
        if call.get("status") != "returned_valid":
            raise ValueError("physical helper call failed; no labels repaired or filled")
        maps.append(call["prediction"])
    labels = protocol.merge_maps(maps, [row["id"] for row in context_records])
    return labels, calls


def adapt(interface, binding, output, plan, public, helper_requests, tokenizer, endpoint, deadline):
    original_installed = interface.installed
    rows = {row["id"]: row for row in plan}
    _, _, _, _, causal = study.sources()

    @contextlib.contextmanager
    def installed(actual_binding, target, actual_plan, actual_public):
        if actual_binding != binding or actual_plan != plan or actual_public != public:
            raise ValueError("live helper installation inputs differ")
        with original_installed(actual_binding, target, actual_plan, actual_public):
            from verifiers.v1.clients.train import TrainClient, serialize_completion
            from verifiers.v1.types import AssistantMessage, Response
            original = TrainClient.get_response
            helper_seen = set()
            counter = itertools.count()
            roots = []

            async def get(client, dialect, body, sampling, session_id=None, turn=None, headers=None):
                coordinate = client.config.headers.get(interface.e.HEADER)
                if coordinate not in rows:
                    raise ValueError("request has no frozen episode coordinate")
                row = rows[coordinate]
                meta = interface.hooks.role.route(copy.deepcopy(body), headers,
                                                   binding["fixed_child"], binding["role_map"])
                if meta["depth"] == 0:
                    index = next(counter)
                    record = {"index": index, "coordinate_id": coordinate, "session_id": session_id,
                        "model": body["model"], "body": copy.deepcopy(body),
                        "sampling": sampling.model_dump(mode="json"),
                        "turn": {"trace_id": turn.trace.id} if turn is not None else {},
                        "started_epoch": time.time(), "status": "started"}
                    roots.append(record)
                    study.write_x(output / "root-native" / f"{index:04d}-start.json", record)
                    try:
                        response = await original(client, dialect, body, sampling, session_id=session_id,
                                                  turn=turn, headers=headers)
                        payload = response.model_dump(mode="json")
                        tokens = payload.get("tokens") or {}
                        action = tokens.get("completion_ids") or []
                        if not action or not tokens.get("prompt_ids") or len(action) != len(tokens.get("completion_logprobs") or []):
                            raise ValueError("root native token evidence missing")
                        prior = [r for r in roots if r["coordinate_id"] == coordinate and r is not record]
                        if not prior and tokens["prompt_ids"] != study.read(study.INPUTS / "PREFIXES.json")[coordinate]["token_ids"]:
                            raise ValueError("actual first root prefix differs from CPU-frozen prompt")
                        record.update(status="returned", response=payload,
                            evidence={"completion_ids_sha256": causal._digest(action)},
                            finish_reason=response.finish_reason)
                        return response
                    except BaseException as error:
                        record.update(status="error", error={"type": type(error).__name__, "message": str(error)})
                        raise
                    finally:
                        record["ended_epoch"] = time.time()
                        study.write_x(output / "root-native" / f"{index:04d}-result.json", record)
                receipt = {"coordinate_id": coordinate, **meta, "session_id": session_id,
                    "started_epoch": time.time(), "status": "started", "physical_calls": [],
                    "logical_wrapper_is_model_sample": False, "wrapper_native_tokens": None,
                    "wrapper_native_logprobs": None, "saved_prediction_replay": False}
                path = output / "helper-wrappers" / (meta["request_id"] + ".json")
                try:
                    if row["arm"] == "no_child_python" or meta["depth"] != 1 or meta["kind"] != "ordinary":
                        raise ValueError("helper unavailable or unsupported role")
                    if coordinate in helper_seen:
                        raise ValueError("one full16 helper acquisition per episode; no retries")
                    helper_seen.add(coordinate)
                    users = [m.get("content") for m in body.get("messages", []) if m.get("role") == "user"]
                    if len(users) != 1:
                        raise ValueError("helper must receive exactly one initial classification task")
                    labels, calls = await acquire(public[row["context_id"]]["records"], users[0],
                        helper_requests[row["context_id"]], endpoint, output, coordinate,
                        row["query_index"], tokenizer, deadline)
                    content = json.dumps(labels, separators=(",", ":"), ensure_ascii=False)
                    response = Response(id="live-B4-map-" + meta["request_id"], created=int(time.time()),
                        model=binding["fixed_child"], message=AssistantMessage(content=content),
                        finish_reason="stop", usage=None, tokens=None)
                    response.raw = serialize_completion(response, binding["fixed_child"])
                    receipt.update(status="returned", labels=labels, returned_content=content,
                        physical_calls=[call["call_id"] for call in calls],
                        returned_content_sha256=__import__("hashlib").sha256(content.encode()).hexdigest())
                    return response
                except BaseException as error:
                    receipt.update(status="error", error={"type": type(error).__name__, "message": str(error)})
                    raise
                finally:
                    receipt["ended_epoch"] = time.time()
                    study.write_x(path, receipt)

            TrainClient.get_response = get
            try:
                yield roots
            finally:
                TrainClient.get_response = original

    interface.installed = installed
    return interface
