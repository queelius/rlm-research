"""Corrected native prefill treatment over the immutable qualification driver."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_qualification_baseline", ROOT / "driver.py")
baseline = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = baseline
_spec.loader.exec_module(baseline)
_make_context = baseline.make_context
_request_metadata = baseline.request_metadata
_episode_metrics = baseline.episode_metrics
_load_inputs = baseline.load_inputs
_summarize = baseline.summarize


def make_context(endpoint: dict[str, Any], row: dict[str, Any]) -> Any:
    from renderers import Qwen3RendererConfig

    context = _make_context(endpoint, row)
    if row["client_path"] == "train":
        context.client.renderer = Qwen3RendererConfig(enable_thinking=True)
    return context


def request_metadata(endpoint: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    metadata = _request_metadata(endpoint, row)
    if row["client_path"] == "train":
        metadata["renderer"] = {"name": "qwen3", "enable_thinking": True}
    metadata["treatment"] = "native_prefill"
    return metadata


def episode_metrics(episode: dict[str, Any], wall_seconds: float | None = None) -> dict[str, Any]:
    metrics = _episode_metrics(episode, wall_seconds)
    closing_tag_intent = False
    cache_known_calls = 0
    calls = []
    for trace in episode.get("traces") or []:
        calls.extend(trace.get("calls") or [])
        for node in trace.get("nodes") or []:
            message = node.get("message") or {}
            content = message.get("content")
            if message.get("role") != "assistant" or not isinstance(content, str):
                continue
            text = content.strip()
            if text.endswith("</tool_call>") and not text.startswith("<tool_call>"):
                try:
                    payload = json.loads(text[: -len("</tool_call>")].strip())
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict) and payload.get("name") == "ipython":
                    closing_tag_intent = True
    for call in calls:
        if (call.get("usage") or {}).get("cached_input_tokens") is not None:
            cache_known_calls += 1
    metrics.update(
        {
            "closing_tag_ipython_intent_heuristic": closing_tag_intent,
            "ipython_intent_in_content": metrics["ipython_intent_in_content"] or closing_tag_intent,
            "logical_input_tokens": metrics["prompt_tokens"] + metrics["cached_input_tokens"],
            "calls_with_cache_measurement": cache_known_calls,
            "calls_without_cache_measurement": len(calls) - cache_known_calls,
            "logical_total_tokens": metrics["prompt_tokens"]
            + metrics["cached_input_tokens"]
            + metrics["completion_tokens"],
        }
    )
    return metrics


def load_inputs(args: Any) -> Any:
    frozen, plan, tasks = _load_inputs(args)
    treatment_path = ROOT / "NATIVE_PREFILL_SPEC.json"
    treatment = json.loads(treatment_path.read_text())
    if baseline.file_hash(ROOT / "driver.py") != treatment["baseline_driver_sha256"]:
        raise ValueError("baseline driver changed after native treatment was specified")
    frozen["treatment"] = treatment
    frozen["design"] = {**frozen["design"], "active_treatment": "native_prefill"}
    for path in (
        Path(__file__).resolve(),
        treatment_path,
        ROOT / "tests/test_native_prefill.py",
        baseline.PRIME / "deps/renderers/renderers/qwen3.py",
        baseline.PRIME / "deps/renderers/renderers/configs.py",
        baseline.PRIME / "deps/verifiers/verifiers/v1/types.py",
        Path(frozen["endpoint"]["renderer_model"]) / "tokenizer_config.json",
    ):
        frozen["source_file_sha256"][str(path)] = baseline.file_hash(path)
    return frozen, plan, tasks


def summarize(records: list[dict[str, Any]], planned: int) -> dict[str, Any]:
    result = _summarize(records, planned)
    for cell in result["cells"]:
        rows = [
            row["derived"]
            for row in records
            if row["coordinate"]["client_path"] == cell["client_path"]
            and row["coordinate"]["temperature"] == cell["temperature"]
        ]
        for key in (
            "logical_input_tokens",
            "cached_input_tokens",
            "logical_total_tokens",
            "closing_tag_ipython_intent_heuristic",
            "calls_without_cache_measurement",
        ):
            cell[key] = sum(row[key] for row in rows)
    result["treatment"] = "native_prefill"
    return result


def main() -> int:
    baseline.make_context = make_context
    baseline.request_metadata = request_metadata
    baseline.episode_metrics = episode_metrics
    baseline.load_inputs = load_inputs
    baseline.summarize = summarize
    if not any(arg == "--image-id" or arg.startswith("--image-id=") for arg in sys.argv[1:]):
        treatment = json.loads((ROOT / "NATIVE_PREFILL_SPEC.json").read_text())
        sys.argv.extend(["--image-id", treatment["runtime_image_id"]])
    return baseline.main()


if __name__ == "__main__":
    raise SystemExit(main())
