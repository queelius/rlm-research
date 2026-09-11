"""Schema-only intervention over frozen singleton/whole-context leaf requests."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / "fixed-leaf-batch-extremes-v1"
BASE = ROOT.parent / "fixed-leaf-composition-v1/driver.py"
BASE_SHA = "9afd6c5d5219a6705c79839e99a87ca45e50c84fc7bdff197c97482f6cd8387a"
PARENT_SHA = {
    64: "ed3056e2e9e058ea26ed73309de8963a288ecf813ea47ac5a0bf807f1fa7e297",
    1: "6df7e55fd29eb7f26f9d6ce2d5d83b80b6199e55aa3b2dec6a1fcec6ea3273ee",
}
if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError("authenticated fixed leaf collector changed")
loader = importlib.util.spec_from_file_location("schema_owned_fixed_leaf_helpers", BASE)
fixed = importlib.util.module_from_spec(loader)
loader.loader.exec_module(fixed)
original_request = fixed.make_request


def make_request(design: dict, row: dict) -> dict:
    return fixed.leaf.make_request(design, {**row, "arm": "both"}, fixed.ALIASES[row["arm"]])


# Override only this independently loaded module's request callback, not its file.
fixed.make_request = make_request


def make_spec(size: int) -> dict:
    if size not in PARENT_SHA:
        raise ValueError("supported batch sizes are1 and64")
    path = PARENT / f"SPEC-B{size:03d}.json"
    if fixed.leaf.file_hash(path) != PARENT_SHA[size]:
        raise ValueError("frozen unconstrained comparison specification changed")
    spec = json.loads(path.read_text())
    fixed.make_request = original_request
    try:
        fixed.verify_inputs(spec)
    finally:
        fixed.make_request = make_request
    spec.update(
        schema=ROOT.name,
        parent_spec_path=str(path),
        parent_spec_sha256=PARENT_SHA[size],
        intervention="Exact-cardinality canonical-enum schema only; original arm='both' builder",
        primary_failure_policy="Unchanged strict first-response score; no repair or fallback",
        request_sha256={
            row["id"]: fixed.leaf.digest(make_request(spec["design"], row))
            for row in spec["design"]["plan"]
        },
        contract_caution="Schema-constrained fixed operator; not unconstrained full-RLM behavior",
    )
    spec["source_file_sha256"].update(
        {
            str(p): fixed.leaf.file_hash(p)
            for p in [Path(__file__), ROOT / "test_driver.py", ROOT / "DESIGN.md", path]
        }
    )
    fixed.verify_inputs(spec)
    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "preflight", "run"))
    parser.add_argument("--size", type=int, choices=(1, 64), required=True)
    args = parser.parse_args()
    path = ROOT / f"SPEC-B{args.size:03d}.json"
    spec = make_spec(args.size)
    if args.command == "prepare":
        fixed.leaf.write_once(path, spec)
    elif json.loads(path.read_text()) != spec:
        raise ValueError("frozen schema intervention changed")
    if args.command == "run":
        fixed.ROOT = ROOT
        raise SystemExit(
            asyncio.run(fixed.run(path, ROOT / "outputs" / f"batch{args.size:03d}-attempt-001"))
        )
    print(
        json.dumps(
            {
                "planned_calls": len(spec["design"]["plan"]),
                "spec_sha256": fixed.leaf.file_hash(path),
                "gpu_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
