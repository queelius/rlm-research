"""Read all pinned MRCR rows; emit hashes/counts only, with no split or model calls."""

import ast
import hashlib
import json
import math
import platform
import re
import time
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import pyarrow
import pyarrow.parquet as pq
import tiktoken

ROOT = Path(__file__).resolve().parent
CACHE = Path("/project/alex_phd/research-cache/datasets/openai-mrcr-f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d")
REVISION = "f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d"
EXPECTED = {"2needle_0.parquet": "1c297b254bf64a31856b74918cd7db889a214503e0b67daa834e84f20df6aa93",
            "2needle_1.parquet": "a5a1dc9ccc945623253d04d33c03d89aee2d676c88955ce368da2ab16a0ce94d"}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def quantiles(values):
    values = sorted(values)
    return {str(q): values[min(len(values) - 1, max(0, math.ceil(q * len(values)) - 1))]
            for q in (0, .1, .25, .5, .75, .9, .95, .99, 1)} if values else {}


def components(incidences, count):
    parent = list(range(count))

    def find(index):
        while index != parent[index]:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for identifiers in incidences:
        identifiers = sorted(identifiers)
        if identifiers:
            first = find(identifiers[0])
            for identifier in identifiers[1:]:
                other = find(identifier)
                if other != first:
                    parent[other] = first
    groups = defaultdict(list)
    for index in range(count):
        groups[find(index)].append(index)
    values = sorted(groups.values(), key=lambda x: (-len(x), x))
    return {"count": len(values), "sizes": [len(value) for value in values],
            "row_ordinals": values}


def write_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main():
    started = time.monotonic()
    card = (CACHE / "README.md").read_text()
    code = re.search(r"```python\n(.*?)```", card, re.S).group(1)
    grade_node = next(node for node in ast.parse(code).body
                      if isinstance(node, ast.FunctionDef) and node.name == "grade")
    # Only the fully reviewed pure scoring function is evaluated; never the
    # dataset snippet's download, client constructor or network invocation.
    namespace = {"SequenceMatcher": SequenceMatcher}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[grade_node], type_ignores=[])),
                 "<reviewed-pinned-card-grade-only>", "exec"), namespace)
    grade = namespace["grade"]
    assert grade("markeranswer", "markeranswer", "marker") == 1
    assert grade("prefixmarkeranswer", "markeranswer", "marker") == 0
    assert grade("marker answer", "markeranswer", "marker") < 1
    enc = tiktoken.get_encoding("o200k_base")
    pairs, answers = defaultdict(set), defaultdict(set)
    pair_occurrences = Counter()
    rows, issues, schemas, files = [], [], {}, {}
    fewshots, cores, full_prompts, markers, target_answers, target_pairs = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    for path in sorted((CACHE / "2needle").glob("*.parquet")):
        checksum = sha(path)
        if checksum != EXPECTED[path.name]:
            raise ValueError("pinned HF LFS checksum differs")
        parquet = pq.ParquetFile(path)
        schemas[path.name] = str(parquet.schema_arrow)
        files[str(path)] = {"sha256": checksum, "bytes": path.stat().st_size,
                            "rows": parquet.metadata.num_rows, "row_groups": parquet.num_row_groups}
        source_row = 0
        for batch in parquet.iter_batches(batch_size=4):
            for raw in batch.to_pylist():
                ordinal = len(rows)
                messages = json.loads(raw["prompt"])
                expected_roles = ["user"] + [role for _ in range((len(messages) - 2) // 2)
                                             for role in ("user", "assistant")] + ["user"]
                valid_roles = [item.get("role") for item in messages] == expected_roles
                if not valid_roles:
                    issues.append({"row": ordinal, "kind": "role_pairing"})
                core = messages[1:-1]
                core_hash = digest(core)
                context_pairs = []
                for user, assistant in zip(core[::2], core[1::2], strict=True):
                    pair = digest([user, assistant])
                    context_pairs.append(pair)
                    pairs[pair].add(ordinal)
                    pair_occurrences[pair] += 1
                    answers[text_sha(assistant["content"])].add(ordinal)
                marker = raw["random_string_to_prepend"]
                answer_prefixed = raw["answer"].startswith(marker) and bool(marker)
                answer = raw["answer"].removeprefix(marker)
                desired = raw["desired_msg_index"]
                target_user_valid = (isinstance(desired, int) and desired % 2 == 1
                                     and 1 <= desired < len(messages) - 1
                                     and messages[desired]["role"] == "user")
                gold_match = target_user_valid and messages[desired + 1]["content"] == answer
                needle_positions = [index for index in range(1, len(messages) - 1, 2)
                                    if messages[index]["content"] == messages[desired]["content"]]
                normalized_needle_positions = [index for index in range(1, len(messages) - 1, 2)
                    if " ".join(messages[index]["content"].split())
                    == " ".join(messages[desired]["content"].split())]
                answer_hash = text_sha(answer)
                target_pair = digest(messages[desired:desired + 2])
                actual_chars = sum(len(item["content"]) for item in messages)
                checks = {"roles": valid_roles, "desired_index_is_core_user": target_user_valid,
                          "local_gold_equals_next_assistant": gold_match,
                          "answer_starts_with_marker": answer_prefixed,
                          "marker_alphanumeric": bool(re.fullmatch(r"[A-Za-z0-9]+", marker)),
                          "n_chars_is_sum_content": raw["n_chars"] == actual_chars,
                          "total_messages_matches": raw["total_messages"] == len(messages),
                          "n_needles_matches_exact_target_ask": raw["n_needles"] == len(needle_positions),
                          "n_needles_matches_whitespace_normalized": raw["n_needles"] == len(normalized_needle_positions),
                          "target_is_declared_needle": desired in needle_positions,
                          "official_gold_self_score_one": grade(raw["answer"], raw["answer"], marker) == 1}
                for key, passed in checks.items():
                    if not passed:
                        issues.append({"row": ordinal, "kind": key})
                fewshot_hash = digest(messages[0])
                fewshots[fewshot_hash] += 1
                cores[core_hash] += 1
                full_prompts[text_sha(raw["prompt"])] += 1
                markers[text_sha(marker)] += 1
                target_answers[answer_hash] += 1
                target_pairs[target_pair] += 1
                tokens = None
                if actual_chars <= 200000:
                    content_tokens = sum(len(enc.encode(item["content"], disallowed_special=()))
                                         for item in messages)
                    answer_tokens = len(enc.encode(raw["answer"], disallowed_special=()))
                    tokens = {"prompt_content": content_tokens, "answer": answer_tokens,
                              "prompt_content_plus_answer": content_tokens + answer_tokens}
                rows.append({"ordinal": ordinal, "shard": path.name, "source_row": source_row,
                             "row_sha256": digest(raw), "full_prompt_sha256": text_sha(raw["prompt"]),
                             "fewshot_sha256": fewshot_hash, "ordered_core_sha256": core_hash,
                             "final_question_sha256": digest(messages[-1]), "target_answer_sha256": answer_hash,
                             "target_pair_sha256": target_pair, "target_user_sha256": text_sha(messages[desired]["content"]),
                             "marker_sha256": text_sha(marker), "message_count": len(messages),
                             "core_pairs": len(context_pairs), "unique_core_pairs": len(set(context_pairs)),
                             "n_chars": actual_chars, "fewshot_chars": len(messages[0]["content"]),
                             "core_chars": sum(len(item["content"]) for item in core),
                             "answer_chars": len(answer), "desired_user_index": desired,
                             "needle_user_indices": needle_positions,
                             "target_occurrence_one_indexed": needle_positions.index(desired) + 1 if desired in needle_positions else None,
                             "n_needles": raw["n_needles"], "date_added": raw["date_added"],
                             "checks": checks, "o200k_base_tokens_if_short": tokens})
                source_row += 1
                if len(rows) % 100 == 0:
                    print(json.dumps({"parsed_rows": len(rows), "elapsed_seconds": time.monotonic() - started}), flush=True)
                if time.monotonic() - started > 540:
                    raise TimeoutError("bounded full inventory exceeded540 CPU seconds")
    if len(rows) != 800:
        raise ValueError("expected exact800 source records")
    for row in rows:
        ordinal = row["ordinal"]
        row["target_answer_other_core_rows"] = sorted(answers[row["target_answer_sha256"]] - {ordinal})
        row["target_pair_other_core_rows"] = sorted(pairs[row["target_pair_sha256"]] - {ordinal})
    short = [row for row in rows if row["o200k_base_tokens_if_short"]]
    all_pairs = sum(row["core_pairs"] for row in rows)
    shared_pairs = {key: value for key, value in pairs.items() if len(value) > 1}
    report = {"schema": "openai-mrcr-all800-hash-inventory-v1", "revision": REVISION,
        "source_url": f"https://huggingface.co/datasets/openai/mrcr/tree/{REVISION}/2needle",
        "distinct_from": "Google DeepMind MRCRv2.1 CSV; scorer conventions must not be substituted",
        "license": "MIT declared by pinned dataset card; no separate license file acquired",
        "files": files, "card_sha256": sha(CACHE / "README.md"), "schemas": schemas,
        "rows": len(rows), "unique_ordered_core_contexts": len(cores),
        "unique_full_prompt_bytes": len(full_prompts), "fewshot_frequency": dict(fewshots),
        "unique_markers": len(markers), "date_added_counts": dict(Counter(row["date_added"] for row in rows)),
        "needle_counts": dict(Counter(row["n_needles"] for row in rows)),
        "target_occurrence_counts": dict(Counter(row["target_occurrence_one_indexed"] for row in rows)),
        "check_failure_counts": dict(Counter(issue["kind"] for issue in issues)), "issues": issues,
        "length_quantiles": {key: quantiles([row[key] for row in rows]) for key in
                             ("n_chars", "core_chars", "message_count", "core_pairs", "answer_chars", "fewshot_chars")},
        "character_threshold_counts": {str(cap): sum(row["n_chars"] <= cap for row in rows)
                                       for cap in (20000, 40000, 80000, 120000, 200000, 1000000)},
        "core_pairs": {"total_occurrences": all_pairs, "unique_exact_pairs": len(pairs),
                       "pairs_in_multiple_rows": len(shared_pairs),
                       "unique_pairs_per_row_incidence_histogram": dict(Counter(len(value) for value in pairs.values())),
                       "occurrences_of_shared_pairs": sum(pair_occurrences[key] for key in shared_pairs),
                       "rows_with_repeated_exact_pair_internally": sum(row["core_pairs"] != row["unique_core_pairs"] for row in rows)},
        "target_reuse": {"unique_target_answers": len(target_answers), "unique_target_pairs": len(target_pairs),
                         "target_answer_frequency_histogram": dict(Counter(target_answers.values())),
                         "rows_target_answer_appears_in_other_core": sum(bool(row["target_answer_other_core_rows"]) for row in rows),
                         "rows_target_pair_appears_in_other_core": sum(bool(row["target_pair_other_core_rows"]) for row in rows),
                         "target_answer_other_context_count_quantiles": quantiles([len(row["target_answer_other_core_rows"]) for row in rows])},
        "core_pair_overlap_components": components(pairs.values(), len(rows)),
        "target_answer_exposure_components": components((answers[key] for key in target_answers), len(rows)),
        "short_candidates": {"criterion": "sum message-content characters<=200000", "rows": len(short),
            "encoding": "o200k_base", "chat_template_overhead_included": False,
            "prompt_tokens_quantiles": quantiles([row["o200k_base_tokens_if_short"]["prompt_content"] for row in short]),
            "prompt_plus_answer_tokens_quantiles": quantiles([row["o200k_base_tokens_if_short"]["prompt_content_plus_answer"] for row in short]),
            "prompt_plus_answer_token_threshold_counts": {str(cap): sum(row["o200k_base_tokens_if_short"]["prompt_content_plus_answer"] <= cap for row in short)
                                                         for cap in (8192, 16384, 32768, 65536)},
            "not_actual_Qwen_chat_context_budget": True},
        "scorer": {"card_python_block_sha256": text_sha(code), "grade_function_ast_sha256": digest(ast.dump(grade_node)),
                   "requires_prefix_at_response_start": True, "removes_prefix_once": True,
                   "whitespace_strip_or_normalization": False, "metric": "difflib.SequenceMatcher(None,response,answer).ratio()",
                   "reviewed_pure_grade_fixture_passed": True, "network_client_code_executed": False},
        "runtime": {"python": platform.python_version(), "pyarrow": pyarrow.__version__, "tiktoken": tiktoken.__version__,
                    "elapsed_seconds": time.monotonic() - started, "GPU_or_model_queries": 0},
        "claim_boundary": "exact hashes do not establish semantic independence or base-pretraining exclusion; no split designated"}
    write_json(ROOT / "INVENTORY.json", report)
    with (ROOT / "ROWS.jsonl").open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    with (ROOT / "CORE_PAIR_INCIDENCE.jsonl").open("x") as stream:
        for key, value in sorted(pairs.items()):
            stream.write(json.dumps({"pair_sha256": key, "row_ordinals": sorted(value),
                                     "occurrences": pair_occurrences[key]}, sort_keys=True) + "\n")
    with (ROOT / "TARGET_ANSWER_INCIDENCE.jsonl").open("x") as stream:
        for key, count in sorted(target_answers.items()):
            stream.write(json.dumps({"answer_sha256": key, "target_rows_count": count,
                                     "core_row_ordinals": sorted(answers[key])}, sort_keys=True) + "\n")
    write_json(ROOT / "MANIFEST.json", {"source_files": files, "source_revision": REVISION,
        "source_card_sha256": sha(CACHE / "README.md"), "inventory_source_sha256": sha(__file__),
        "artifacts_sha256": {str(ROOT / name): sha(ROOT / name) for name in
                              ("INVENTORY.json", "ROWS.jsonl", "CORE_PAIR_INCIDENCE.jsonl", "TARGET_ANSWER_INCIDENCE.jsonl")},
        "raw_answers_published": False, "training_split_created": False, "GPU_queries": 0})
    print(json.dumps({"rows": len(rows), "unique_contexts": len(cores), "issues": len(issues),
                      "seconds": time.monotonic() - started, "manifest_sha256": sha(ROOT / "MANIFEST.json")}), flush=True)


if __name__ == "__main__":
    main()
