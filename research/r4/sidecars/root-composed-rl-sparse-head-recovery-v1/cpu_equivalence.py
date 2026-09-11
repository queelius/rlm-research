"""CPU-only tiny Qwen3 full-vs-selected logits/loss/gradient qualification."""
import json
import os

if os.environ.get("CUDA_VISIBLE_DEVICES", ""):
    raise ValueError("CPU fixture forbids visible CUDA")

import torch
from transformers import Qwen3Config, Qwen3ForCausalLM

import sparse_math


class TinyTIS:
    @staticmethod
    def tis_action_loss(logits, turn, *, advantage, temperature):
        prompt, count = turn["prompt_length"], len(turn["old_logprobs"])
        action = logits[:, prompt - 1 : prompt - 1 + count, :].float() / temperature
        target = torch.tensor([turn["input_ids"][prompt:]], device=logits.device)
        current = torch.log_softmax(action, -1).gather(-1, target.unsqueeze(-1)).reshape(-1)
        proximal = current.detach()
        rollout = torch.tensor(turn["old_logprobs"], device=logits.device)
        weights = (proximal - rollout).exp().clamp(max=2).detach()
        ratio = (current - proximal).exp()
        loss = -(weights * torch.minimum(ratio * advantage, ratio.clamp(.8, 1.2) * advantage)).mean()
        return loss, {"hf_old_logprobs": proximal}


def run():
    torch.manual_seed(731)
    config = Qwen3Config(vocab_size=97, hidden_size=32, intermediate_size=64,
                         num_hidden_layers=2, num_attention_heads=4,
                         num_key_value_heads=2, head_dim=8, max_position_embeddings=64)
    model = Qwen3ForCausalLM(config).to(dtype=torch.float32)
    ids = torch.tensor([[2, 7, 5, 11, 13, 17, 19, 23, 29]], dtype=torch.long)
    turn = {"input_ids": ids[0].tolist(), "prompt_length": 5,
            "old_logprobs": [-4.0] * 4}
    full = model(input_ids=ids, use_cache=False).logits
    loss_full, capture_full = TinyTIS.tis_action_loss(full, turn, advantage=.75, temperature=.5)
    loss_full.backward()
    grad_full = {name: p.grad.detach().clone() for name, p in model.named_parameters() if p.grad is not None}
    model.zero_grad(set_to_none=True)
    positions = torch.tensor(sparse_math.position_list(turn), dtype=torch.long)
    selected = model(input_ids=ids, use_cache=False, logits_to_keep=positions).logits
    loss_selected, capture_selected = sparse_math.selected_tis_loss(
        selected, turn, advantage=.75, temperature=.5, tis=TinyTIS)
    loss_selected.backward()
    grad_selected = {name: p.grad.detach().clone() for name, p in model.named_parameters() if p.grad is not None}
    result = {
        "schema": "root-composed-rl-sparse-head-cpu-equivalence-v1",
        "device": str(ids.device),
        "full_positions": full.shape[1],
        "selected_positions": selected.shape[1],
        "loss_close": torch.allclose(loss_full, loss_selected, rtol=1e-6, atol=1e-7),
        "logprobs_close": torch.allclose(capture_full["hf_old_logprobs"], capture_selected["hf_old_logprobs"], rtol=1e-6, atol=1e-7),
        "gradients_close": grad_full.keys() == grad_selected.keys() and all(
            torch.allclose(grad_full[name], grad_selected[name], rtol=2e-5, atol=2e-6)
            for name in grad_full),
        "max_gradient_absolute_difference": max(
            float((grad_full[name] - grad_selected[name]).abs().max()) for name in grad_full),
    }
    if not all(result[k] for k in ("loss_close", "logprobs_close", "gradients_close")):
        raise ValueError("tiny Qwen3 selected-position objective differs")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, allow_nan=False))
