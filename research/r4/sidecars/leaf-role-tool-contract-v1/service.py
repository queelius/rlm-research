"""Released Qwen3-4B base endpoint validation for the role/tool screen."""

import study as s


def validate_descriptor(endpoint):
    if endpoint.get("adapter") is not None or endpoint.get("base_model") != s.MODEL:
        raise ValueError("not exact no-adapter checkpoint")
    if endpoint.get("model_alias") != s.MODEL["alias"] or endpoint.get("max_model_len") != 8192:
        raise ValueError("base alias or context differs")
    if endpoint.get("vllm_version") != "0.28.0":
        raise ValueError("runtime version differs")


def validate_models(payload):
    cards = payload.get("data", [])
    if len(cards) != 1 or cards[0].get("id") != s.MODEL["alias"]:
        raise ValueError("live model alias differs")
    if cards[0].get("root") != s.MODEL["path"] or cards[0].get("parent") is not None:
        raise ValueError("live base path or adapter state differs")

