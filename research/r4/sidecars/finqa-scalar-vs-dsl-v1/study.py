"""Frozen FinQA16 paired32 bindings, same qualified B05V3 native service."""
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "b05-recombination-feasibility-v1"
spec = importlib.util.spec_from_file_location("finqa_native_source_study", SOURCE / "runner_study.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
for name in ("read", "sha", "digest", "write_x", "bytes_x", "now", "load", "aliases", "tokenizer", "renderer",
             "request_body", "decode_response", "base_owner", "call_id", "MUSIQUE", "MODEL", "MODEL_ALIAS", "NATIVE"):
    globals()[name] = getattr(source, name)
REV = "0f16e2867befa6840783e58be38c9efb9229d742"
DATA = Path("/project/alex_phd/research-cache/repos") / ("FinQA-"+REV) / "dataset/dev.json"
ATTEMPT = ROOT / "outputs/attempt-001"
READY_RUN = ROOT / "CPU_READY.json"
INPUTS = ROOT / "PUBLIC_INPUTS.json"
HOST = ROOT / "HOST_TARGETS.json"
OWNER_SECONDS, SCIENCE_SECONDS, EXTERNAL_SECONDS = 700, 600, 800
MAX_PHYSICAL, CONCURRENCY = 32, 4
SOURCE_READY = SOURCE / "READY_RUN_V3.json"
SOURCE_READY_SHA = "b534d80731de70cc250ec4138204a177629cfb19ded6b5a1b637345d964acee8"


def calls():
    return read(INPUTS)["calls"]


def verify():
    ready = read(READY_RUN)
    assert ready["identity"] == digest({key: value for key,value in ready.items() if key != "identity"})
    for path, expected in ready["closure_sha256"].items():
        assert sha(Path(path)) == expected, path
    assert len(calls()) == MAX_PHYSICAL
    assert sha(SOURCE_READY) == SOURCE_READY_SHA
    terminal = read(SOURCE / "outputs/attempt-003/OWNER_TERMINAL.json")
    assert terminal["complete"] and terminal["released"] and terminal["runtime_qualified"]
    return ready
