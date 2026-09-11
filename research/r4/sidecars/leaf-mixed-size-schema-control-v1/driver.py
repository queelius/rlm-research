"""Fixed checkpoint × free/schema control; GPU launch belongs to the parent."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import time
from copy import deepcopy
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
CORR_PATH = SIDE / "leaf-correspondence-controls-v1/driver.py"
CORR_SHA = "6fa2846b144f863cea79f2c82ee9e6d07d00104aba4f01dc8d95ec51fd1a49c8"
PARENT_SPEC = CORR_PATH.parent / "SPEC-ROTATION.runtime-order-v2.json"
PARENT_SHA = "e08813e94cb2bf054437749b1ca86640edcc59b942840165062bd1207786d04d"
SST_PATH = SIDE / "leaf-sentiment-transfer-v1/driver.py"
SST_SHA = "eb9509ed00a85cd942d959407deb8c80f495f7fec2426f477265af48e407cb63"
WEIGHTS = {"original": "original", "old_sft": "old_sft", "Afinal": "A", "Bfinal": "B"}


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_owned(name: str, path: Path, expected: str):
    if file_hash(path) != expected:
        raise ValueError("frozen helper source changed: " + str(path))
    loader = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


corr = load_owned("mixed_schema_owned_correspondence", CORR_PATH, CORR_SHA)
sst = load_owned("mixed_schema_owned_weight_authentication", SST_PATH, SST_SHA)
digest, write_once = corr.digest, corr.write_once
original_score_coordinate = corr.score_coordinate


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def build_spec() -> dict:
    if file_hash(PARENT_SPEC) != PARENT_SHA:
        raise ValueError("frozen offset0 source changed")
    parent = read(PARENT_SPEC)
    corr.verify_inputs(parent)
    design = deepcopy(parent["design"])
    design.update(
        {
            "model_alias": "__UNBOUND_WEIGHT__",
            "plan": [],
            "coordinates": [],
            "batches": [],
            "wall_time_cap_seconds": 600,
            "call_timeout_seconds": 120,
        }
    )
    for source in parent["design"]["plan"]:
        if source["offset"] != 0:
            continue
        bid = len(design["batches"])
        design["batches"].append(deepcopy(parent["design"]["batches"][source["batch_id"]]))
        cells = ["free64", "schema64"]
        if (source["context_index"] + source["repeat"]) % 2:
            cells.reverse()
        for position, cell in enumerate(cells):
            row = {
                **source,
                "parent_row_id": source["id"],
                "arm": cell,
                "cell": cell,
                "batch_id": bid,
                "dispatch_order": len(design["plan"]),
                "treatment_order": position,
                "id": digest([ROOT.name, source["id"], cell]),
            }
            row["coordinate_id"] = row["id"]
            design["plan"].append(row)
            design["coordinates"].append(deepcopy(row))
    if len(design["plan"]) != 16:
        raise ValueError("requires eight fixed source context/seed pairs")
    sources = dict(parent["source_file_sha256"])
    sources.update(
        {
            str(p): file_hash(p)
            for p in [
                Path(__file__),
                ROOT / "test_driver.py",
                ROOT / "DESIGN.md",
                ROOT / "PLAN.md",
                ROOT / "README.md",
                ROOT / "DESIGN_FREEZE.json",
                PARENT_SPEC,
                CORR_PATH.parent / "READY.json",
                SST_PATH,
            ]
        }
    )
    spec = {
        "schema": ROOT.name,
        "weight_conditions": list(WEIGHTS),
        "calls_per_weight": 16,
        "total_calls": 64,
        "design": design,
        "source_sha256": sources,
        "parent_spec_path": str(PARENT_SPEC),
        "parent_spec_sha256": PARENT_SHA,
        "provenance": parent["provenance"],
        "checkpoint_rule": "fixed original/old-selected/A epoch2 step206/B epoch2 step204; no outcome-based substitution",
        "B_outcomes_used_for_preparation": False,
        "only_condition_request_delta": "free64 removes structured_outputs from exact offset0 schema64 body",
        "request_sha256": {r["id"]: digest(make_request(design, r)) for r in design["plan"]},
    }
    return spec


def make_request(design: dict, row: dict) -> dict:
    body = corr.make_request(design, {**row, "arm": "anonymous"})
    if row["arm"] == "free64":
        body.pop("structured_outputs")
    elif row["arm"] != "schema64":
        raise ValueError("unknown format condition")
    return body


def score_coordinate(design: dict, coordinate: dict, records: list[dict]) -> dict:
    parent_id = coordinate["parent_row_id"]
    parent_coordinate = {**coordinate, "id": parent_id, "coordinate_id": parent_id}
    selected = []
    for record in records:
        if record["coordinate"]["id"] == coordinate["id"]:
            selected.append({**record, "coordinate": parent_coordinate})
    result = original_score_coordinate(design, parent_coordinate, selected)
    result["coordinate"] = coordinate
    return result


# Private instances only: the sealed sources and other agents' imports never change.
corr.score_coordinate = score_coordinate
corr.fixed.make_request = make_request
corr.fixed.score_coordinate = score_coordinate
collect_calls = corr.fixed.collect_calls


def summarize(design: dict, records: list[dict]) -> dict:
    summary = corr.summarize(design, records)
    pairs = {}
    for result in summary["coordinates"]:
        pairs.setdefault(result["coordinate"]["parent_row_id"], {})[result["coordinate"]["arm"]] = (
            result
        )
    paired = []
    for parent_id, cells in pairs.items():
        free, schema = cells["free64"], cells["schema64"]
        observed = free["model_completed"] and schema["model_completed"]
        aligned = free["aligned_records"] == schema["aligned_records"] == 64
        captured = free["physical_prompt"]["captured"] and schema["physical_prompt"]["captured"]
        changes = []
        if aligned:
            for a, b in zip(free["record_results"], schema["record_results"], strict=True):
                if a["id"] != b["id"]:
                    raise ValueError("paired question identity differs")
                changes.append(
                    {
                        "id": a["id"],
                        "question_group_sha256": a["question_group_sha256"],
                        "source_position": a["source_position"],
                        "free_prediction": a["prediction"],
                        "schema_prediction": b["prediction"],
                        "canonical_correct_difference": int(b["canonical_correct"])
                        - int(a["canonical_correct"]),
                    }
                )
        paired.append(
            {
                "parent_row_id": parent_id,
                "context_index": free["coordinate"]["context_index"],
                "seed": free["coordinate"]["seed"],
                "jointly_aligned_records": 64 if aligned else 0,
                "schema_valid_difference": int(schema["schema_valid"]) - int(free["schema_valid"])
                if observed
                else None,
                "canonical_correct_difference": schema["canonical_correct"]
                - free["canonical_correct"]
                if aligned
                else None,
                "physical_input_ids_equal": free["physical_prompt"]["token_ids_sha256"]
                == schema["physical_prompt"]["token_ids_sha256"]
                if captured
                else None,
                "per_question_changes_when_jointly_aligned": changes,
            }
        )
    summary.update({"comparison": ROOT.name, "paired": paired})
    return summary


def authenticate(weight: str, endpoint: dict, sources: dict) -> None:
    if weight not in WEIGHTS:
        raise ValueError("unknown fixed weight")
    sst.authenticate_weight(WEIGHTS[weight], endpoint, sources)
    if (
        endpoint["host"] != "127.0.0.1"
        or not endpoint.get("inference_only")
        or endpoint.get("vllm", {}).get("version") != "0.28.0"
        or endpoint["vllm"].get("max_model_len", 0) < 8192
        or not isinstance(endpoint["port"], int)
        or not 1024 <= endpoint["port"] <= 65535
    ):
        raise ValueError("requires truthful compatible local inference endpoint")


def bind_spec(weight: str, endpoint_path: Path, frozen_path: Path = ROOT / "SPEC.json") -> dict:
    spec = read(frozen_path)
    verify_inputs(spec)
    if "endpoint" in spec:
        raise ValueError("bind the unbound frozen specification")
    endpoint = read(endpoint_path)
    sources = dict(spec["source_sha256"])
    sources[str(frozen_path.resolve())] = file_hash(frozen_path)
    sources[str(endpoint_path.resolve())] = file_hash(endpoint_path)
    authenticate(weight, endpoint, sources)
    spec.update(
        {
            "weight": weight,
            "endpoint": endpoint,
            "endpoint_path": str(endpoint_path.resolve()),
            "frozen_spec_path": str(frozen_path.resolve()),
            "source_sha256": sources,
        }
    )
    spec["design"]["model_alias"] = endpoint["model_alias"]
    spec["request_sha256"] = {
        r["id"]: digest(make_request(spec["design"], r)) for r in spec["design"]["plan"]
    }
    return spec


def verify_inputs(spec: dict) -> None:
    sst.verify_hashes(spec["source_sha256"])
    expected = (
        bind_spec(spec["weight"], Path(spec["endpoint_path"]), Path(spec["frozen_spec_path"]))
        if "endpoint" in spec
        else build_spec()
    )
    if expected != spec:
        raise ValueError("frozen specification differs from exact implementation inputs")


def check_live(endpoint: dict, models: dict) -> None:
    cards = {r["id"]: r for r in models["data"]}
    card = cards.get(endpoint["model_alias"], {})
    if (
        card.get("root") != endpoint["adapter"]["path"]
        or card.get("parent") != endpoint["base_model"]["path"]
    ):
        raise ValueError("live alias/root/base differs from bound checkpoint")
    if cards.get(endpoint["base_model"]["path"], {}).get("max_model_len", 0) < 8192:
        raise ValueError("live model context not qualified")


async def run(spec_path: Path, output: Path) -> int:
    spec = read(spec_path)
    verify_inputs(spec)
    if "endpoint" not in spec:
        raise ValueError("run requires an immutable completed-weight endpoint binding")
    endpoint = spec["endpoint"]
    url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
    key = os.environ[endpoint["api_key_env"]]
    output.mkdir(parents=True, exist_ok=False)
    (output / "calls").mkdir()
    (output / "coordinates").mkdir()
    write_once(output / "SPEC.json", spec)
    started, deadline = time.time(), time.monotonic() + 600
    write_once(
        output / "ATTEMPT.json",
        {
            "started": started,
            "spec_sha256": file_hash(spec_path),
            "weight": spec["weight"],
            "model_alias": endpoint["model_alias"],
            "adapter_sha256": endpoint["adapter"]["model_sha256"],
        },
    )
    reason = None
    try:
        async with asyncio.timeout(max(0.001, deadline - time.monotonic())):
            async with httpx.AsyncClient(
                headers={"Authorization": "Bearer " + key}, timeout=120, trust_env=False
            ) as client:
                version = await client.get(url.removesuffix("/v1") + "/version")
                version.raise_for_status()
                write_once(output / "VERSION_PREFLIGHT.json", version.json())
                if version.json().get("version") != "0.28.0":
                    raise ValueError("live vLLM version changed")
                response = await client.get(url + "/models")
                response.raise_for_status()
                write_once(output / "MODELS_PREFLIGHT.json", response.json())
                check_live(endpoint, response.json())
                _, reason = await collect_calls(client, url, spec, output, deadline)
    except TimeoutError:
        reason = "wall_time_cap"
    except Exception as error:
        reason = "preflight_or_runtime_error:" + type(error).__name__
        write_once(
            output / "ERROR.json", {"type": type(error).__name__, "message": str(error)[:1200]}
        )
    finally:
        records = [read(p) for p in sorted((output / "calls").glob("*.json"))]
        summary = summarize(spec["design"], records)
        summary["weight"] = spec["weight"]
        write_once(output / "analysis.json", summary)
        seen = {r["coordinate"]["id"] for r in records}
        write_once(
            output / "STATUS.json",
            {
                "planned": 16,
                "recorded": len(records),
                "stop_reason": reason,
                "wall_seconds": time.time() - started,
                "unrun": [r["id"] for r in spec["design"]["plan"] if r["id"] not in seen],
            },
        )
    return 0 if reason is None and len(records) == 16 else 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "verify", "bind", "run"])
    parser.add_argument("--weight", choices=list(WEIGHTS))
    parser.add_argument("--endpoint-descriptor", type=Path)
    parser.add_argument("--spec-path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        path = args.spec_path or ROOT / "SPEC.json"
        write_once(path, build_spec())
        print(json.dumps({"spec": str(path), "sha256": file_hash(path), "live_calls": 0}))
    elif args.command == "verify":
        path = args.spec_path or ROOT / "SPEC.json"
        verify_inputs(read(path))
        print(json.dumps({"verified": str(path), "live_calls": 0}))
    elif args.command == "bind":
        if not args.weight or not args.endpoint_descriptor or not args.spec_path:
            parser.error("bind requires --weight --endpoint-descriptor --spec-path NEW.json")
        write_once(args.spec_path, bind_spec(args.weight, args.endpoint_descriptor))
        print(
            json.dumps(
                {
                    "bound_spec": str(args.spec_path),
                    "sha256": file_hash(args.spec_path),
                    "live_calls": 0,
                }
            )
        )
    else:
        if not args.spec_path or not args.output_dir:
            parser.error("run requires --spec-path --output-dir NEW_DIR")
        raise SystemExit(asyncio.run(run(args.spec_path, args.output_dir)))


if __name__ == "__main__":
    main()
