"""Exact failed update-2 trainer with only sparse credited-position LM-head projection."""
import argparse
import json
from pathlib import Path
import sys
import types

import sparse_math
import sparse_study as study

sys.path.insert(0, str(study.SOURCE))
import terminal_common as common  # noqa: E402
import terminal_train as original  # noqa: E402

SOURCE = study.SIDE / "root-rlvr-campaign-v1/campaign_train.py"
study.check(SOURCE, study.PINS[SOURCE])
text = SOURCE.read_text()
changes = {
    "        for index, turn in enumerate(episode[\"turns\"]):\n            ids =":
        "        for index, turn in enumerate(episode[\"turns\"]):\n            turn_started = time.monotonic()\n            ids =",
    "result = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False)":
        "positions = torch.tensor(sparse_math.position_list(turn), dtype=torch.long, device=model.device)\n"
        "            result = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, logits_to_keep=positions)",
    "loss, capture = tis.tis_action_loss(result.logits, turn, advantage=episode[\"advantage\"], temperature=recipe[\"temperature\"]):": "",
}
# The loss replacement is kept separate because it is long and must occur exactly once.
bad_key = next(iter([key for key in changes if key.endswith('):')]), None)
if bad_key is not None:
    changes.pop(bad_key)
loss_before = 'loss, capture = tis.tis_action_loss(result.logits, turn, advantage=episode["advantage"], temperature=recipe["temperature"])'
loss_after = 'loss, capture = sparse_math.selected_tis_loss(result.logits, turn, advantage=episode["advantage"], temperature=recipe["temperature"], tis=tis)'
capture_before = '"role_depth": 0, "loss_weight": weight, "loss": float(loss.detach().cpu())})'
capture_after = '"role_depth": 0, "loss_weight": weight, "loss": float(loss.detach().cpu()),\n                "sequence_tokens": len(turn["input_ids"]), "selected_positions": len(positions),\n                "turn_seconds": time.monotonic() - turn_started})'
for before, after in {**changes, loss_before: loss_after, capture_before: capture_after}.items():
    if text.count(before) != 1:
        raise ValueError("qualified sparse trainer seam changed: " + before[:80])
    text = text.replace(before, after)
if text.count('recipe["training_wall_cap_seconds"]') != 2:
    raise ValueError("qualified trainer cap seam changed")
text = text.replace('recipe["training_wall_cap_seconds"]', "1800")

impl = types.ModuleType("sparse_qualified_campaign_train")
impl.__file__ = str(SOURCE)
impl.sparse_math = sparse_math
sys.modules[impl.__name__] = impl
with study.aliases({"campaign_common": common.c}):
    exec(compile(text, str(SOURCE) + ":sparse-head-update2", "exec"), impl.__dict__)
impl.authenticate_group = original.authenticate_group


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--generation", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--deadline", type=float, required=True)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    if args.group.resolve() != study.GROUP.resolve() or args.generation.resolve() != study.GENERATION.resolve():
        raise ValueError("exact frozen failed group/generation only")
    if args.checkpoint.resolve() != study.CHECKPOINT.resolve():
        raise ValueError("exact checkpoint1 only")
    return args


def run(args):
    study.verify_inputs()
    group, generation, identity = original.authenticate_group(args.group, args.generation)
    if generation["previous_policy"]["path"] != str(args.checkpoint.resolve()):
        raise ValueError("generation/checkpoint path mismatch")
    if args.preflight:
        return {"input_identity": identity["input_identity"], "episodes": len(group["episodes"]), "sparse_head": True}
    return impl.train(args)


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(run(args), sort_keys=True, allow_nan=False))

