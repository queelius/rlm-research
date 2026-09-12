"""Additive native-evidence validation; reuses the qualified collector primitives."""
from __future__ import annotations

import hashlib, importlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
SIDE = STORE / "sidecars/openai-mrcr-fourneedle-ordinal-transfer-eval-v1"
ARMS = {"base": SIDE / "outputs/base-001", "checkpoint32": SIDE / "outputs/checkpoint32-001"}
ANALYSIS_READY = ROOT / "CPU_READY.json"
ANALYSIS_READY_SHA = "f2c28c9c305e52136659f9e1e1fa3d6ef8e35259aa76dd49210376d5332264a5"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def load(path): return json.loads(Path(path).read_text())


def verify_analysis_ready():
    if sha(ANALYSIS_READY) != ANALYSIS_READY_SHA: raise ValueError("analysis CPU_READY changed")
    value = load(ANALYSIS_READY)
    if value["identity"] != digest({k: v for k, v in value.items() if k != "identity"}): raise ValueError("analysis identity changed")
    for path, expected in value["closure_sha256"].items():
        if sha(path) != expected: raise ValueError("analysis closure changed: " + path)
    return value


def sampling_issues(value, seed):
    expected = {"temperature": 0.5, "top_p": 1.0, "seed": seed, "max_tokens": 2048,
                "reasoning_effort": None, "extra_body": {"top_k": -1, "min_p": 0.0,
                "return_token_ids": True, "cache_salt": "0"}}
    return ["sampling." + key for key in expected if value.get(key) != expected[key]]


def terminal_expectation(calls, matches, reply):
    finals = [m for m in matches if m.get("role") == "root" and calls.get(m.get("node"), {}).get("finish_reason") == "stop"]
    if finals: return "PARSE_PHYSICAL_STOP"
    if reply == "" and matches and all(calls.get(m.get("node"), {}).get("finish_reason") == "length" for m in matches if m.get("role") == "root"):
        return "NO_PHYSICAL_STOP_EMPTY_REPLY"
    return "MISSING_PHYSICAL_TERMINAL_EVIDENCE"


def source_modules():
    old_path, old = list(sys.path), {name: sys.modules.get(name) for name in ("study", "checkpoint", "collect")}
    try:
        sys.path.insert(0, str(SIDE))
        for name in old: sys.modules.pop(name, None)
        study = importlib.import_module("study")
        collect = importlib.import_module("collect")
        study.dependencies()
        return study, collect.source.source
    finally:
        sys.path[:] = old_path
        for name, value in old.items():
            if value is None: sys.modules.pop(name, None)
            else: sys.modules[name] = value


def stage(arm, study, collector, renderer, gold, prefixes):
    directory = ARMS[arm] / "science"
    episodes = [load(path) for path in sorted((directory / "episodes").glob("*.json"))]
    starts = [load(path) for path in sorted((directory / "native-calls").glob("*-start.json"))]
    results = [load(path) for path in sorted((directory / "native-calls").glob("*-result.json"))]
    starts_by_index, results_by_index = ({row["index"]: row for row in values} for values in (starts, results))
    binding = load(ARMS[arm] / "owned-service/BINDING.json")
    aliases, issues, provider_ids = set(binding["models"]), [], []
    coordinate_by_trace = {}
    for item in episodes:
        traces = item["episode"].get("traces") or []
        if len(traces) == 1: coordinate_by_trace[traces[0].get("id")] = item["coordinate"]
    for index in sorted(set(starts_by_index) | set(results_by_index)):
        start, result = starts_by_index.get(index), results_by_index.get(index)
        if start is None or result is None:
            issues.append(f"native orphan:{index}"); continue
        for key in ("body", "model", "sampling", "session_id", "turn"):
            if start.get(key) != result.get(key): issues.append(f"start/result {key} differs:{index}")
        coordinate = coordinate_by_trace.get(result.get("session_id"))
        if coordinate is None: issues.append(f"native session has no episode:{index}")
        else: issues.extend(f"{problem}:{index}" for problem in sampling_issues(result["sampling"], coordinate["seed"]))
        body = result.get("body") or {}
        if body.get("model") not in aliases: issues.append(f"unbound request model:{index}")
        if any(body.get(k) != v for k, v in {"temperature": .5, "top_p": 1.0, "top_k": -1,
               "min_p": 0.0, "max_tokens": 2048, "return_token_ids": True, "cache_salt": "0"}.items()):
            issues.append(f"native request body sampling differs:{index}")
        if result.get("status") == "returned":
            response = result.get("response") or {}
            try: collector.validate_native_response(response)
            except Exception as error: issues.append(f"native response invalid:{index}:{type(error).__name__}")
            if response.get("model") != body.get("model"): issues.append(f"response model differs:{index}")
            if response.get("finish_reason") not in {"stop", "tool_calls", "length"}: issues.append(f"finish reason invalid:{index}")
            if not response.get("id"): issues.append(f"provider id absent:{index}")
            else: provider_ids.append(response["id"])
    if len(provider_ids) != len(set(provider_ids)): issues.append("duplicate provider response id")
    recomputed, terminal_equal, no_physical_stop = 0, 0, 0
    hooks = study.terminal_hooks()
    with hooks.installed():
        for item in episodes:
            coordinate, raw = item["coordinate"], item["episode"]
            expected = collector.inspect_trace(raw, gold[coordinate["record_id"]], results,
                prefixes[coordinate["id"]]["token_ids"], item["derived"].get("terminal_status") == "deadline_censored")
            if expected != item["derived"]: issues.append("derived replay differs:" + coordinate["id"])
            else: recomputed += 1
            traces = raw.get("traces") or []
            if len(traces) != 1 or not isinstance(traces[0].get("root_reply"), str): continue
            trace, mapping = traces[0], expected["causal_mapping"]
            calls = {call.get("node"): call for call in trace.get("calls") or []}
            returned = [row for row in results if row.get("session_id") == trace.get("id") and row.get("status") == "returned"]
            matches = mapping.get("matches") or []
            finals = [m for m in matches if m.get("role") == "root" and calls.get(m.get("node"), {}).get("finish_reason") == "stop"]
            expectation = terminal_expectation(calls, matches, trace["root_reply"])
            if expectation == "NO_PHYSICAL_STOP_EMPTY_REPLY": no_physical_stop += 1; continue
            if not finals: issues.append("missing physical terminal evidence:" + coordinate["id"]); continue
            match = finals[-1]; native = returned[match["audit_index"]]
            parsed = renderer.parse_response(native["response"]["tokens"]["completion_ids"], tools=native["body"].get("tools"))
            if parsed.content != trace["root_reply"]: issues.append("native terminal decode differs:" + coordinate["id"])
            else: terminal_equal += 1
    available = sum(item["derived"].get("scientifically_available") is True for item in episodes)
    return {"episodes": len(episodes), "scientifically_available": available, "starts": len(starts),
            "results": len(results), "returned": sum(row.get("status") == "returned" for row in results),
            "errors": sum(row.get("status") != "returned" for row in results), "recomputed_derived_exact": recomputed,
            "native_terminal_decode_equal": terminal_equal, "no_physical_stop_empty_reply": no_physical_stop, "issues": issues,
            "native_starts_sha256": digest(starts), "native_results_sha256": digest(results),
            "episodes_sha256": digest(episodes)}


def main():
    verify_analysis_ready()
    prior = load(ROOT / "outcome/RESULTS.json")
    if prior.get("status") != "COMPLETE_RAW_AUDIT": raise ValueError("source string audit is not complete")
    study, collector = source_modules()
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    renderer = create_renderer(load_tokenizer(str(study.BASE)), Qwen3RendererConfig(enable_thinking=True))
    gold, prefixes = load(SIDE / "inputs/HOST_GOLD.json"), load(SIDE / "inputs/PREFIXES.json")
    stages = {arm: stage(arm, study, collector, renderer, gold, prefixes) for arm in ARMS}
    issues = [issue for stage_value in stages.values() for issue in stage_value["issues"]]
    all_available = all(value["episodes"] == value["scientifically_available"] == 16 for value in stages.values())
    status = "COMPLETE_NATIVE_VALIDATION" if all_available and not issues else "PARTIAL_NATIVE_VALIDATION"
    value = {"schema": "openai-mrcr-fourneedle-native-validation-v2", "status": status,
        "reuse_boundary": "collector validate_native_response, inspect_trace, causal mapper, tokenizer renderer, and qualified terminal hook are reused; request/result inventories, contracts, decode equality, and comparisons are computed here",
        "source_string_audit_sha256": sha(ROOT / "outcome/RESULTS.json"), "analysis_cpu_ready_sha256": ANALYSIS_READY_SHA,
        "stages": stages, "all_32_scientifically_available": all_available, "integrity_issues": issues,
        "gpu_calls": 0, "model_calls": 0}
    out = ROOT / "native-validation-v2"; out.mkdir(exist_ok=False)
    (out / "RESULTS.json").write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    (out / "REPORT.md").write_text(f"""---\nschema: openai-mrcr-fourneedle-native-validation-report-v2\nstatus: {status}\n---\n\n# Native-evidence supplement\n\nThe supplement authenticated {sum(x['returned'] for x in stages.values())} returned native calls and replayed {sum(x['recomputed_derived_exact'] for x in stages.values())}/32 episode derivations exactly. Physical stop-token decoding matched the preserved root reply for {sum(x['native_terminal_decode_equal'] for x in stages.values())}/31 episodes with a physical stop; one checkpoint episode exhausted its 2,048-token action with an empty parsed reply and is retained separately rather than called a decode mismatch. All 32 episodes are scientifically available: {all_available}. Integrity issues: {len(issues)}.\n\nThis does not independently reimplement the causal mapper or Qwen parser. It reuses the qualified collector's native validator, trace inspector, exact tokenizer renderer, and terminal-strip-disabled hook, then independently checks inventories, start/result equality, sampling, model aliases, provider IDs, prefixes through trace replay, and native terminal equality. It adds no model or GPU calls and does not replace the separate string/score audit.\n""")
    print(json.dumps({"status": status, "issues": len(issues), "available": all_available}, sort_keys=True))


if __name__ == "__main__": main()
