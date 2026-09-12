"""Freeze one outcome-blind, mutually disjoint 16K--32K OpenAI MRCR cohort."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parent.parent
INVENTORY = STORE / "analyses/openai-mrcr-source-inventory-2026-09-12"
SHORT = ROOT.parent / "openai-mrcr-short-root-data-v1"
CACHE = Path(
    "/project/alex_phd/research-cache/datasets/"
    "openai-mrcr-f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d"
)
NAMESPACE = "mrcr-long-transfer-20260912"
LOW = 16384
HIGH = 32768
COUNT = 16


def read(path: Path):
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_bytes(path: Path, value: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(value)


def write_json(path: Path, value, mode: int = 0o644) -> None:
    write_bytes(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(),
        mode,
    )


def load_inventory():
    manifest = read(INVENTORY / "MANIFEST.json")
    for path, expected in manifest["artifacts_sha256"].items():
        if sha(Path(path)) != expected:
            raise ValueError("pinned inventory changed: " + path)
    rows = {
        row["ordinal"]: row
        for row in map(json.loads, (INVENTORY / "ROWS.jsonl").read_text().splitlines())
    }
    incidences = [
        set(row["row_ordinals"])
        for row in map(
            json.loads,
            (INVENTORY / "CORE_PAIR_INCIDENCE.jsonl").read_text().splitlines(),
        )
    ]
    if len(rows) != 800:
        raise ValueError("expected exact 800-row inventory")
    return rows, incidences


def load_exposed() -> set[int]:
    value = read(SHORT / "MODEL_INPUTS_V2.json")
    exposed = {row["source_ordinal"] for split in value.values() for row in split}
    if len(exposed) != 48:
        raise ValueError("expected exact 48 previously queried short records")
    return exposed


def rank_sha(row: dict) -> str:
    return sha_text(NAMESPACE + "|" + row["row_sha256"])


def _neighbors(incidences: list[set[int]], count: int = 800):
    values = {index: set() for index in range(count)}
    for incidence in incidences:
        for index in incidence:
            values[index].update(incidence - {index})
    return values


def _target_crosses(left: int, right: int, rows: dict[int, dict]) -> bool:
    return (
        right in set(rows[left]["target_answer_other_core_rows"])
        or left in set(rows[right]["target_answer_other_core_rows"])
    )


def audit_selected(selected, rows, incidences, exposed) -> list[dict]:
    neighbors = _neighbors(incidences, len(rows))
    issues = []
    ordinals = [row["ordinal"] for row in selected]
    for ordinal in ordinals:
        tokens = rows[ordinal]["o200k_base_tokens_if_short"]["prompt_content_plus_answer"]
        if not LOW <= tokens <= HIGH:
            issues.append({"ordinal": ordinal, "kind": "outside_token_band"})
        if ordinal in exposed:
            issues.append({"ordinal": ordinal, "kind": "direct_prior_exposure"})
        if neighbors[ordinal] & exposed:
            issues.append({"ordinal": ordinal, "kind": "core_pair_overlap_with_exposed"})
        if set(rows[ordinal]["target_answer_other_core_rows"]) & exposed:
            issues.append({"ordinal": ordinal, "kind": "target_answer_in_exposed_core"})
        if any(ordinal in set(rows[item]["target_answer_other_core_rows"]) for item in exposed):
            issues.append({"ordinal": ordinal, "kind": "exposed_target_answer_in_candidate_core"})
    for position, left in enumerate(ordinals):
        for right in ordinals[position + 1 :]:
            if right in neighbors[left]:
                issues.append({"left": left, "right": right, "kind": "selected_core_pair_overlap"})
            if _target_crosses(left, right, rows):
                issues.append({"left": left, "right": right, "kind": "selected_target_core_cross"})
    return issues


def select_rows(rows: dict[int, dict], incidences: list[set[int]], exposed: set[int]):
    neighbors = _neighbors(incidences, len(rows))
    band = [
        ordinal
        for ordinal, row in rows.items()
        if row.get("o200k_base_tokens_if_short")
        and LOW <= row["o200k_base_tokens_if_short"]["prompt_content_plus_answer"] <= HIGH
    ]
    exclusion_counts = {
        "direct_prior_exposure": sum(ordinal in exposed for ordinal in band),
        "core_pair_overlap_with_exposed": sum(bool(neighbors[ordinal] & exposed) for ordinal in band),
        "candidate_target_answer_in_exposed_core": sum(
            bool(set(rows[ordinal]["target_answer_other_core_rows"]) & exposed) for ordinal in band
        ),
        "exposed_target_answer_in_candidate_core": sum(
            any(ordinal in set(rows[item]["target_answer_other_core_rows"]) for item in exposed)
            for ordinal in band
        ),
    }
    eligible = [
        ordinal
        for ordinal in band
        if ordinal not in exposed
        and not neighbors[ordinal] & exposed
        and not set(rows[ordinal]["target_answer_other_core_rows"]) & exposed
        and not any(ordinal in set(rows[item]["target_answer_other_core_rows"]) for item in exposed)
    ]
    ranked = sorted(eligible, key=lambda ordinal: (rank_sha(rows[ordinal]), rows[ordinal]["row_sha256"]))
    selected = []
    for ordinal in ranked:
        if any(
            prior in neighbors[ordinal] or _target_crosses(ordinal, prior, rows)
            for prior in selected
        ):
            continue
        selected.append(ordinal)
        if len(selected) == COUNT:
            break
    values = [
        {
            "ordinal": ordinal,
            "row_sha256": rows[ordinal]["row_sha256"],
            "rank_sha256": rank_sha(rows[ordinal]),
            "prompt_plus_answer_o200k": rows[ordinal]["o200k_base_tokens_if_short"][
                "prompt_content_plus_answer"
            ],
            "source_shard": rows[ordinal]["shard"],
            "source_row": rows[ordinal]["source_row"],
        }
        for ordinal in selected
    ]
    issues = audit_selected(values, rows, incidences, exposed)
    if issues:
        raise ValueError("selected cohort failed disjointness audit: " + repr(issues))
    return {
        "counts": {
            "source": len(rows),
            "band": len(band),
            "exposed": len(exposed),
            "eligible_after_exposure_exclusions": len(eligible),
            "selected": len(values),
        },
        "exclusion_counts_not_mutually_exclusive": exclusion_counts,
        "selected": values,
    }


def _raw_rows(selected: list[dict], inventory_rows: dict[int, dict]):
    wanted = {row["ordinal"] for row in selected}
    result = {}
    ordinal = 0
    source_manifest = read(INVENTORY / "MANIFEST.json")
    for path in sorted((CACHE / "2needle").glob("*.parquet")):
        if sha(path) != source_manifest["source_files"][str(path)]["sha256"]:
            raise ValueError("pinned source parquet changed")
        for batch in pq.ParquetFile(path).iter_batches(batch_size=8):
            for raw in batch.to_pylist():
                if digest(raw) != inventory_rows[ordinal]["row_sha256"]:
                    raise ValueError("source row differs from inventory")
                if ordinal in wanted:
                    result[ordinal] = raw
                ordinal += 1
    if ordinal != 800 or set(result) != wanted:
        raise ValueError("selected raw source inventory incomplete")
    return result


def materialize(selected: list[dict], destination: Path):
    inventory_rows, _ = load_inventory()
    raw_rows = _raw_rows(selected, inventory_rows)
    public, gold = [], {}
    for selected_row in selected:
        ordinal = selected_row["ordinal"]
        raw = raw_rows[ordinal]
        messages = json.loads(raw["prompt"])
        desired = raw["desired_msg_index"]
        if (
            [message.get("role") for message in messages]
            != ["user"]
            + [role for _ in range((len(messages) - 2) // 2) for role in ("user", "assistant")]
            + ["user"]
            or desired % 2 != 1
            or messages[desired + 1]["content"]
            != raw["answer"].removeprefix(raw["random_string_to_prepend"])
        ):
            raise ValueError("selected official row schema/target differs")
        target = messages[desired]["content"]
        positions = [
            index
            for index in range(1, len(messages) - 1, 2)
            if messages[index]["content"] == target
        ]
        target_ordinal = positions.index(desired) + 1
        identifier = "omrcr-long-" + selected_row["row_sha256"][:20]
        folder = Path(destination) / "records" / identifier
        prompt_bytes = raw["prompt"].encode()
        question_bytes = messages[-1]["content"].encode()
        write_bytes(folder / "prompt.json", prompt_bytes)
        write_bytes(folder / "question.txt", question_bytes)
        public.append(
            {
                "id": identifier,
                "source_ordinal": ordinal,
                "source_shard": inventory_rows[ordinal]["shard"],
                "source_row": inventory_rows[ordinal]["source_row"],
                "source_row_sha256": inventory_rows[ordinal]["row_sha256"],
                "ordered_core_sha256": inventory_rows[ordinal]["ordered_core_sha256"],
                "target_pair_sha256": inventory_rows[ordinal]["target_pair_sha256"],
                "target_answer_sha256": inventory_rows[ordinal]["target_answer_sha256"],
                "target_occurrence_one_indexed": target_ordinal,
                "n_needles": raw["n_needles"],
                "message_count": len(messages),
                "prompt_json_path": str(folder / "prompt.json"),
                "prompt_json_sha256": sha(folder / "prompt.json"),
                "prompt_json_bytes": len(prompt_bytes),
                "final_question_path": str(folder / "question.txt"),
                "final_question_sha256": sha(folder / "question.txt"),
                "prompt_content_o200k_tokens": inventory_rows[ordinal][
                    "o200k_base_tokens_if_short"
                ]["prompt_content"],
                "answer_o200k_tokens": inventory_rows[ordinal]["o200k_base_tokens_if_short"][
                    "answer"
                ],
                "prompt_plus_answer_o200k_tokens": inventory_rows[ordinal][
                    "o200k_base_tokens_if_short"
                ]["prompt_content_plus_answer"],
                "external_context_representation": "original JSON list of official messages",
                "external_file_length_is_not_neural_root_prompt_length": True,
                "no_added_needle_answer_parser_or_position_hint": True,
            }
        )
        gold[identifier] = {
            "answer": raw["answer"],
            "random_string_to_prepend": raw["random_string_to_prepend"],
            "desired_msg_index": desired,
            "target_occurrence_one_indexed": target_ordinal,
            "source_row_sha256": inventory_rows[ordinal]["row_sha256"],
        }
    return {"schema": "openai-mrcr-long-transfer-public-inputs-v1", "records": public}, gold


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (ROOT / "DATA_READY.json").exists():
        raise ValueError("unused CPU-only data freeze required")
    rows, incidences = load_inventory()
    exposed = load_exposed()
    selection = select_rows(rows, incidences, exposed)
    if selection["counts"]["selected"] != COUNT:
        write_json(
            ROOT / "FEASIBILITY.json",
            {
                "schema": "openai-mrcr-long-transfer-feasibility-v1",
                "status": "INFEASIBLE_WITHOUT_CHANGING_COHORT",
                **selection,
            },
        )
        raise ValueError("fewer than 16 rows satisfy the frozen cohort")
    write_json(
        ROOT / "RANKING.json",
        {
            "schema": "openai-mrcr-long-transfer-ranking-v1",
            "namespace": NAMESPACE,
            "inclusive_o200k_prompt_plus_answer_band": [LOW, HIGH],
            "selection_uses_model_answers": False,
            "selection_uses_previous_outcomes": False,
            "selection_rule": "hash rank eligible rows, then greedily accept pair/target-disjoint rows",
            **selection,
        },
    )
    public, gold = materialize(selection["selected"], ROOT / "inputs")
    write_json(ROOT / "MODEL_INPUTS.json", public)
    host = ROOT / "host"
    host.mkdir(mode=0o700)
    write_json(host / "HOST_GOLD.json", gold, mode=0o600)
    if stat.S_IMODE(host.stat().st_mode) != 0o700 or stat.S_IMODE(
        (host / "HOST_GOLD.json").stat().st_mode
    ) != 0o600:
        raise ValueError("host truth permissions differ")

    grader_source = SHORT / "official_score.py"
    write_bytes(ROOT / "official_score.py", grader_source.read_bytes())
    if sha(ROOT / "official_score.py") != sha(grader_source):
        raise ValueError("official scorer bytes changed")
    source_manifest = read(INVENTORY / "MANIFEST.json")
    sources = {
        str(INVENTORY / "MANIFEST.json"): sha(INVENTORY / "MANIFEST.json"),
        str(INVENTORY / "ROWS.jsonl"): sha(INVENTORY / "ROWS.jsonl"),
        str(INVENTORY / "CORE_PAIR_INCIDENCE.jsonl"): sha(
            INVENTORY / "CORE_PAIR_INCIDENCE.jsonl"
        ),
        str(SHORT / "MODEL_INPUTS_V2.json"): sha(SHORT / "MODEL_INPUTS_V2.json"),
        str(CACHE / "README.md"): sha(CACHE / "README.md"),
    }
    sources.update({path: value["sha256"] for path, value in source_manifest["source_files"].items()})
    generated = [ROOT / "RANKING.json", ROOT / "MODEL_INPUTS.json", ROOT / "official_score.py"]
    generated += [Path(row[key]) for row in public["records"] for key in ("prompt_json_path", "final_question_path")]
    manifest = {
        "schema": "openai-mrcr-long-transfer-data-manifest-v1",
        "status": "DATA_ONLY_NO_MODEL_QUERY_OR_EVALUATOR_ADMISSION",
        "source_dataset": "openai/mrcr 2needle",
        "source_revision": "f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d",
        "source_url": "https://huggingface.co/datasets/openai/mrcr/tree/f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d/2needle",
        "license": "MIT declared by pinned dataset card; no separate dataset license file acquired",
        "namespace": NAMESPACE,
        "records": COUNT,
        "source_rows": 800,
        "previously_queried_short_rows_excluded": 48,
        "pairwise_exact_core_pair_overlap": 0,
        "pairwise_target_answer_to_other_core_overlap_both_directions": 0,
        "o200k_band": {"inclusive_min": LOW, "inclusive_max": HIGH},
        "common_fewshot_retained": True,
        "unknown_base_pretraining_exposure": True,
        "root_runtime_context_limit_tokens": 8192,
        "external_context_is_file_not_neural_prompt": True,
        "later_comparison": "fixed base versus checkpoint32, one fresh seed per record",
        "later_owner_cap_seconds_each_provisional": 900,
        "terminal_parser_condition": "must be fixed after experiment-scoped fidelity repair",
        "model_queries": 0,
        "optimizer_steps": 0,
        "host_gold_mode": "0600",
        "files_sha256": {str(path): sha(path) for path in generated},
        "host_gold_sha256": sha(host / "HOST_GOLD.json"),
        "source_sha256": sources,
        "claim_boundary": "same-task long-input transfer prerequisite, not broad generalization, new decomposition, or pretraining exclusion",
    }
    write_json(ROOT / "MANIFEST.json", manifest)
    ready = {
        "schema": "openai-mrcr-long-transfer-data-ready-v1",
        "status": "DATA_ONLY_NO_GPU_OR_EVALUATOR",
        "manifest_sha256": sha(ROOT / "MANIFEST.json"),
        "records": COUNT,
        "closure_sha256": {
            **manifest["files_sha256"],
            **sources,
            str(host / "HOST_GOLD.json"): sha(host / "HOST_GOLD.json"),
            str(ROOT / "MANIFEST.json"): sha(ROOT / "MANIFEST.json"),
        },
    }
    ready["identity"] = digest(ready)
    write_json(ROOT / "DATA_READY.json", ready)
    print(
        json.dumps(
            {
                "data_ready_sha256": sha(ROOT / "DATA_READY.json"),
                "identity": ready["identity"],
                "counts": selection["counts"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

