"""Pinned released Qwen3-4B base-service configuration without an adapter."""

from copy import deepcopy
from pathlib import Path

import study as s

OLD = s.SIDE / "strict-rlm-temperature-adherence-v1"


def config(model, directory, key):
    value = s.read(OLD / "configs/inference-replica0.json")
    value["vllm"].update(
        model=model["path"], served_model_name=[model["alias"]], dtype="bfloat16",
        enable_lora=False, enforce_eager=True, enable_prefix_caching=False,
        generation_config="vllm", max_model_len=8192, max_num_seqs=4, api_key=[key],
        reasoning_parser=None, tool_call_parser="hermes",
    )
    for name in ("max_loras", "max_lora_rank", "max_cpu_loras", "lora_dtype"):
        value["vllm"].pop(name, None)
    value.update(enable_fp32_lm_head=False, enable_fp32_router_logits=False,
                 output_dir=str(Path(directory) / "launcher"))
    return value


def descriptor(model, directory):
    return {
        "host": "127.0.0.1", "port": 18601, "replica": 0,
        "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY", "model_alias": model["alias"],
        "base_model": deepcopy(model), "adapter": None, "inference_only": True,
        "prime_inference_config": str(Path(directory) / "inference.json"),
        "vllm_version": "0.28.0", "max_model_len": 8192,
        "model_semantics": "Released instruction checkpoint without research adapter",
    }


def validate_descriptor(endpoint, model):
    if endpoint.get("adapter") is not None or endpoint.get("base_model") != model:
        raise ValueError("not exact no-adapter checkpoint")
    if endpoint.get("model_alias") != model["alias"] or endpoint.get("max_model_len") != 8192:
        raise ValueError("base alias or context differs")
    if endpoint.get("vllm_version") != "0.28.0":
        raise ValueError("runtime version differs")


def validate_models(payload, model):
    cards = payload.get("data", [])
    if len(cards) != 1 or cards[0].get("id") != model["alias"]:
        raise ValueError("live model alias differs")
    if cards[0].get("root") != model["path"] or cards[0].get("parent") is not None:
        raise ValueError("live base path or adapter state differs")

