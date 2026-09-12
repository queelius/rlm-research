"""One attested native service,336fixed requests,768explicit prediction slots."""

import argparse
import json
import os
import signal
import time
from collections import Counter
from urllib.request import Request, urlopen

import size_study as study


def send(endpoint, row, tokenizer, destination, timeout):
    started = time.time()
    study.write(destination / "REQUEST.json", row)
    raw = None
    try:
        request = Request(
            endpoint,
            data=json.dumps(row["body"], separators=(",", ":")).encode(),
            headers=study.validator().headers(),
            method="POST",
        )
        with urlopen(request, timeout=timeout) as response:
            raw = json.loads(response.read())
        study.write(destination / "RESPONSE.json", raw)
        if (
            len(raw.get("choices", [])) != 1
            or not raw.get("request_id")
            or raw.get("model") != study.CHILD_ALIAS
        ):
            raise ValueError("native response identity differs")
        choice, usage = raw["choices"][0], raw["usage"]
        if usage["prompt_tokens"] != len(row["body"]["token_ids"]) or usage[
            "completion_tokens"
        ] != len(choice["token_ids"]):
            raise ValueError("native physical token inventory differs")
        result = study.validator().response_record(row, raw, tokenizer, started, time.time())
        if choice.get("finish_reason") != "stop":
            result.update(
                status="invalid_response", prediction={}, validation_error="non-stop reply"
            )
        result["raw_response_file_sha256"] = study.sha(destination / "RESPONSE.json")
    except Exception as error:
        result = {
            "call_id": row["call_id"],
            "dataset": row["dataset"],
            "start": row["start"],
            "ids": row["ids"],
            "status": "request_error" if raw is None else "integrity_error",
            "prediction": {},
            "error": {"type": type(error).__name__, "message": str(error)},
        }
        if raw is not None:
            usage = raw.get("usage", {})
            for name in ("prompt_tokens", "completion_tokens"):
                value = usage.get(name)
                if isinstance(value, int) and value >= 0:
                    result[name] = value
    result.update(
        batch_size=row["batch_size"],
        started_epoch=started,
        ended_epoch=time.time(),
        wall_seconds=time.time() - started,
        request_body_sha256=study.digest(row["body"]),
        requested_prompt_tokens=len(row["body"]["token_ids"]),
    )
    study.write(destination / "CALL.json", result)
    return result


def summarize(calls, schedule, gold):
    planned = {row["call_id"]: row for row in schedule}
    observed = {call["call_id"]: call for call in calls}
    if (
        len(planned) != len(schedule)
        or len(observed) != len(calls)
        or not observed.keys() <= planned.keys()
    ):
        raise ValueError("duplicate or out-of-inventory call")
    metrics, outcomes = {}, {}
    for row in schedule:
        key = f"{row['dataset']}:{row['batch_size']}"
        metric = metrics.setdefault(
            key,
            {
                "planned_calls": 0,
                "attempted_calls": 0,
                "unattempted_calls": 0,
                "planned_predictions": 0,
                "valid_predictions": 0,
                "correct": 0,
                "wrong": 0,
                "invalid_predictions": 0,
                "request_error_predictions": 0,
                "integrity_error_predictions": 0,
                "unavailable_predictions": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cached_prompt_tokens": 0,
                "request_wall_seconds": 0.0,
                "requested_prompt_tokens": 0,
                "usage_unknown_calls": 0,
                "gold_label_counts": Counter(),
                "correct_label_counts": Counter(),
            },
        )
        metric["planned_calls"] += 1
        metric["planned_predictions"] += len(row["ids"])
        call = observed.get(row["call_id"])
        if call and (
            call["dataset"] != row["dataset"]
            or call["ids"] != row["ids"]
            or call["batch_size"] != row["batch_size"]
        ):
            raise ValueError("call coordinate identity mismatch")
        metric["attempted_calls"] += int(call is not None)
        metric["unattempted_calls"] += int(call is None)
        valid = call is not None and call["status"] == "returned_valid"
        for identifier in row["ids"]:
            label = gold["labels"][identifier]
            metric["gold_label_counts"][label] += 1
            correct = call["prediction"][identifier] == label if valid else None
            outcomes[(row["dataset"], row["batch_size"], identifier)] = correct
            if valid:
                metric["valid_predictions"] += 1
                metric["correct"] += int(correct)
                metric["wrong"] += int(not correct)
                metric["correct_label_counts"][label] += int(correct)
            else:
                metric["unavailable_predictions"] += 1
                if call:
                    name = {
                        "invalid_response": "invalid_predictions",
                        "request_error": "request_error_predictions",
                        "integrity_error": "integrity_error_predictions",
                    }[call["status"]]
                    metric[name] += 1
        if call:
            metric["requested_prompt_tokens"] += call.get("requested_prompt_tokens", 0)
            metric["usage_unknown_calls"] += int(
                call.get("prompt_tokens") is None or call.get("completion_tokens") is None
            )
            for token_key in ("prompt_tokens", "completion_tokens", "cached_prompt_tokens"):
                metric[token_key] += int(call.get(token_key) or 0)
            metric["request_wall_seconds"] += call.get("wall_seconds", 0)
    for metric in metrics.values():
        metric["gold_label_counts"] = dict(metric["gold_label_counts"])
        metric["correct_label_counts"] = dict(metric["correct_label_counts"])
        metric["correct_lower_bound"] = metric["correct"]
        metric["correct_upper_bound"] = metric["correct"] + metric["unavailable_predictions"]
        metric["total_tokens"] = metric["prompt_tokens"] + metric["completion_tokens"]
    paired = {}
    for dataset in sorted({row["dataset"] for row in schedule}):
        identifiers = {
            identifier for row in schedule if row["dataset"] == dataset for identifier in row["ids"]
        }
        for larger, smaller in ((16, 4), (16, 1), (4, 1)):
            counts = Counter()
            for identifier in sorted(identifiers):
                a, b = (
                    outcomes.get((dataset, larger, identifier)),
                    outcomes.get((dataset, smaller, identifier)),
                )
                if a is None or b is None:
                    category = (
                        "both_unavailable"
                        if a is None and b is None
                        else ("larger_unavailable" if a is None else "smaller_unavailable")
                    )
                else:
                    category = (
                        "both_correct"
                        if a and b
                        else "both_wrong"
                        if not a and not b
                        else ("smaller_wins" if b else "smaller_losses")
                    )
                counts[category] += 1
            paired[f"{dataset}:{larger}_vs_{smaller}"] = dict(counts)
    return {
        "schema": "helper-unseen-size-comparison-result-v1",
        "planned_calls": len(schedule),
        "attempted_calls": len(calls),
        "planned_predictions": sum(len(row["ids"]) for row in schedule),
        "all_calls_attempted": len(calls) == len(schedule),
        "by_dataset_size": metrics,
        "paired": paired,
        "runtime": "fresh shared service; VLLM_BATCH_INVARIANT=1 attested; no flag-off pooling",
        "claim_boundary": (
            "256 unique records times 3 sizes; research-exposed, absent from verified c32 SFT/new32"
        ),
        "cost_boundary": (
            "token totals sum reported usage only; error-call unknown usage is not zero cost; "
            "requested prompt tokens and usage-unknown calls are separate"
        ),
    }


def execute(cap):
    ready = study.verify()
    if cap != study.CAP or study.ATTEMPT.exists():
        raise ValueError("unused attempt001 and exact1200-second cap required")
    if (
        not os.environ.get("CUDA_VISIBLE_DEVICES")
        or "," in os.environ["CUDA_VISIBLE_DEVICES"]
        or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    ):
        raise ValueError("MAIN must assign one GPU and inherited private credential")
    started, calls, errors, released, suite = time.time(), [], [], False, None
    deadline = started + study.CAP - 90
    study.ATTEMPT.mkdir(parents=True)
    service = study.ATTEMPT / "service"
    service.mkdir()
    rows = study.schedule()
    gold = study.source().panel()[3]
    study.write(
        study.ATTEMPT / "OWNER_RUN.json",
        {
            "ready_identity": ready["identity"],
            "started_epoch": started,
            "planned_calls": study.CALLS,
            "planned_predictions": study.PREDICTIONS,
            "cap_seconds": cap,
            "root_calls": 0,
            "training_updates": 0,
            "runtime_flag": "VLLM_BATCH_INVARIANT=1",
        },
    )

    def stop(sig, _frame):
        raise TimeoutError("new-panel size comparison interrupted by signal " + str(sig))

    previous = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, study.CAP - 30)
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
        suite = study.dependencies()
        suite.start_service(service, study.source().binding(), min(started + 240, deadline))
        study.write(study.ATTEMPT / "RUNTIME_ATTESTATION.json", study.attest(service / "service"))
        descriptor = study.read(service / "service/endpoint-original.json")
        endpoint = f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
        request_ids = set()
        for row in rows:
            if time.time() >= deadline:
                raise TimeoutError(
                    "request deadline reached; remaining planned slots remain unattempted"
                )
            result = send(
                endpoint,
                row,
                tokenizer,
                study.ATTEMPT / "calls" / row["call_id"],
                max(1, min(180, deadline - time.time())),
            )
            request_id = result.get("request_id")
            if request_id and request_id in request_ids:
                result.update(
                    status="integrity_error", prediction={}, error="duplicate provider request ID"
                )
                study.write(study.ATTEMPT / "calls" / row["call_id"] / "CALL.json", result)
            if request_id:
                request_ids.add(request_id)
            calls.append(result)
            study.write(
                study.ATTEMPT / "PROGRESS.json",
                {
                    "attempted_calls": len(calls),
                    "last_dataset": row["dataset"],
                    "last_size": row["batch_size"],
                    "elapsed_seconds": time.time() - started,
                },
            )
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error)})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 60)
        if suite is not None:
            try:
                suite.release_service(service)
                released = True
            except BaseException as error:
                errors.append(
                    {"stage": "release", "type": type(error).__name__, "message": str(error)}
                )
        else:
            released = True
        summary = summarize(calls, rows, gold)
        study.write(study.ATTEMPT / "RESULT.json", summary)
        terminal = {
            "complete": not errors and released and len(calls) == study.CALLS,
            "released": released,
            "errors": errors,
            "attempted_calls": len(calls),
            "elapsed_seconds": time.time() - started,
        }
        study.write(study.ATTEMPT / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=study.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(study.verify()["identity"])
    else:
        value = execute(args.outer_seconds)
        print(json.dumps(value, sort_keys=True))
        raise SystemExit(0 if value["complete"] else 1)
