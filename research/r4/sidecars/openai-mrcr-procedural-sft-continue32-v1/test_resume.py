"""Focused CPU qualification using the actual saved checkpoint4 LoRA/Adam/RNG."""

import importlib.util
import random
from pathlib import Path

import numpy as np
import pytest
import torch
from peft import LoraConfig, get_peft_model
from safetensors.torch import load_file
from transformers import AutoConfig, AutoModelForCausalLM


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "openai-mrcr-procedural-sft-warmstart-v1"
CHECKPOINT = SOURCE / "outputs/attempt-001/checkpoint-0004"
BASE = Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554")


def implementation():
    spec = importlib.util.spec_from_file_location("continuation_resume", ROOT / "resume.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def actual_adapter_on_meta_base():
    """No base weights or GPU: real model hierarchy with only saved LoRA tensors materialized."""
    config = AutoConfig.from_pretrained(BASE, local_files_only=True)
    with torch.device("meta"):
        base = AutoModelForCausalLM.from_config(config, dtype=torch.bfloat16)
        model = get_peft_model(
            base, LoraConfig.from_pretrained(CHECKPOINT),
            autocast_adapter_dtype=True, low_cpu_mem_usage=True,
        )
    for config in model.peft_config.values():
        config.inference_mode = False
    model.set_adapter("default")
    saved = load_file(CHECKPOINT / "adapter_model.safetensors")
    for name, parameter in list(model.named_parameters()):
        if parameter.requires_grad:
            parent, attribute = name.rsplit(".", 1)
            model.get_submodule(parent)._parameters[attribute] = torch.nn.Parameter(
                saved[name.replace(".default.", ".")].clone()
            )
    return model


def test_actual_checkpoint_restores_adam_rng_and_matches_step5():
    torch.set_num_threads(4)
    resume = implementation()
    model = actual_adapter_on_meta_base()
    optimizer, receipt = resume.restore_state(model, CHECKPOINT, restore_cuda=False)
    parameters = [p for p in model.parameters() if p.requires_grad]
    assert len(parameters) == 504
    assert {int(s["step"]) for s in optimizer.state.values()} == {4}
    assert receipt["optimizer_state_exact"] is True
    assert receipt["adapter_parameters_exact"] is True
    assert receipt["restored_step"] == 4
    actual_draw = (random.random(), float(np.random.random()), torch.rand(4))
    saved_rng = torch.load(CHECKPOINT / "rng.pt", map_location="cpu", weights_only=False)
    random.setstate(saved_rng["python"])
    np.random.set_state(saved_rng["numpy"])
    torch.set_rng_state(saved_rng["torch_cpu"])
    expected_draw = (random.random(), float(np.random.random()), torch.rand(4))
    assert actual_draw[:2] == expected_draw[:2]
    assert torch.equal(actual_draw[2], expected_draw[2])
    assert len(saved_rng["torch_cuda"]) == 1
    assert saved_rng["torch_cuda"][0].dtype == torch.uint8

    # Independent reference uses the first two original optimizer slots, which include
    # nonzero saved moments. Fresh Adam or dropped moments changes this resumed update.
    raw = torch.load(CHECKPOINT / "optimizer.pt", map_location="cpu", weights_only=True)
    reference_parameters = [torch.nn.Parameter(p.detach().clone()) for p in parameters[:2]]
    reference = torch.optim.AdamW(reference_parameters, lr=1e-4, weight_decay=0.0)
    groups = [{**raw["param_groups"][0], "params": [0, 1]}]
    reference.load_state_dict({"state": {i: raw["state"][i] for i in (0, 1)}, "param_groups": groups})
    assert any(torch.count_nonzero(raw["state"][i]["exp_avg"]) for i in (0, 1))
    for original, expected in zip(parameters[:2], reference_parameters, strict=True):
        gradient = torch.linspace(-0.01, 0.01, original.numel()).reshape(original.shape)
        original.grad = gradient.clone()
        expected.grad = gradient.clone()
    optimizer.step()
    reference.step()
    assert all(torch.equal(a, b) for a, b in zip(parameters[:2], reference_parameters, strict=True))
    assert all(int(optimizer.state[p]["step"]) == 5 for p in parameters[:2])


def test_actual_adapter_tensor_change_rejects_resume():
    resume = implementation()
    model = actual_adapter_on_meta_base()
    parameter = next(p for p in model.parameters() if p.requires_grad)
    with torch.no_grad():
        parameter.flatten()[0] += 0.125
    with pytest.raises(ValueError, match="adapter parameters"):
        resume.restore_state(model, CHECKPOINT, restore_cuda=False)


def test_checkpoint_binding_rebinds_primary32_through_original_saver(monkeypatch):
    import train

    monkeypatch.setattr(train.study.original_train, "eval_binding", train.eval_binding)
    binding = train.eval_binding(CHECKPOINT, {"identity": "cpu-fixture"}, 5)
    assert binding["step"] == 5
    assert binding["fixed_primary_step"] == 32
    assert binding["root"]["adapter"] == str(CHECKPOINT)
    assert binding["training_ready_identity"] == "cpu-fixture"
    assert binding["child"]["adapter"] is None
