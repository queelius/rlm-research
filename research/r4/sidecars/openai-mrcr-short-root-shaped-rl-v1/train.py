"""Exact CLI for the transformed shaped24 trainer."""

import argparse
import json
from pathlib import Path

import trainer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap-seconds", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(trainer.module().run(args.output, args.cap_seconds), sort_keys=True))
