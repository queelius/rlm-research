"""Qualified trainer with an explicit, frozen new-corpus gate-plan root."""
import json
from pathlib import Path
import sys

import recovery as r

sys.path.insert(0, str(r.SOURCE))
import qs_train as qualified  # noqa: E402


class Study:
    ROOT = r.ROOT
    ATTEMPT = r.SOURCE_ATTEMPT
    verify = staticmethod(r.s.verify)
    corpus = staticmethod(r.s.corpus)
    def __getattr__(self, name):
        return getattr(r.s, name)


study = Study()


def input_receipt():
    episodes = study.corpus()
    ids = {row["episode_id"] for row in episodes}
    gate = study.read(study.ROOT / "inputs/GATE_PLAN.json")
    valid = len(gate) == 6 and all(row["id"] in ids for row in gate)
    if not valid:
        raise ValueError("gate/corpus binding")
    return {"corpus": len(episodes), "gate": len(gate), "gate_ids_in_corpus": valid}


def train(argv):
    input_receipt()
    qualified.s = study
    qualified.implementation.cache_clear()
    module = qualified.implementation()
    module.s = study
    args = module.parse_args(argv)
    module.run(args)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "verify-inputs":
        print(json.dumps(input_receipt(), sort_keys=True))
    elif len(sys.argv) >= 2 and sys.argv[1] == "train":
        train(sys.argv[2:])
    else:
        raise SystemExit("usage: train_v2.py verify-inputs | train --output PATH --deadline EPOCH")
