"""Unchanged authenticated original trainer, all generations1–8 with new ROOT/SEED."""
import argparse
import json
import traceback
import uuid

import campaign_common as c

trainer = c.private("independent_seed_trainer_original", c.OLD / "campaign_train.py")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=c.Path, required=True)
    parser.add_argument("--generation", type=c.Path, required=True)
    parser.add_argument("--output", type=c.Path)
    parser.add_argument("--deadline", type=float, default=float("inf"))
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(trainer.train(args), sort_keys=True, allow_nan=False))
    except BaseException as error:
        if args.output is not None:
            c.write_once(args.output.parent / ("TRAIN_FAILURE-" + uuid.uuid4().hex + ".json"),
                {"type": type(error).__name__, "error": str(error), "traceback": traceback.format_exc(), "checkpoint_preserved": True})
        raise


if __name__ == "__main__":
    main()
