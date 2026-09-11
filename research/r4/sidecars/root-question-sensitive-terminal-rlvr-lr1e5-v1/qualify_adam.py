"""Tiny real CPU AdamW two-step restore and wrong-LR rejection proof."""
from pathlib import Path
import random

import torch

import lr_study as study
import lr_train as train
import terminal_common as common


def optimizer_step(optimizer):
    return int(next(iter(optimizer.state.values()))["step"])


def run():
    output = study.ROOT / "qualification-adam"
    output.mkdir(exist_ok=False)
    recipe = study.read(study.ROOT / "RECIPE.json")
    parameter = torch.nn.Parameter(torch.tensor([1.0], dtype=torch.float32))
    first = torch.optim.AdamW([parameter], lr=recipe["learning_rate"],
                              weight_decay=recipe["weight_decay"])
    parameter.grad = torch.tensor([0.25])
    first.step()
    checkpoint = output / "checkpoint-1"
    checkpoint.mkdir()
    torch.save(first.state_dict(), checkpoint / "optimizer.pt")
    torch.save({"python": random.getstate(), "torch": torch.get_rng_state(), "cuda": []},
               checkpoint / "rng_state.pt")
    study.write(checkpoint / "state.json", {"optimizer_parameter_names": ["weight"]})
    policy = {"step": 1, "path": str(checkpoint)}
    original_authenticate = common.c.authenticate_policy
    common.c.authenticate_policy = lambda _policy: True
    try:
        second = torch.optim.AdamW([parameter], lr=recipe["learning_rate"],
                                   weight_decay=recipe["weight_decay"])
        train.restore_optimizer(second, policy, ["weight"])
        if optimizer_step(second) != 1:
            raise ValueError("restored cursor is not one")
        parameter.grad = torch.tensor([0.25])
        second.step()
        if optimizer_step(second) != 2:
            raise ValueError("second Adam step did not advance")

        wrong = torch.optim.AdamW([parameter], lr=5e-5, weight_decay=0.0)
        parameter.grad = torch.tensor([0.25])
        wrong.step()
        torch.save(wrong.state_dict(), checkpoint / "optimizer.pt")
        rejected = None
        try:
            target = torch.optim.AdamW([parameter], lr=recipe["learning_rate"],
                                       weight_decay=recipe["weight_decay"])
            train.restore_optimizer(target, policy, ["weight"])
        except ValueError as error:
            rejected = str(error)
        if not rejected:
            raise ValueError("wrong 5e-5 restored state was accepted")
    finally:
        common.c.authenticate_policy = original_authenticate
    result = {"status": "PASS", "real_torch_adamw": True, "restored_step": 1,
              "advanced_step": 2, "learning_rate": recipe["learning_rate"],
              "wrong_5e5_rejected": True, "rejection": rejected, "gpu_calls": 0}
    study.write(output / "RESULT.json", result)
    return result


if __name__ == "__main__":
    print(run())
