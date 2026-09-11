"""Second additive completion: exact missing gate input, same immutable corpus/science."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
V1 = ROOT.parent / "root-question-sensitive-sft-new-corpus-completion-v1"
_spec = importlib.util.spec_from_file_location("new_corpus_completion_v1", V1 / "recovery.py")
base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = base
sys.path.insert(0, str(V1))
_spec.loader.exec_module(base)
if base.s.sha(V1 / "recovery.py") != "6a4384b0745cda3021fb899423acd4215e06c9f17cc93717296d85f8a834d48f":
    raise ValueError("completion v1 recovery changed")

ATTEMPT = ROOT / "outputs/attempt-001"
base.ROOT = ROOT
base.ATTEMPT = ATTEMPT
base.binding_module.cache_clear()
base.readout_study.cache_clear()

s = base.s
BUDGET = base.BUDGET
SOURCE = base.SOURCE
SOURCE_ATTEMPT = base.SOURCE_ATTEMPT
source_corpus_receipt = base.source_corpus_receipt
binding_module = base.binding_module
readout_study = base.readout_study
dependencies = base.dependencies
remaining = base.remaining
gpu_command = base.gpu_command
collector_argv = base.collector_argv
selected = base.selected


def training_argv(output, deadline):
    return [str(s.TRAIN), str(ROOT / "train_v2.py"), "train", "--output",
            str(Path(output) / "training"), "--deadline", str(float(deadline))]


def verify():
    ready = s.read(ROOT / "READY.json")
    if s.digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("completion v2 READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if s.sha(path) != pin:
            raise ValueError("completion v2 closure changed: " + path)
    source_corpus_receipt()
    gate = s.read(ROOT / "inputs/GATE_PLAN.json")
    corpus_ids = {row["episode_id"] for row in s.corpus()}
    if len(gate) != 6 or any(row["id"] not in corpus_ids for row in gate):
        raise ValueError("exact gate must be inside complete72 corpus")
    return ready


base.ROOT = ROOT
base.ATTEMPT = ATTEMPT
base.verify = verify
