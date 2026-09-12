"""Exact adapter/Adam/RNG restoration for an authenticated procedural-SFT checkpoint."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random


def file_sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tensor_state_digest(value) -> str:
    """Device-independent identity over scalar metadata and tensor dtype/shape/bytes."""
    import torch

    digest = hashlib.sha256()

    def visit(item):
        if isinstance(item, torch.Tensor):
            tensor = item.detach().cpu().contiguous()
            digest.update(str((str(tensor.dtype), tuple(tensor.shape))).encode())
            digest.update(tensor.numpy().tobytes())
        elif isinstance(item, dict):
            for key in sorted(item, key=lambda key: (type(key).__name__, str(key))):
                digest.update(repr(key).encode())
                visit(item[key])
        elif isinstance(item, (list, tuple)):
            digest.update(str(type(item)).encode())
            for element in item:
                visit(element)
        else:
            digest.update(repr(item).encode())

    visit(value)
    return digest.hexdigest()


def restore_rng(saved: dict, *, restore_cuda: bool) -> None:
    import numpy as np
    import torch

    if set(saved) != {"python", "numpy", "torch_cpu", "torch_cuda"}:
        raise ValueError("parent RNG schema differs")
    if len(saved["torch_cuda"]) != 1 or saved["torch_cuda"][0].dtype != torch.uint8:
        raise ValueError("one saved CUDA RNG state is required")
    random.setstate(saved["python"])
    np.random.set_state(saved["numpy"])
    torch.set_rng_state(saved["torch_cpu"])
    if restore_cuda:
        if torch.cuda.device_count() != 1:
            raise ValueError("exactly one visible GPU is required for RNG restore")
        torch.cuda.set_rng_state_all(saved["torch_cuda"])


def restore_state(model, checkpoint: Path, *, restore_cuda: bool = True):
    """Verify the loaded adapter and restore the original optimizer slots and RNG."""
    import torch
    from safetensors.torch import load_file

    checkpoint = Path(checkpoint)
    state = json.loads((checkpoint / "state.json").read_text())
    step = int(state["optimizer_steps"])
    if step != int(state["step"]) or step < 1:
        raise ValueError("parent optimizer step differs")
    named = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
    if len(named) != 504 or any("lora_" not in name or p.dtype != torch.float32 for name, p in named):
        raise ValueError("exact504 FP32 trainable LoRA parameters required")
    saved_adapter = load_file(checkpoint / "adapter_model.safetensors", device="cpu")
    keys = [name.replace(".default.", ".") for name, _ in named]
    if set(keys) != set(saved_adapter) or any(
        not torch.equal(parameter.detach().cpu(), saved_adapter[key])
        for key, (_, parameter) in zip(keys, named, strict=True)
    ):
        raise ValueError("loaded adapter parameters differ from the parent checkpoint")
    raw_optimizer = torch.load(checkpoint / "optimizer.pt", map_location="cpu", weights_only=True)
    groups = raw_optimizer["param_groups"]
    if (
        len(groups) != 1
        or groups[0]["params"] != list(range(504))
        or groups[0]["lr"] != 1e-4
        or groups[0]["weight_decay"] != 0.0
        or set(raw_optimizer["state"]) != set(range(504))
        or {int(value["step"]) for value in raw_optimizer["state"].values()} != {step}
    ):
        raise ValueError("parent Adam state/recipe differs")
    for index, (_, parameter) in enumerate(named):
        for key in ("exp_avg", "exp_avg_sq"):
            moment = raw_optimizer["state"][index][key]
            if moment.shape != parameter.shape or moment.dtype != torch.float32 or not torch.isfinite(moment).all():
                raise ValueError("parent Adam slot shape/dtype/support differs")
    optimizer = torch.optim.AdamW([p for _, p in named], lr=1e-4, weight_decay=0.0)
    optimizer.load_state_dict(raw_optimizer)
    expected = tensor_state_digest(raw_optimizer)
    actual = tensor_state_digest(optimizer.state_dict())
    if actual != expected:
        raise ValueError("loaded Adam moments/metadata differ from the saved state")
    saved_rng = torch.load(checkpoint / "rng.pt", map_location="cpu", weights_only=False)
    restore_rng(saved_rng, restore_cuda=restore_cuda)
    return optimizer, {
        "restored_step": step,
        "adapter_parameters_exact": True,
        "optimizer_state_exact": True,
        "optimizer_tensor_state_identity": actual,
        "trainable_parameter_order": [name for name, _ in named],
        "adapter_model_sha256": file_sha(checkpoint / "adapter_model.safetensors"),
        "optimizer_sha256": file_sha(checkpoint / "optimizer.pt"),
        "rng_sha256": file_sha(checkpoint / "rng.pt"),
        "cuda_rng_restored": restore_cuda,
    }
