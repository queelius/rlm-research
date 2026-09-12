"""Correct the isolated-node prefix diagnostic using actual complete causal chains."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
RUN = STORE / "sidecars/root-qs6-recursion-interface-qualifier-v1"
SOURCE = ROOT.parent / "mrcr-root-only-update-preflight-2026-09-12/extract_inputs.py"
EXPECTED = "0f163af566b4bd360523733790f037c33d802be39c67d1cc9256248438d2ff02"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


if __name__ == "__main__":
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or sha(SOURCE) != EXPECTED:
        raise ValueError("CPU-only exact reviewed extractor required")
    spec = importlib.util.spec_from_file_location("reviewed_causal_prefix_extractor", SOURCE)
    extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extractor)
    ready = read(RUN / "READY.json")
    for name, expected in ready["closure_sha256"].items():
        if sha(Path(name)) != expected:
            raise ValueError("sealed qualifier source changed: " + name)
    prefixes = {row["id"]: row["token_ids"] for row in read(RUN / "PREFIXES.json")["coordinates"]}
    outcomes = []
    for block_index, mode in enumerate(ready["science"]["block_order"]):
        for identifier in ready["plan_ids"][block_index]:
            path = RUN / f"outputs/attempt-001/blocks/{block_index:02d}-{mode}/collection/rollout/episodes/{identifier}.json"
            trace = read(path)["traces"][0]
            failed = [call for call in trace["calls"] if not isinstance(call.get("node"), int)]
            if any(not call.get("error") for call in failed):
                raise ValueError("unexplained call without sampled node")
            completed_trace = {**trace, "calls": [call for call in trace["calls"] if isinstance(call.get("node"), int)]}
            turns = extractor.trace_turns(completed_trace)
            first = turns[0]
            outcomes.append({
                "mode": mode, "coordinate_id": identifier, "episode_sha256": sha(path),
                "first_causal_prefix_matches": first["prompt_ids"] == prefixes[identifier],
                "expected_prefix_tokens": len(prefixes[identifier]),
                "reconstructed_prefix_tokens": len(first["prompt_ids"]),
                "calls": len(turns), "failed_calls_without_sampled_node": len(failed),
                "all_call_usage_lengths_match": all(t["usage_matches"] for t in turns),
                "root_calls": sum(t["depth"] == 0 for t in turns),
                "child_calls": sum(t["depth"] > 0 for t in turns),
            })
    report = {
        "schema": "root-interface-causal-prefix-addendum-v1",
        "source_sha256": sha(Path(__file__)), "extractor_sha256": EXPECTED,
        "ready_sha256": sha(RUN / "READY.json"), "prefixes_sha256": sha(RUN / "PREFIXES.json"),
        "original_report_sha256": sha(ROOT / "REPORT.json"),
        "rows": outcomes, "planned": 12,
        "prefixes_matched": sum(r["first_causal_prefix_matches"] for r in outcomes),
        "calls": sum(r["calls"] for r in outcomes),
        "failed_calls_without_sampled_node": sum(r["failed_calls_without_sampled_node"] for r in outcomes),
        "all_calls_usage_match": all(r["all_call_usage_lengths_match"] for r in outcomes),
        "effect_on_science": "None: correctness, repeated-action gate and faithful-computation caveats unchanged",
    }
    with (ROOT / "PREFIX_ADDENDUM.json").open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print({key: value for key, value in report.items() if key != "rows"})
