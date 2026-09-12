"""CPU source-to-raw audit and all fixed paired fresh512 comparisons."""

import json
from pathlib import Path

import collect
import eligibility
import metrics
import study


def audited_arm(arm, tokenizer):
    ready = study.verify(arm)
    output = study.attempt(arm)
    terminal = study.read(output / "OWNER_TERMINAL.json")
    saved = study.read(output / "RESULT.json")
    run = study.read(output / "OWNER_RUN.json")
    runtime = study.read(output / "RUNTIME.json") if (output / "RUNTIME.json").exists() else {}
    engine = (
        study.read(output / "ENGINE_ATTESTATION.json")
        if (output / "ENGINE_ATTESTATION.json").exists()
        else {}
    )
    fixed = study.read(output / "ELIGIBILITY.json")
    current = eligibility.fixed_endpoints(arm)
    if (
        fixed != current
        or run["ready_identity"] != ready["identity"]
        or run["schedule_sha256"] != study.digest(study.schedule())
        or terminal["result_sha256"] != study.sha(output / "RESULT.json")
        or saved["eligibility_sha256"] != study.sha(output / "ELIGIBILITY.json")
    ):
        raise ValueError("arm source/runtime/fixed endpoint provenance differs")
    if runtime and (
        study.read(output / "service/BINDING.json") != current["arm_eligibility"]["binding"]
        or runtime["binding_sha256"] != study.sha(output / "service/BINDING.json")
        or runtime["configuration"]
        != study.sanitized_runtime(study.read(output / "service/service/inference.json"))
        or runtime["configuration_sha256"] != study.digest(runtime["configuration"])
    ):
        raise ValueError("saved runtime configuration or native endpoint binding differs")
    if engine and (
        engine["actual_kernel_marker"] != "batch_invariant.py / matmul_persistent"
        or engine["inference_log_sha256"] != study.sha(engine["inference_log"])
    ):
        raise ValueError("actual kernel evidence differs")
    stopped_path = output / "service/SERVICE_STOPPED.json"
    stopped = study.read(stopped_path) if stopped_path.exists() else {}
    qualified_runtime = bool(
        runtime
        and engine
        and stopped.get("all_owned_process_identities_exited")
        and stopped.get("ports_free")
    )
    if terminal["complete"] and not qualified_runtime:
        raise ValueError("complete arm lacks qualified cleanly released runtime")
    rows = study.schedule()
    calls, request_ids = [], set()
    for row in rows:
        path = output / "calls" / (row["call_id"] + ".json")
        if not path.exists():
            continue
        saved_call = study.read(path)
        request_path = Path(saved_call["raw_request_path"])
        if (
            study.sha(request_path) != saved_call["raw_request_bytes_sha256"]
            or study.read(request_path) != row["body"]
            or list(
                study.read(request_path)["sampling_params"]["structured_outputs"]["json"][
                    "properties"
                ]
            )
            != row["ids"]
            or saved_call["request_body_sha256"] != study.digest(row["body"])
        ):
            raise ValueError("exact saved request bytes/body/ordered schema differs")
        if "raw_response_path" in saved_call:
            response_path = Path(saved_call["raw_response_path"])
            if study.sha(response_path) != saved_call["raw_response_bytes_sha256"]:
                raise ValueError("raw response bytes differ")
        if saved_call["status"] == "returned_valid":
            call = collect.decode(
                row,
                study.read(response_path),
                tokenizer,
                saved_call["started_epoch"],
                saved_call["ended_epoch"],
            )
            if saved_call.get("http_status") != 200 or call["request_id"] in request_ids:
                raise ValueError("valid response HTTP/unique request identity differs")
            for key in (
                "status",
                "prediction",
                "completion_ids",
                "decoded_text",
                "request_id",
                "finish_reason",
                "prompt_tokens",
                "completion_tokens",
                "cached_prompt_tokens",
            ):
                if call.get(key) != saved_call.get(key):
                    raise ValueError("raw native decoding differs: " + key)
            request_ids.add(call["request_id"])
            calls.append(call)
        else:
            calls.append(saved_call)
    result = metrics.summarize(calls, study.gold(), rows)
    if not saved["runtime_qualified"]:
        result["metrics"]["primary_accuracy"] = None
    for key in ("inventory", "metrics", "per_class", "predictions", "cost", "complete"):
        if result[key] != saved[key]:
            raise ValueError("raw recomputed result differs: " + key)
    result["complete"] = (
        result["complete"]
        and terminal["complete"]
        and terminal["runtime_qualified"]
        and qualified_runtime
    )
    if not result["complete"]:
        result["metrics"]["primary_accuracy"] = None
    return (
        result,
        runtime,
        {
            "result_sha256": study.sha(output / "RESULT.json"),
            "terminal_sha256": study.sha(output / "OWNER_TERMINAL.json"),
            "raw_envelopes_redecoded": len(request_ids),
        },
    )


def execute():
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    arms, runtimes, provenance = {}, {}, {}
    for arm in study.ARMS:
        if (study.attempt(arm) / "OWNER_TERMINAL.json").exists():
            arms[arm], runtimes[arm], provenance[arm] = audited_arm(arm, tokenizer)
    comparisons = {}
    for left, right in (("c32", "rl_step8"), ("c32", "sft_step8"), ("rl_step8", "sft_step8")):
        key = left + "_vs_" + right
        if left not in arms or right not in arms:
            comparisons[key] = {"available": False, "reason": "a planned endpoint is not terminal"}
            continue
        runtime_keys = (
            "configuration_sha256",
            "service_wrapper_sha256",
            "native_python",
            "max_prompt_plus_1024",
            "actual_max_model_len",
            "concurrency",
            "batch",
        )
        matched = bool(runtimes[left] and runtimes[right]) and all(
            runtimes[left][key] == runtimes[right][key] for key in runtime_keys
        )
        if not matched:
            comparisons[key] = {"available": False, "reason": "runtime differs; no baseline reuse"}
            continue
        comparisons[key] = {
            "available": True,
            **metrics.paired(arms[left], arms[right], study.gold(), study.schedule()),
        }
    return {
        "schema": "fresh512-source-to-raw-paired-audit-v1",
        "arms": arms,
        "comparisons": comparisons,
        "provenance": provenance,
        "boundary": (
            "source-to-raw audit, not independent trainer replication; all fixed endpoints reported"
        ),
        "baseline_reuse": "only complete exact fresh512 c32 with matched qualified service",
        "training_costs": "separate trainer results; endpoint costs contain only fresh512 calls",
    }


if __name__ == "__main__":
    print(json.dumps(execute(), sort_keys=True))
