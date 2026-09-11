"""CPU-only native admission and immutable READY seal."""

import asyncio
import hashlib
from pathlib import Path

import study as s


class Memory:
    def __init__(self):
        self.files = {}

    async def write(self, name, data):
        self.files[name] = data


async def setup_files(task):
    memory = Memory()
    await task.setup(None, memory)
    return memory.files


def main():
    if (s.ROOT / "READY.json").exists() or (s.ROOT / "inputs/PROMPTS_ACCURATE.json").exists():
        raise FileExistsError("seal is one-time and non-rerolling")
    plan = s.read(s.ROOT / "inputs/FREE_PLAN.json")
    contexts = {row["id"]: row for row in s.read(s.ROOT / "inputs/PUBLIC.json")}
    host = s.read(s.ROOT / "inputs/HOST_GOLD.json")
    prompts = {}
    checks = []
    native = s.base.base.qnative()
    for row in plan:
        context = contexts[row["context_id"]]
        gold = host[row["context_id"]]["answers"]["J1"]
        task = s.make_task(context, row, gold)
        other = s.make_task(context, row, gold + 1000003)
        prefix = native.first_prefix(task)
        other_prefix = native.first_prefix(other)
        actual = asyncio.run(setup_files(task))
        changed = asyncio.run(setup_files(other))
        if prefix != other_prefix or actual != changed:
            raise ValueError("private gold changed public prompt or setup files")
        required = {
            "records.json",
            "context.txt",
            "query.txt",
            "batch_contract.py",
            ".observation_view.json",
        }
        if set(actual) != required:
            raise ValueError("exact five-file native public interface changed")
        if len(prefix) + 2048 > 8192:
            raise ValueError("native 8192-token admission failed; no reranking")
        prompts[row["id"]] = {
            "prompt": task.data.prompt,
            "plain_query": row["question"],
            "token_ids": prefix,
            "prefix_tokens": len(prefix),
            "files_sha256": {
                name: hashlib.sha256(value).hexdigest() for name, value in sorted(actual.items())
            },
            "gold_independent": True,
        }
        checks.append(
            {
                "id": row["id"],
                "cluster": row["cluster"],
                "size": row["size"],
                "policy": row["policy"],
                "harness_arm": row["harness_arm"],
                "prefix_tokens": len(prefix),
                "gold_independent": True,
                "exact_five_files": True,
            }
        )
    s.write(s.ROOT / "inputs/PROMPTS_ACCURATE.json", prompts)
    s.write(
        s.ROOT / "CPU_INPUT_NATIVE.json",
        {
            "rows": checks,
            "contexts": 16,
            "groups": 1024,
            "planned": 64,
            "min_prefix_tokens": min(row["prefix_tokens"] for row in checks),
            "max_prefix_tokens": max(row["prefix_tokens"] for row in checks),
            "scientific_gpu_calls": 0,
        },
    )
    local_sources = [
        s.ROOT / name
        for name in (
            "DESIGN.md",
            "PLAN.md",
            "prepare.py",
            "seal.py",
            "study.py",
            "collect.py",
            "owner.py",
            "test_prepare.py",
            "test_inputs.py",
            "test_runtime.py",
        )
    ]
    dependencies = [
        s.QS_REPLICATION / "READY.json",
        s.QS_REPLICATION / "study.py",
        s.QS / "qs_problem.py",
        s.AE / "READY.json",
        s.AE / "ae_protocol.py",
        s.AE / "decoder_tail.py",
        s.BV / "READY_v2.json",
        s.BV / "bv_overlay_v2.py",
        s.SIDE / "trec-leaf-sft-v1/source/data.py",
        s.SIDE / "trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json",
        s.SIDE / "trec-leaf-split-provenance-v1/INVENTORY.json",
    ]
    provenance = s.read(s.ROOT / "inputs/PROVENANCE.json")
    dependencies.append(Path(provenance["named_manifest_rows"][0]["path"]))
    # Pin the authenticated raw source path carried by the split revision when present.
    source_path = Path(
        s.read(s.ROOT / "inputs/PROVENANCE.json")["dataset_revision"]["source_train"][0][
            "source_path"
        ]
    ) if "source_path" in s.read(s.ROOT / "inputs/PROVENANCE.json")["dataset_revision"]["source_train"][0] else Path(
        "/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv/train_5500.label"
    )
    if source_path.exists():
        dependencies.append(source_path)
    license_path = Path(
        "/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv/oolong__LICENSE"
    )
    if license_path.exists():
        dependencies.append(license_path)
    sources = {str(path): s.sha(path) for path in [*local_sources, *dependencies]}
    inputs = {
        str(path): s.sha(path)
        for path in sorted((s.ROOT / "inputs").glob("*.json"))
    }
    ready = {
        "schema": "root-qs-scale-harness-factorial-ready-v1",
        "source_sha256": sources,
        "input_sha256": inputs,
        "planned": 64,
        "contexts": 16,
        "selected_groups": 1024,
        "policies": ["sft6", "unchanged"],
        "harness_arms": ["raw_batch_20000b", "cumulative_4096b"],
        "scientific_gpu_calls": 0,
        "gpu_launch_authority": "MAIN only",
        "outer_seconds": 3600,
        "owned_seconds": 3570,
        "work_seconds": 3420,
        "no_retry": True,
        "new_training": False,
    }
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY.json", ready)
    print(
        {
            "identity": ready["identity"],
            "planned": 64,
            "max_prefix_tokens": max(row["prefix_tokens"] for row in checks),
        }
    )


if __name__ == "__main__":
    main()
