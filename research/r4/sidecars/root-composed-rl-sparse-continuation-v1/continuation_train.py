"""Generic sparse credited-position trainer for authenticated source GROUP/GENERATION pairs."""
import argparse
import json
import sys
import types
from pathlib import Path

import continuation_study as study

sys.path.insert(0, str(study.SPARSE_V1))
import sparse_math  # noqa: E402

source = study.SIDE / "root-rlvr-campaign-v1/campaign_train.py"
text = source.read_text()
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
}
for before, after in changes.items():
    if text.count(before) != 1:
        raise ValueError("qualified sparse seam changed: " + before[:80])
    text = text.replace(before, after)
if text.count('recipe["training_wall_cap_seconds"]') != 2:
    raise ValueError("qualified trainer cap seam changed")
text = text.replace('recipe["training_wall_cap_seconds"]', "1800")
impl = types.ModuleType("continuation_sparse_campaign_train")
impl.__file__ = str(source)
impl.sparse_math = sparse_math
sys.modules[impl.__name__] = impl
with study.source_study.aliases({"campaign_common": study.common.c}):
    exec(compile(text, str(source) + ":generic-sparse-head", "exec"), impl.__dict__)
impl.authenticate_group = study.source_train.authenticate_group


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--generation", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    parser.add_argument("--preflight", action="store_true")
    return parser.parse_args(argv)


def run(args):
    study.verify_prepared()
    group, generation, identity = study.source_train.authenticate_group(
        args.group.resolve(), args.generation.resolve())
    if generation["candidate_window"] not in range(4, 9):
        raise ValueError("only frozen remaining windows4..8")
    if Path(generation["previous_policy"]["path"]).resolve() != args.checkpoint.resolve():
        raise ValueError("generation/checkpoint path mismatch")
    if args.preflight:
        return {"input_identity": identity["input_identity"], "episodes": len(group["episodes"]),
                "candidate_window": generation["candidate_window"], "sparse_head": True}
    return impl.train(args)


if __name__ == "__main__":
    arguments = parse_args()
    print(json.dumps(run(arguments), sort_keys=True, allow_nan=False))
