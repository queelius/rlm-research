"""Qualified sparse-head trainer for the exact fresh LR1e-5 campaign."""
import argparse
import json
import sys
import types
from pathlib import Path

import lr_study as study
import terminal_common as common
import terminal_train as source_train

sys.path.insert(0, str(study.SPARSE))
import sparse_math  # noqa: E402


def optimizer_group_hyperparameters(optimizer):
    return [{key: value for key, value in group.items() if key != "params"}
            for group in optimizer.param_groups]


def assert_optimizer_recipe(optimizer, recipe):
    for group in optimizer.param_groups:
        if group.get("lr") != recipe["learning_rate"]:
            raise ValueError("optimizer learning rate differs from LR1e-5 recipe")
        if group.get("weight_decay") != recipe["weight_decay"]:
            raise ValueError("optimizer weight decay differs from recipe")
    return True


SOURCE = study.SIDE / "root-rlvr-campaign-v1/campaign_train.py"
PIN = "38fe3087b8deb94ee8e0fa2e0330ca34a822f84192031c389ff32acf00d79d1f"
study.check(SOURCE, PIN)
text = SOURCE.read_text()
changes = {
    '        for index, turn in enumerate(episode["turns"]):\n            ids =':
        '        for index, turn in enumerate(episode["turns"]):\n            turn_started = time.monotonic()\n            ids =',
    'result = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False)':
        'positions = torch.tensor(sparse_math.position_list(turn), dtype=torch.long, device=model.device)\n'
        '            result = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, logits_to_keep=positions)',
    'loss, capture = tis.tis_action_loss(result.logits, turn, advantage=episode["advantage"], temperature=recipe["temperature"])':
        'loss, capture = sparse_math.selected_tis_loss(result.logits, turn, advantage=episode["advantage"], temperature=recipe["temperature"], tis=tis)',
    '"role_depth": 0, "loss_weight": weight, "loss": float(loss.detach().cpu())})':
        '"role_depth": 0, "loss_weight": weight, "loss": float(loss.detach().cpu()),\n'
        '                "sequence_tokens": len(turn["input_ids"]), "selected_positions": len(positions),\n'
        '                "turn_seconds": time.monotonic() - turn_started})',
    '"optimizer_parameter_names": [name for name, _ in trainable], "input_identity": input_identity,':
        '"optimizer_parameter_names": [name for name, _ in trainable],\n'
        '        "optimizer_group_hyperparameters": optimizer_group_hyperparameters(optimizer),\n'
        '        "input_identity": input_identity,',
}
for before, after in changes.items():
    if text.count(before) != 1:
        raise ValueError("qualified LR sparse seam changed: " + before[:80])
    text = text.replace(before, after)

impl = types.ModuleType("lr1e5_sparse_campaign_train")
impl.__file__ = str(SOURCE)
impl.sparse_math = sparse_math
impl.optimizer_group_hyperparameters = optimizer_group_hyperparameters
sys.modules[impl.__name__] = impl
with study.aliases({"campaign_common": common.c}):
    exec(compile(text, str(SOURCE) + ":lr1e5-sparse-head", "exec"), impl.__dict__)

_restore_optimizer = impl.restore_optimizer


def restore_optimizer(optimizer, policy, parameter_names):
    recipe = study.read(study.ROOT / "RECIPE.json")
    assert_optimizer_recipe(optimizer, recipe)
    _restore_optimizer(optimizer, policy, parameter_names)
    assert_optimizer_recipe(optimizer, recipe)


impl.restore_optimizer = restore_optimizer


def check_policy_namespace(policy, generation):
    path = Path(policy["path"]).resolve()
    if policy["step"] == 0:
        if path != study.CHECKPOINT.resolve() or policy.get("optimizer_sha256") is not None:
            raise ValueError("step0 must be exact QS6 with fresh Adam")
        return True
    attempt = study.ATTEMPT.resolve()
    if attempt not in path.parents:
        raise ValueError("foreign high-LR checkpoint path")
    if not 0 < policy["step"] < generation["candidate_window"]:
        raise ValueError("optimizer cursor incompatible with fixed candidate window")
    if path.name != f"checkpoint-{policy['step']}":
        raise ValueError("checkpoint path/cursor mismatch")
    return True


def authenticate_group(group_path, generation_path):
    group, generation, identity = source_train.authenticate_group(group_path, generation_path)
    policy = generation["previous_policy"]
    check_policy_namespace(policy, generation)
    return group, generation, identity


impl.authenticate_group = authenticate_group


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--generation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    parser.add_argument("--preflight", action="store_true")
    return parser.parse_args(argv)


def run(args):
    study.verify_prepared()
    return impl.train(args)


if __name__ == "__main__":
    arguments = parse_args()
    print(json.dumps(run(arguments), sort_keys=True, allow_nan=False))
