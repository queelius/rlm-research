"""Fixed child-only bindings; comparator must be qualified source-visible V3."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "b05-recombination-feasibility-v1"
spec = importlib.util.spec_from_file_location("ids_interface_original_study", SOURCE / "runner_study.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
for name in ("read", "sha", "digest", "write_x", "bytes_x", "now", "load", "aliases", "tokenizer", "renderer",
             "request_body", "decode_response", "active_roots", "base_owner", "canonical_json", "call_id",
             "MUSIQUE", "MODEL", "MODEL_ALIAS", "NATIVE"):
    globals()[name] = getattr(source, name)
ATTEMPT = ROOT / "outputs/attempt-001"
READY_RUN = ROOT / "READY_RUN.json"
BASELINE = SOURCE / "outputs/attempt-003"
BASELINE_READY = SOURCE / "READY_RUN_V3.json"
BASELINE_READY_SHA = "b534d80731de70cc250ec4138204a177629cfb19ded6b5a1b637345d964acee8"
OWNER_SECONDS, SCIENCE_SECONDS, EXTERNAL_SECONDS = 700, 600, 800
MAX_PHYSICAL, CONCURRENCY = 24, 4


def calls():
    return [call for call in source.calls() if call["kind"] == "child"]


def b05():
    import interface
    return interface


def qualify_baseline():
    assert sha(BASELINE_READY) == BASELINE_READY_SHA
    terminal = read(BASELINE / "OWNER_TERMINAL.json")
    result = read(BASELINE / "RESULT.json")
    assert terminal["complete"] and terminal["released"] and terminal["runtime_qualified"]
    assert result["complete"] and result["released"] and result["runtime_qualified"]
    assert terminal["result_sha256"] == sha(BASELINE / "RESULT.json")
    run = read(BASELINE / "OWNER_RUN.json")
    assert run["ready_sha256"] == BASELINE_READY_SHA
    for call in calls():
        record = read(BASELINE / "calls" / (call_id(call)+".json"))
        assert record["physical_started"] and record["transport_valid"]
        assert all(record[key] == value for key, value in call.items())
    return terminal


def verify():
    ready = read(READY_RUN)
    assert ready["identity"] == digest({key: value for key, value in ready.items() if key != "identity"})
    for path, expected in ready["closure_sha256"].items():
        assert sha(Path(path)) == expected, path
    qualify_baseline()
    assert len(calls()) == 24 and len(active_roots()) == 4
    return ready
