"""Twenty bounded paired episodes; no retries, fallbacks, recursive children or training."""

import argparse
import json
import os
import signal
import time
from urllib.request import Request, urlopen

import mini as m
import native_service


class NativeCalls:
    def __init__(self, endpoint):
        self.endpoint, self.calls, self.ids = endpoint, [], set()

    def call(self, messages, maximum, destination, deadline, engineering=False):
        if time.time() >= deadline:
            raise TimeoutError("native call deadline")
        if sum(not c["engineering"] for c in self.calls) >= 50 and not engineering:
            raise ValueError("50 research call cap")
        if sum(c["engineering"] for c in self.calls) >= 2 and engineering:
            raise ValueError("two engineering call cap")
        request = m.body(messages, maximum)
        if destination.exists():
            raise ValueError("call destination already used")
        destination.mkdir(parents=True)
        wire = json.dumps(request, separators=(",", ":")).encode()
        (destination / "REQUEST_WIRE.bin").write_bytes(wire)
        m.write(destination / "MESSAGES.json", messages)
        began, raw = time.time(), None
        result = {
            "engineering": engineering,
            "status": "request_error",
            "call_id": destination.name,
            "request_wire_sha256": m.sha(destination / "REQUEST_WIRE.bin"),
            "request_sha256": m.digest(request),
            "requested_max_tokens": maximum,
            "requested_prompt_tokens": len(request["token_ids"]),
            "started_epoch": began,
        }
        error = None
        try:
            req = Request(
                self.endpoint,
                data=wire,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=max(0.001, min(180, deadline - time.time()))) as response:
                response_wire = response.read()
            (destination / "RESPONSE_WIRE.bin").write_bytes(response_wire)
            raw = json.loads(response_wire)
            decoded = m.decode(request, raw)
            if decoded["request_id"] in self.ids:
                raise ValueError("duplicate native provider request ID")
            self.ids.add(decoded["request_id"])
            result.update(decoded, status="returned_valid")
        except Exception as exc:
            error = exc
            result["error"] = {"type": type(exc).__name__, "message": str(exc)}
            if isinstance(raw, dict):
                for field in ("prompt_tokens", "completion_tokens"):
                    count = raw.get("usage", {}).get(field)
                    if type(count) is int and count >= 0:
                        result[field] = count
        result["elapsed_seconds"] = time.time() - began
        result["response_wire_sha256"] = (
            m.sha(destination / "RESPONSE_WIRE.bin")
            if (destination / "RESPONSE_WIRE.bin").exists()
            else None
        )
        m.write(destination / "CALL.json", result)
        self.calls.append(result)
        m.write(
            m.ATTEMPT / "CALL_PROGRESS.json",
            {
                "attempted_calls": len(self.calls),
                "last_call_id": destination.name,
                "last_call_sha256": m.sha(destination / "CALL.json"),
            },
        )
        if error is not None:
            raise error
        return result


def inspection_prompt(question):
    return (
        "The full numerical data is in context.json in your working directory, shaped "
        '{"series": {channel: [values]}}. Read actual channel names. '
        "Values are rounded to 3 decimals; indices are original sample indices. "
        "Use NumPy or the Python standard library (SciPy is not installed), "
        "without images, plots, "
        "network, shell commands, child models or reading any other files. "
        "You have at most 3 inspection calls followed by one final answer. "
        "For this inspection, return exactly one fenced python cell, no prose. "
        "Print concise numerical observations. "
        "Do not call final() or submit an answer in the cell.\nQuestion: " + question
    )


def engineering(client, deadline):
    workspace = m.ATTEMPT / "engineering/workspace"
    m.write(workspace / "context.json", {"series": {"x": [1, 2, 3]}})
    messages = [{"role": "user", "content": inspection_prompt("Print the sum of the x values.")}]
    with m.executor(workspace) as worker:
        first = client.call(messages, 512, m.ATTEMPT / "calls/engineering-0", deadline, True)
        result = m.execute_cell(worker, first["text"], min(5, max(0.001, deadline - time.time())))
        m.write(m.ATTEMPT / "engineering/EXECUTION.json", result)
        if (
            result["exception"]
            or result["host_failure"]
            or result["stdout"].strip() not in ("6", "6.0")
        ):
            raise ValueError("engineering Python result is not exact6")
    second = client.call(
        [
            {
                "role": "user",
                "content": "A verified Python computation produced sum=6. "
                'Return exactly {"sum":6} with no prose.',
            }
        ],
        512,
        m.ATTEMPT / "calls/engineering-1",
        deadline,
        True,
    )
    if (
        first["finish_reason"] != "stop"
        or second["finish_reason"] != "stop"
        or json.loads(second["text"]) != {"sum": 6}
    ):
        raise ValueError("engineering native final/EOS qualification failed")
    m.write(
        m.ATTEMPT / "ENGINEERING_QUALIFICATION.json",
        {
            "qualified": True,
            "model": str(m.MODEL),
            "native_calls": 2,
            "python_sum": 6,
            "final_sum": 6,
            "evidence_class": "engineering_only",
        },
    )


def episode(row, client, global_deadline):
    began = time.time()
    deadline = min(global_deadline, began + m.EPISODE_CAP)
    directory = m.ATTEMPT / "episodes" / row["episode_id"]
    directory.mkdir(parents=True)
    outcome = {
        **row,
        "status": "failed",
        "answer": "",
        "started_epoch": began,
        "generated_tokens": 0,
    }
    before = len(client.calls)
    try:
        if row["arm"] == "direct":
            value = m.read(m.ROOT / "inputs/direct" / f"{row['row_id']}.json")
            call = client.call(
                [{"role": "user", "content": value["prompt"]}],
                2048,
                m.ATTEMPT / "calls" / (row["episode_id"] + "-final"),
                deadline,
            )
            outcome.update(
                answer=call["text"],
                status="answered",
                direct_view=value["view"],
                generated_tokens=call["completion_tokens"],
                final_finish_reason=call["finish_reason"],
            )
        else:
            public = m.read(m.ROOT / "inputs/public" / f"{row['row_id']}.json")
            workspace = directory / "workspace"
            m.write(workspace / "context.json", {"series": public["series"]})
            messages = [{"role": "user", "content": inspection_prompt(public["question"])}]
            with m.executor(workspace) as worker:
                for turn in range(3):
                    call = client.call(
                        messages,
                        m.output_allowance(outcome["generated_tokens"], False),
                        m.ATTEMPT / "calls" / f"{row['episode_id']}-inspect-{turn}",
                        deadline,
                    )
                    outcome["generated_tokens"] += call["completion_tokens"]
                    result = m.execute_cell(
                        worker, call["text"], min(5, max(0.001, deadline - time.time()))
                    )
                    m.write(directory / f"EXECUTION-{turn}.json", result)
                    observation, inventory = m.observation(result)
                    m.write(
                        directory / f"OBSERVATION-{turn}.json", {"text": observation, **inventory}
                    )
                    messages.extend(
                        [
                            {"role": "assistant", "content": call["text"]},
                            {
                                "role": "user",
                                "content": observation
                                + "\nNext inspection: one fenced python cell only.",
                            },
                        ]
                    )
            messages.append(
                {
                    "role": "user",
                    "content": "FINAL TURN. Python is disabled. Give only one JSON object "
                    "matching the original question schema, without prose or fences.",
                }
            )
            call = client.call(
                messages,
                m.output_allowance(outcome["generated_tokens"], True),
                m.ATTEMPT / "calls" / (row["episode_id"] + "-final"),
                deadline,
            )
            outcome.update(
                answer=call["text"],
                status="answered",
                generated_tokens=outcome["generated_tokens"] + call["completion_tokens"],
                final_finish_reason=call["finish_reason"],
            )
    except Exception as exc:
        outcome["error"] = {"type": type(exc).__name__, "message": str(exc)}
    outcome["call_ids"] = [c["call_id"] for c in client.calls[before:]]
    outcome["elapsed_seconds"] = time.time() - began
    m.write(directory / "EPISODE.json", outcome)
    return outcome


def execute(cap):
    ready = m.verify()
    if (
        cap != m.CAP
        or m.ATTEMPT.exists()
        or not os.environ.get("CUDA_VISIBLE_DEVICES")
        or "," in os.environ["CUDA_VISIBLE_DEVICES"]
    ):
        raise ValueError("MAIN must assign one GPU and unused attempt under exact1100 cap")
    began = time.time()
    m.ATTEMPT.mkdir(parents=True)
    m.write(
        m.ATTEMPT / "OWNER_RUN.json",
        {
            "ready_sha256": m.sha(m.ROOT / "READY.json"),
            "identity": ready["identity"],
            "started_epoch": began,
            "cap_seconds": cap,
            "planned_episodes": 20,
            "research_call_cap": 50,
            "engineering_call_cap": 2,
        },
    )
    process, client, qualified, released, errors, outcomes = None, None, False, False, [], []

    def stop(sig, _frame):
        raise TimeoutError("owner interrupted by signal " + str(sig))

    previous = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, cap - 30)
    deadline = began + cap - 90
    schedule = m.read(m.ROOT / "inputs/SCHEDULE.json")
    try:
        process, endpoint = native_service.start(m.ATTEMPT / "service", min(deadline, began + 240))
        client = NativeCalls(endpoint)
        engineering(client, min(deadline, time.time() + 60))
        qualified = True
        for row in schedule:
            if time.time() >= deadline:
                break
            outcome = episode(row, client, deadline)
            outcomes.append(outcome)
            m.write(
                m.ATTEMPT / "PROGRESS.json",
                {
                    "episodes_terminal": len(outcomes),
                    "last_episode": row["episode_id"],
                    "last_status": outcome["status"],
                    "elapsed_seconds": time.time() - began,
                },
            )
    except BaseException as exc:
        errors.append({"type": type(exc).__name__, "message": str(exc)})
    finally:
        signal.setitimer(signal.ITIMER_REAL, min(60, max(1, began + cap - time.time())))
        try:
            if process is not None:
                native_service.release(process, m.ATTEMPT / "service")
            released = True
        except BaseException as exc:
            errors.append({"stage": "release", "type": type(exc).__name__, "message": str(exc)})
        gold = m.read(m.ROOT / "inputs/HOST_GOLD.json")
        by_id = {r["episode_id"]: r for r in outcomes}
        scored = []
        for row in schedule:
            result = by_id.get(row["episode_id"], {**row, "status": "unattempted", "answer": ""})
            scored.append({**result, "score": m.score(result["answer"], gold[row["row_id"]])})
        paired = []
        for identifier in dict.fromkeys(r["row_id"] for r in schedule):
            values = {r["arm"]: r["score"]["primary"] for r in scored if r["row_id"] == identifier}
            paired.append(
                {
                    "row_id": identifier,
                    **values,
                    "python_minus_direct": values["python"] - values["direct"],
                }
            )
        calls = client.calls if client is not None else []
        cost = {}
        for scope in ("engineering", "research", "direct", "python"):
            selected = [
                c
                for c in calls
                if (
                    c["engineering"] == (scope == "engineering")
                    if scope in ("engineering", "research")
                    else "-" + scope + "-" in c["call_id"]
                )
            ]
            cost[scope] = {
                "attempted_calls": len(selected),
                "observed_prompt_tokens": sum(c.get("prompt_tokens", 0) for c in selected),
                "observed_completion_tokens": sum(c.get("completion_tokens", 0) for c in selected),
                "observed_cached_tokens": sum(c.get("cached_tokens") or 0 for c in selected),
                "unknown_cache_usage_calls": sum(c.get("cached_tokens") is None for c in selected),
                "unknown_usage_calls": sum(
                    "prompt_tokens" not in c or "completion_tokens" not in c for c in selected
                ),
            }
        report = {
            "schema": "anomalyxl-native-mini-result-v1",
            "runtime_qualified": qualified,
            "primary_readout_eligible": qualified and len(outcomes) == 20 and released,
            "episodes": scored,
            "paired": paired,
            "paired_mean_delta": sum(r["python_minus_direct"] for r in paired) / 10
            if qualified
            else None,
            "cost": cost,
            "owner_elapsed_seconds": time.time() - began,
            "complete_episodes": len(outcomes) == 20,
            "released": released,
            "claim": "Exploratory current-executor adaptation and official-score headroom; "
            "no RL/novelty/paper-reproduction claim.",
        }
        m.write(m.ATTEMPT / "RESULT.json", report)
        terminal = {
            "runtime_qualified": qualified,
            "released": released,
            "episodes_terminal": len(outcomes),
            "errors": errors,
            "complete": qualified and released and len(outcomes) == 20 and not errors,
            "elapsed_seconds": time.time() - began,
            "result_sha256": m.sha(m.ATTEMPT / "RESULT.json"),
        }
        m.write(m.ATTEMPT / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--outer-seconds", type=int, default=m.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(m.verify()["identity"])
    else:
        result = execute(args.outer_seconds)
        print(json.dumps(result))
        raise SystemExit(0 if result["complete"] else 1)
