"""Recompute the saved structural-preview readout; never execute generated code."""

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
SIDE = STORE / "sidecars/openai-mrcr-structural-preview-screen-v1"
SCIENCE = SIDE / "outputs/attempt-001/science"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def derive():
    ready_path = SIDE / "READY.json"
    if sha(ready_path) != "7a0fb4f45c0eecbebaae591f5668386a669a6aeb1b4c81fb45b9dbdcf88fe48d":
        raise ValueError("frozen study changed")
    ready = json.loads(ready_path.read_text())
    closure = ready["closure_sha256"]
    for path, expected in closure.items():
        if sha(path) != expected:
            raise ValueError("source changed: " + path)
    sys.path.insert(0, str(SIDE))
    import study
    import collect

    records = [study.read(p) for p in sorted((SCIENCE / "episodes").glob("*.json"))]
    native_paths = sorted((SCIENCE / "native-calls").glob("*-result.json"))
    native = [study.read(p) for p in native_paths]
    gold = study.read(SIDE / "inputs/HOST_GOLD.json")
    assert len(records) == 32 and len(native) == 79
    coordinates = {row["id"]: row for row in study.plan()}
    rows = []
    for record in records:
        coordinate = record["coordinate"]
        assert coordinates[coordinate["id"]] == coordinate
        raw = record["episode"]
        assert study.digest(raw) == record["episode_sha256"]
        derived = collect.inspect_trace(raw, gold[coordinate["record_id"]], native)
        assert derived == record["derived"]
        trace = raw["traces"][0]
        observations = [
            (node.get("message") or {}).get("content") or ""
            for node in trace["nodes"]
            if (node.get("message") or {}).get("role") == "tool"
        ]
        assert all(isinstance(value, str) for value in observations)
        code = derived["first_python"].get("code")
        rows.append({
            "coordinate": coordinate,
            "episode_sha256": record["episode_sha256"],
            "available": derived["scientifically_available"],
            "raw_exact": derived["root_reply"] == gold[coordinate["record_id"]]["answer"],
            "raw_official_similarity": derived["reward"],
            "first_python_category_heuristic": derived["first_python"]["category"],
            "first_python_sha256": hashlib.sha256(code.encode()).hexdigest() if code else None,
            "observation_bytes": sum(len(value.encode("utf-8")) for value in observations),
            "observation_characters": sum(map(len, observations)),
            "tool_tracebacks": sum("Traceback" in value for value in observations),
            "terminal_sha256": hashlib.sha256((derived["root_reply"] or "").encode()).hexdigest(),
        })
    summary = collect.summarize(records)
    saved = study.read(SCIENCE / "RESULT.json")
    assert all(saved[key] == value for key, value in summary.items())
    source_paths = [ready_path, SCIENCE / "RESULT.json", SIDE / "outputs/attempt-001/OWNER_TERMINAL.json", Path(__file__)]
    return {
        "schema": "mrcr-structural-preview-saved-readout-v1",
        "source_sha256": {str(p): sha(p) for p in source_paths},
        "episode_and_native_files_sha256": {str(p): sha(p) for p in [*sorted((SCIENCE / "episodes").glob("*.json")), *native_paths]},
        "summary": summary,
        "rows": rows,
        "observation_bytes_by_arm": {arm: sum(row["observation_bytes"] for row in rows if row["coordinate"]["arm"] == arm) for arm in ("no_preview", "structural_preview")},
        "scope": "Recomputed shared causal mapper and official raw-string scorer against saved episodes/native tokens; not an independently implemented native-wire auditor.",
        "generated_code_executed": False,
        "new_model_calls": 0,
        "heuristic_limit": "AST categories can misclassify guarded/reassigned variables; do not equate absence of detected top-level misuse with correct retrieval.",
    }


if __name__ == "__main__":
    result = derive()
    output = ROOT / "FINDINGS.json"
    if "--check" in sys.argv:
        assert json.loads(output.read_text()) == result
        print("Saved structural readout reproduces exactly")
    else:
        with output.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        print(json.dumps({"sha256": sha(output), "arms": result["summary"]["arm_summaries"]}))
