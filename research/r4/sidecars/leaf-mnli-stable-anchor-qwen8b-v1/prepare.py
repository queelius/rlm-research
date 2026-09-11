"""CPU-only freeze and seal for the paired Qwen3-8B stable-key check."""
import copy
import json
from pathlib import Path
import time

import protocol as p
import study as s


def freeze(path, value):
    if path.exists():
        if s.read(path) != value:
            raise ValueError("frozen artifact differs: " + str(path))
    else:
        s.write(path, value)


def typed_prompt(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value = ChatCompletionRequest.model_validate(copy.deepcopy(body))
    if value.tools:
        raise ValueError("tools prohibited")
    return tokenizer.apply_chat_template(
        body["messages"], tools=None, add_generation_prompt=True, tokenize=True,
        return_dict=False, **value.chat_template_kwargs,
    )


def inputs():
    old_plan = s.read(s.PRIOR / "PLAN.json")
    old_requests = s.read(s.PRIOR / "REQUESTS.json")
    chosen = [row for row in old_plan if row["anchor"] in p.ANCHORS]
    if len(chosen) != 144:
        raise ValueError("expected exact 144-row subset")
    plan, requests = [], {}
    for position, old in enumerate(chosen):
        row = dict(old)
        row["source_id"] = old["id"]
        row["id"] = s.digest([s.ROOT.name, old["id"]])
        row["pair_position"] = position
        plan.append(row)
        body = copy.deepcopy(old_requests[old["id"]])
        body["model"] = s.MODEL["alias"]
        body["cache_salt"] = s.ROOT.name
        requests[row["id"]] = body
    for name in ("DATA.json", "PUBLIC.json", "ALIEN_DICTIONARIES.json", "DATASET_MANIFEST.json"):
        freeze(s.ROOT / name, s.read(s.PRIOR / name))
    freeze(s.ROOT / "PLAN.json", plan)
    freeze(s.ROOT / "REQUESTS.json", requests)
    tokenizer = s.tokenizer()
    prompt_ids = {}
    for row in plan:
        body = requests[row["id"]]
        ids = typed_prompt(tokenizer, body)
        if len(ids) + body["max_tokens"] > 8192:
            raise ValueError("8B native prompt exceeds context")
        prompt_ids[row["id"]] = ids
        old_body = old_requests[row["source_id"]]
        if body["messages"] != old_body["messages"] or body["structured_outputs"] != old_body["structured_outputs"]:
            raise ValueError("user prompt or output contract changed")
    wires = {key: s.serialize(value) for key, value in requests.items()}
    freeze(s.ROOT / "PROMPT_IDS.json", prompt_ids)
    freeze(s.ROOT / "ORDERED_REQUESTS.json", wires)
    import hashlib
    freeze(s.ROOT / "CPU_NATIVE.json", {
        "schema": "qwen3-8b-native-request-freeze-v1", "requests": len(requests),
        "gpu_calls": 0, "service_calls": 0,
        "request_wire_sha256": {key: hashlib.sha256(wire.encode()).hexdigest() for key, wire in wires.items()},
        "max_prompt_tokens": max(map(len, prompt_ids.values())),
        "max_prompt_plus_output": max(len(prompt_ids[key]) + requests[key]["max_tokens"] for key in requests),
    })
    freeze(s.ROOT / "PLANNED_NULL_ENDPOINTS.json", [p.null_row(row, "before service startup") for row in plan])
    freeze(s.ROOT / "WEIGHTS.json", {"schema": "released-base-model-binding-v1", "checkpoint": s.MODEL, "adapter": None})
    freeze(s.ROOT / "MODEL_PROVENANCE.json", {
        "schema": "local-huggingface-model-provenance-v1",
        "model": s.MODEL,
        "local_manifest_sha256": s.sha(s.MODEL_PATH / "local-research-manifest.json"),
        "model_card_sha256": s.sha(s.MODEL_PATH / "README.md"),
        "config_sha256": s.sha(s.MODEL_PATH / "config.json"),
        "generation_config_sha256": s.sha(s.MODEL_PATH / "generation_config.json"),
        "tokenizer_config_sha256": s.sha(s.MODEL_PATH / "tokenizer_config.json"),
        "note": "Cached manifest authenticates the full model; this freeze rechecked manifest and auxiliary files, not all tensor bytes.",
    })


def seal():
    sources = ["study.py", "protocol.py", "scoring.py", "collect.py", "service.py", "service_wrapper.py", "owner.py", "prepare.py", "test_cross_model.py", "DESIGN.md", "PLAN.md"]
    inputs_ = ["PLAN.json", "REQUESTS.json", "ORDERED_REQUESTS.json", "PROMPT_IDS.json", "CPU_NATIVE.json", "DATA.json", "PUBLIC.json", "ALIEN_DICTIONARIES.json", "DATASET_MANIFEST.json", "WEIGHTS.json", "MODEL_PROVENANCE.json", "PLANNED_NULL_ENDPOINTS.json"]
    ready = {
        "schema": "leaf-mnli-stable-anchor-qwen8b-ready-v1", "status": "READY_CPU_ONLY",
        "created_epoch": time.time(), "planned_endpoints": 144, "contexts": 16,
        "anchors": list(p.ANCHORS), "model": s.MODEL, "workers": 4,
        "request_seconds": 90, "outer_seconds": 2400, "work_seconds": 2250,
        "owned_seconds": 2370, "gpu_launch_authority": "MAIN only",
        "source_sha256": {str(s.ROOT / x): s.sha(s.ROOT / x) for x in sources},
        "input_sha256": {str(s.ROOT / x): s.sha(s.ROOT / x) for x in inputs_},
        "ancestor_sha256": {str(s.PRIOR / "READY.json"): s.sha(s.PRIOR / "READY.json"), str(s.MODEL_PATH / "local-research-manifest.json"): s.sha(s.MODEL_PATH / "local-research-manifest.json")},
    }
    ready["identity"] = s.digest(ready)
    freeze(s.ROOT / "READY.json", ready)
    return ready


if __name__ == "__main__":
    inputs(); print(json.dumps(seal(), sort_keys=True))
