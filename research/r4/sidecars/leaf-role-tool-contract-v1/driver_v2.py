"""V2 collector: admit scoring only after complete native response authentication."""

import argparse
import asyncio
import os
import time
from pathlib import Path

import httpx
from transformers import AutoTokenizer

import driver as v1
import scoring_v2
import study as s

AUTHORIZED_OUTPUT = s.ROOT / "outputs/attempt-001/rollout"
verify = v1.verify


def validate_output(output):
    if Path(output).resolve() != AUTHORIZED_OUTPUT.resolve():
        raise ValueError("only exact leaf-role-tool-contract attempt-001 rollout is authorized")


async def run(endpoint, spec, output, deadline):
    validate_output(output)
    v1.validate_endpoint(endpoint)
    output.mkdir(parents=True, exist_ok=False)
    s.write_once(output / "SPEC.json", spec)
    s.write_once(output / "ENDPOINT.json", endpoint)
    tokenizer = AutoTokenizer.from_pretrained(s.MODEL["path"], local_files_only=True,
                                               trust_remote_code=False)
    prompt_ids = s.read(s.ROOT / "PROMPT_IDS.json") if s.ROOT == Path(__file__).resolve().parent else {}
    # Tests supply the prompt identity through the design; production additionally pins the full vectors.
    records = []
    pending = iter(spec["design"]["plan"])
    stop = asyncio.Event()

    async def worker(client, url):
        while not stop.is_set():
            row = next(pending, None)
            if row is None:
                return
            body = s.make_request(spec["design"], row)
            gold = spec["design"]["batches"][row["batch_id"]]["gold"]
            record = {"coordinate": row, "request_sha256": s.digest(body),
                      "started": time.time(), "model_called": False,
                      "response_received": False, "native_verified": False,
                      "model_completed": False, "score": s.score_missing(gold),
                      "usage": {}, "tools_executed": False}
            try:
                record["model_called"] = True
                response = await client.post(url + "/chat/completions", json=body)
                record["response_received"] = True
                record["http_status"] = response.status_code
                record["raw_response_text"] = response.text
                record["response_headers"] = {key: response.headers[key] for key in
                                               ("x-request-id", "x-ratelimit-remaining-requests")
                                               if key in response.headers}
                response.raise_for_status()
                raw = response.json()
                record["raw_response"] = raw
                record["provider_response_id"] = raw.get("id")
                expected = prompt_ids.get(row["id"])
                if expected is None:
                    expected_digest = spec["design"]["rendered_prompts"][row["id"]]["typed_token_ids_sha256"]
                    incoming = raw.get("prompt_token_ids")
                    if not isinstance(incoming, list) or s.digest(incoming) != expected_digest:
                        raise ValueError("actual native prompt token identity unavailable or different")
                    expected = incoming
                message, finish, usage = scoring_v2.verified_response(raw, expected, tokenizer)
                record["native_verified"] = True
                record["model_completed"] = True
                record["finish_reason"] = finish
                record["usage"] = usage
                record["score"] = s.score_message(message, gold, finish)
            except asyncio.CancelledError:
                record["error"] = {"type": "CancelledError", "cost_unknown": True}
                raise
            except Exception as error:
                record["native_verified"] = False
                record["model_completed"] = False
                record["score"] = s.score_missing(gold)
                record["usage"] = {}
                record["error"] = {"type": type(error).__name__, "message": str(error)[:1200]}
                stop.set()
            finally:
                record["ended"] = time.time()
                s.write_once(output / "calls" / f"{row['id']}.json", record)
                records.append(record)

    started = time.time()
    reason = None
    try:
        async with asyncio.timeout(max(0.001, deadline - time.time())):
            url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
            headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]}
            async with httpx.AsyncClient(headers=headers, timeout=120, trust_env=False,
                                         event_hooks={"request": [v1.wire_hook(spec, output)]}) as client:
                version = await client.get(url.removesuffix("/v1") + "/version")
                version.raise_for_status()
                if version.json().get("version") != "0.28.0":
                    raise ValueError("wrong vLLM version")
                models = await client.get(url + "/models")
                models.raise_for_status()
                cards = models.json().get("data", [])
                if len(cards) != 1 or cards[0].get("id") != s.MODEL["alias"] or \
                        cards[0].get("root") != s.MODEL["path"] or cards[0].get("parent") is not None:
                    raise ValueError("live model differs")
                await asyncio.gather(*(worker(client, url) for _ in range(4)))
    except TimeoutError:
        reason = "collection_deadline"
    except BaseException as error:
        reason = type(error).__name__
        s.write_once(output / "ERROR.json", {"type": reason, "message": str(error)[:1200]})
    finally:
        retained = [s.read(path) for path in sorted((output / "calls").glob("*.json"))]
        analysis = scoring_v2.summarize(spec["design"], retained)
        s.write_once(output / "analysis.json", analysis)
        seen = {record["coordinate"]["id"] for record in retained}
        stop_reason = reason or ("request_error" if stop.is_set() else None)
        s.write_once(output / "STATUS.json", {"planned": len(spec["design"]["plan"]),
            "recorded": len(retained), "native_verified": analysis["native_verified"],
            "model_completed": sum(record.get("model_completed", False) for record in retained),
            "stop_reason": stop_reason, "elapsed_seconds": time.time() - started,
            "unrun": [row["id"] for row in spec["design"]["plan"] if row["id"] not in seen]})
    return 0 if reason is None and not stop.is_set() and len(records) == len(spec["design"]["plan"]) else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--endpoint", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--deadline", type=float)
    args = parser.parse_args()
    spec = s.read(s.ROOT / "SPEC.json")
    if args.command == "verify":
        v1.verify(spec)
        print("verified V2 native-admission collector; no model calls")
    else:
        v1.verify(spec)
        raise SystemExit(asyncio.run(run(s.read(args.endpoint), spec, args.output, args.deadline)))


if __name__ == "__main__":
    main()
