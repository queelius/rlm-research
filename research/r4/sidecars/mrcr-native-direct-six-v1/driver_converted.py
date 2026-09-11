"""Additive exact-key-conversion binding for the frozen native-direct MRCR driver."""

from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import re
from pathlib import Path

import driver as v1

ROOT = v1.ROOT
SPEC = ROOT / "SPEC_CONVERTED.json"
PROOF = ROOT / "CONVERSION_PROOF.json"
CONVERTED = ROOT.parent / "single-gpu-self-sft-control-v1/inputs/step0-peft-key-conversion-v2"
BOUND = ROOT.parent / "leaf-role-routing-v1/BOUND_WEIGHTS.json"
ENDPOINT = ROOT.parent / "leaf-role-routing-v1/service-attempt-001/endpoint-original.json"
V1_SOURCE_SHA = "ad98dc4f07c16f78aad321f922f7c826daff342c3388aa571214ca4ac8ce99ec"
V1_SPEC_SHA = "62ff6d30352957ee98a9eb33249ba1d2abf46505be4d4c5e6ebf8a6e148201e6"
ORIGINAL_SHA = "e5be32e83aa00893f7c75074d79843b8a7f88cc4cf794fab75ca00c7b48e05a8"
CONVERTED_SHA = "857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6"
CONFIG_SHA = "e6828a7cbb97028a871958e71ba6b8a75ac4887c25008ac4dbf7366bd298fbc4"
MANIFEST_SHA = "428f0241a075977fa02fc3c315fad39a21bb1e02a31d26b0ff47e49c6c8d15ba"
BOUND_SHA = "a468f158cc81d5ee8a31ae3d03dfce9fb4faa567dcfc64445fd59c325b1c0e15"
ALIAS = "strict-rlm-qwen3-4b-role-original-v1"
_v1_validate = v1.validate_binding_identity


def prove_tensor_mapping(original, converted):
    """Independent byte-, dtype-, shape-, and key-exact proof; no tensor conversion."""
    import torch

    if set(converted) != {"base_model.model." + key for key in original}:
        raise ValueError("conversion has missing, extra, or incorrectly mapped keys")
    evidence = {}
    for key, source in sorted(original.items()):
        if not re.fullmatch(r"model\.layers\.\d+\.(?:mlp|self_attn)\.[a-z_]+\.lora_[AB]\.weight", key):
            raise ValueError("unexpected Prime tensor key")
        target_key = "base_model.model." + key
        target = converted[target_key]
        if source.device.type != "cpu" or target.device.type != "cpu":
            raise ValueError("proof must run on CPU")
        if source.dtype != torch.float32 or target.dtype != source.dtype:
            raise ValueError("FP32 tensor dtype identity failed")
        if source.shape != target.shape or not torch.equal(source, target):
            raise ValueError("tensor shape/value identity failed")
        before = hashlib.sha256(source.contiguous().numpy().tobytes()).hexdigest()
        after = hashlib.sha256(target.contiguous().numpy().tobytes()).hexdigest()
        if before != after:
            raise ValueError("tensor byte identity failed")
        evidence[key] = {"destination_key": target_key, "shape": list(source.shape),
                         "dtype": str(source.dtype), "tensor_bytes_sha256": before}
    return evidence


def verify_conversion():
    import torch
    from safetensors.torch import load_file

    torch.set_num_threads(2)
    original = v1.read(ROOT / "SPEC.json")["original_identity"]["adapter"]
    source = Path(original["path"])
    pinned = {ROOT / "driver.py": V1_SOURCE_SHA, ROOT / "SPEC.json": V1_SPEC_SHA,
              source / "adapter_model.safetensors": ORIGINAL_SHA,
              source / "adapter_config.json": CONFIG_SHA,
              CONVERTED / "adapter_model.safetensors": CONVERTED_SHA,
              CONVERTED / "adapter_config.json": CONFIG_SHA,
              CONVERTED / "CONVERSION.json": MANIFEST_SHA, BOUND: BOUND_SHA}
    for path, expected in pinned.items():
        if v1.file_hash(path) != expected:
            raise ValueError(f"pinned conversion provenance changed: {path}")
    manifest = v1.read(CONVERTED / "CONVERSION.json")
    if (manifest["source_adapter_sha256"] != ORIGINAL_SHA
            or manifest["destination_adapter_sha256"] != CONVERTED_SHA
            or Path(manifest["source_path"]).resolve() != source.resolve()
            or Path(manifest["destination_path"]).resolve() != CONVERTED.resolve()
            or not manifest["config_bytes_unchanged"]):
        raise ValueError("conversion manifest identity failed")
    before = load_file(source / "adapter_model.safetensors", device="cpu")
    after = load_file(CONVERTED / "adapter_model.safetensors", device="cpu")
    if len(before) != 504 or len(after) != 504:
        raise ValueError("expected exactly 504 adapter tensors on both sides")
    mapping = prove_tensor_mapping(before, after)
    if mapping != manifest["tensor_mapping"]:
        raise ValueError("fresh full tensor proof differs from conversion manifest")
    return {"schema": "mrcr-original-conversion-proof-v1", "tensor_count": 504,
            "all_values_shapes_dtypes_and_bytes_equal": True, "dtype": "torch.float32",
            "key_transform": "prepend base_model.model. only", "tensor_mapping": mapping,
            "source_sha256": {str(p): h for p, h in pinned.items()}, "device": "cpu",
            "gpu_launched": False, "live_memory_attestation": False}


def validate_converted_binding(endpoint, frozen):
    if frozen["adapter"]["model_sha256"] != ORIGINAL_SHA or frozen["adapter"]["config_sha256"] != CONFIG_SHA:
        raise ValueError("original rollout identity must remain unchanged")
    expected = copy.deepcopy(frozen)
    expected["adapter"] = {"path": str(CONVERTED), "model_sha256": CONVERTED_SHA,
                           "config_sha256": CONFIG_SHA}
    _v1_validate(endpoint, expected)
    if (Path(endpoint["adapter"]["path"]).resolve() != CONVERTED.resolve()
            or Path(endpoint["base_model"]["path"]).resolve() != Path(frozen["base_model"]["path"]).resolve()
            or endpoint["model_alias"] != ALIAS
            or endpoint.get("role_binding_sha256") != BOUND_SHA):
        raise ValueError("only the exact verified conversion/original service alias is admitted")


def prepare():
    original = v1.verify_spec()
    proof = verify_conversion()
    validate_converted_binding(v1.read(ENDPOINT), original["original_identity"])
    v1.write_once(PROOF, proof)
    spec = copy.deepcopy(original)
    spec.pop("spec_id")
    spec["schema"] = "mrcr-native-direct-six-exact-conversion-v2"
    spec["amendment"] = {
        "reason": "Original service alias uses tensor-identical PEFT key conversion, not original Prime file bytes.",
        "preserved_v1_spec_id": original["spec_id"],
        "only_change": "Binding admits the one pinned, freshly verified 504-FP32-tensor key conversion.",
        "converted_adapter": {"path": str(CONVERTED), "model_sha256": CONVERTED_SHA,
                              "config_sha256": CONFIG_SHA, "manifest_sha256": MANIFEST_SHA},
        "proof": str(PROOF), "proof_sha256": v1.file_hash(PROOF),
        "prepared_endpoint": str(ENDPOINT), "prepared_endpoint_sha256": v1.file_hash(ENDPOINT),
        "allowed_alias": ALIAS, "role_binding_sha256": BOUND_SHA,
        "runtime": "Fresh CPU full tensor proof before delegated v1 native calls; live alias/root/parent check retained.",
        "serving_precision": "Endpoint declares auto LoRA dtype with BF16 base; FP32 disk identity is not a live-memory FP32 claim.",
    }
    spec["endpoint_binding"] = "Only pinned converted original adapter, full tensor/dtype proof, exact original alias and live advertised root/parent. Original rollout identity retained."
    for path in (Path(__file__), ROOT / "test_driver_converted.py", ROOT / "SPEC.json", PROOF, BOUND,
                 CONVERTED / "CONVERSION.json"):
        spec["source_sha256"][str(path)] = v1.file_hash(path)
    spec["spec_id"] = v1.digest(spec)
    v1.write_once(SPEC, spec)
    PROOF.chmod(0o444)
    SPEC.chmod(0o444)
    return {"spec_id": spec["spec_id"], "tensor_count": proof["tensor_count"], "gpu_launched": False}


def verify():
    spec = v1.read(SPEC)
    if v1.digest({k: v for k, v in spec.items() if k != "spec_id"}) != spec["spec_id"]:
        raise ValueError("amended spec changed")
    for path, expected in {**spec["source_sha256"], **spec["upstream_source_sha256"]}.items():
        if v1.file_hash(path) != expected:
            raise ValueError(f"pinned amended source/input changed: {path}")
    if verify_conversion() != v1.read(PROOF):
        raise ValueError("fresh tensor proof differs from frozen proof")
    return spec


async def run(endpoint_path, output):
    verify()
    old_spec, old_validator = v1.SPEC, v1.validate_binding_identity
    try:
        # Only this fresh process uses the additive spec and exact-conversion validator.
        v1.SPEC, v1.validate_binding_identity = SPEC, validate_converted_binding
        await v1.run(endpoint_path, output)
    finally:
        v1.SPEC, v1.validate_binding_identity = old_spec, old_validator


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    sub.add_parser("verify")
    launch = sub.add_parser("run")
    launch.add_argument("--endpoint", type=Path, required=True)
    launch.add_argument("--output", type=Path, default=ROOT / "outputs/converted-attempt-001")
    args = parser.parse_args()
    if args.command == "run":
        asyncio.run(run(args.endpoint.resolve(), args.output.resolve()))
    else:
        result = prepare() if args.command == "prepare" else {"verified_spec_id": verify()["spec_id"]}
        print(v1.json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
