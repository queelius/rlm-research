"""Training-environment entry for the generic sparse continuation trainer."""
import continuation_study_v2 as study
import continuation_train as base

base.study = study

parse_args = base.parse_args
impl = base.impl


def runtime_preflight():
    import accelerate
    import peft
    import torch
    import transformers
    if not study.TRAIN.exists():
        raise ValueError("qualified training Python absent")
    return {"torch": torch.__version__, "transformers": transformers.__version__,
            "peft": peft.__version__, "accelerate": accelerate.__version__,
            "sparse_math": str(base.sparse_math.__file__), "optimizer_steps": 0}


def run(args):
    study.verify_prepared()
    group, generation, identity = study.source_train.authenticate_group(
        args.group.resolve(), args.generation.resolve())
    if generation["candidate_window"] not in range(4, 9):
        raise ValueError("only frozen remaining windows4..8")
    if __import__("pathlib").Path(generation["previous_policy"]["path"]).resolve() != args.checkpoint.resolve():
        raise ValueError("generation/checkpoint path mismatch")
    if args.preflight:
        return {"input_identity": identity["input_identity"], "episodes": len(group["episodes"]),
                "candidate_window": generation["candidate_window"], "sparse_head": True,
                "runtime": runtime_preflight()}
    return impl.train(args)


if __name__ == "__main__":
    import json
    arguments = parse_args()
    print(json.dumps(run(arguments), sort_keys=True, allow_nan=False))
