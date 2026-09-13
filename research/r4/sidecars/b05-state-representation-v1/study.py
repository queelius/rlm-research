"""Three-view frozen public-state representation screen."""

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / "b05-public-normalization-fresh12-v1"
spec = importlib.util.spec_from_file_location("b05_state_repr_prior", PRIOR / "study.py")
prior = importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
for name in ("read","sha","digest","write_x","bytes_x","now","load","aliases","tokenizer",
             "renderer","request_body","decode_response","base_owner","call_id","MUSIQUE","MODEL",
             "MODEL_ALIAS","NATIVE","SOURCE","TRAIN","source"):
    globals()[name] = getattr(prior, name)
normalize = prior.normalize
represent = load("b05_state_repr_runtime_transform", ROOT / "represent.py")
ATTEMPT = ROOT / "outputs/attempt-001"
READY_RUN = ROOT / "READY.json"
INPUTS = ROOT / "PUBLIC_INPUTS.json"
HOST = ROOT / "HOST_GOLD.json"
OWNER_SECONDS, SCIENCE_SECONDS, EXTERNAL_SECONDS = 1000, 900, 1100
MAX_PHYSICAL, CONCURRENCY = 72, 4


def calls():
    return read(INPUTS)["calls"]


def verify():
    ready = read(READY_RUN)
    assert ready["identity"] == digest({key: value for key, value in ready.items() if key != "identity"})
    for path, expected in ready["closure_sha256"].items():
        assert sha(path) == expected, path
    terminal = read(PRIOR / "outputs/attempt-001/OWNER_TERMINAL.json")
    assert all(terminal[key] for key in ("complete", "released", "runtime_qualified"))
    assert len(calls()) == 72 and len(read(INPUTS)["tasks"]) == 12
    assert len({call_id(call) for call in calls()}) == 72
    return ready

