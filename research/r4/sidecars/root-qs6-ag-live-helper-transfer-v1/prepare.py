"""CPU-only, outcome-blind freeze of fresh official AG content; no model calls."""

from collections import Counter
import copy
import hashlib
import os

import protocol
import study


def build():
    import pyarrow.parquet as pq
    from transformers import AutoTokenizer

    source = study.load("ag_live_official_data_builder", study.DATA_SOURCE / "prepare.py")
    if study.sha(source.PARQUET) != source.PARQUET_SHA:
        raise ValueError("official test cache hash differs")
    manifest = study.INPUTS / "MANIFEST.json"
    if manifest.exists():
        # Rebuild from the exact freeze-time exclusion snapshot, not later adaptive work.
        sources = study.read(manifest)["canonical_exposure_files"]
        found = []
        for path, receipt in sources.items():
            if study.sha(path) != receipt["sha256"]:
                raise ValueError("frozen exclusion input changed: " + path)
            source.extract(study.read(path), found)
        exposed_ids = {row["source_id"] for row in found if isinstance(row.get("source_id"), str)}
        exposed_norms = {normalizer(row["text"]) for row in found for normalizer in (source.whitespace, source.word)}
    else:
        exposed_ids, exposed_norms, sources = source.exposure_inventory()
    # Source builder excludes its own sidecar. This new task explicitly excludes it.
    official_path = study.DATA_SOURCE / "inputs/PUBLIC.json"
    for row in study.read(official_path)["records"]:
        exposed_ids.add(row["source_id"])
        exposed_norms.update((source.whitespace(row["text"]), source.word(row["text"])))
    sources[str(official_path)] = {"sha256": study.sha(official_path)}
    raw = pq.read_table(source.PARQUET, columns=["text", "label"]).to_pylist()
    groups = Counter(source.word(row["text"]) for row in raw)
    pool = [dict(source_id=f"test:{index}", source_row_0based=index, **row)
            for index, row in enumerate(raw)
            if groups[source.word(row["text"])] == 1
            and f"test:{index}" not in exposed_ids
            and source.word(row["text"]) not in exposed_norms
            and source.whitespace(row["text"]) not in exposed_norms]
    ranked = lambda key, row: study.digest([study.NAMESPACE, key, row["source_id"]])
    selected = []
    for label in range(4):
        eligible = sorted((row for row in pool if row["label"] == label), key=lambda row: ranked("select", row))
        if len(eligible) < 32:
            raise ValueError("insufficient fresh test remainder; no replacement source")
        selected.extend(eligible[:32])
    selected.sort(key=lambda row: ranked("group-order", row))
    contexts, provenance, gold, plans, requests = [], [], {}, {arm: [] for arm in study.ARMS}, {}
    tokenizer = AutoTokenizer.from_pretrained(source.MODEL, local_files_only=True)
    old = study.read(source.BATCH_SOURCES)["contexts"]["question-sensitive-sft-train-05"]["partitions"]["4"]["0"]
    text_ids = tokenizer.encode(old["request_text"], add_special_tokens=False)
    body = old["body"]
    hits = [i for i in range(len(body["token_ids"]) - len(text_ids) + 1)
            if body["token_ids"][i:i + len(text_ids)] == text_ids]
    if len(hits) != 1:
        raise ValueError("qualified helper message/token boundary differs")
    prefix = body["token_ids"][:hits[0]]
    suffix = body["token_ids"][hits[0] + len(text_ids):]
    builder = source.load_builder()
    for ci in range(8):
        cid = f"ag-live-fresh-{ci:02}"
        members = selected[ci * 16:ci * 16 + 16]
        public, labels = [], {}
        for index, row in enumerate(members):
            identifier = "agrt" + ranked("id", row)[:16]
            record = {"id": identifier, "user": f"u{index % 4}", "text": row["text"],
                      "weight": 1 + int(ranked("weight", row)[:8], 16) % 7}
            public.append(record)
            labels[identifier] = protocol.LABELS[row["label"]]
            provenance.append({"id": identifier, "context_id": cid, "dataset": "ag_news",
                "source_id": row["source_id"], "source_row_0based": row["source_row_0based"],
                "text_sha256": hashlib.sha256(row["text"].encode()).hexdigest(), "label": row["label"]})
        context = {"id": cid, "index": ci, "size": 16, "stratum": "official-ag-fresh",
                   "native_context_id": 202609131700 + ci, "records": public,
                   "text": "".join(__import__("json").dumps(row, ensure_ascii=False) + "\n" for row in public)}
        contexts.append(context)
        gold[cid] = {"labels": labels, "answers": {}}
        requests[cid] = []
        for bi in range(4):
            batch = public[bi * 4:bi * 4 + 4]
            text = protocol.request_for(batch)
            if (text, protocol.LABELS) != builder.prompt("ag_news", batch):
                raise ValueError("canonical learned helper prompt or definition changed")
            ids = [row["id"] for row in batch]
            schema = protocol.schema(ids)
            sampling = copy.deepcopy(body["sampling_params"])
            sampling.update(temperature=0.0, seed=study.HELPER_SEED + ci * 8 + bi,
                            max_tokens=1024, structured_outputs={"json": schema})
            native = {"model": source.CHILD_ALIAS,
                      "token_ids": prefix + tokenizer.encode(text, add_special_tokens=False) + suffix,
                      "sampling_params": sampling, "cache_salt": "0"}
            if len(native["token_ids"]) + 1024 > 8192:
                raise ValueError("B4 prompt/output exceeds8192; no rerank")
            requests[cid].append({"call_id": study.digest([study.NAMESPACE, cid, bi]),
                "dataset": "ag_news", "start": bi * 4, "ids": ids, "request_text": text,
                "schema_ordered_json": __import__("json").dumps(schema, separators=(",", ":")), "body": native})
        for qi, operator in enumerate(("count", "weight_sum")):
            spec = {"operator": operator, "target": protocol.LABELS[(ci + qi) % 4]}
            pair = {"context_id": cid, "query_index": qi, **spec,
                    "question": protocol.question(spec), "seed": study.ROOT_SEED + 2 * ci + qi,
                    "context_window_id": context["native_context_id"], "temperature": .5,
                    "family": operator, "repeat": 0, "arm": "typed", "client_path": "train"}
            gold[cid]["answers"][operator] = protocol.aggregate(public, labels, spec)
            for arm in study.ARMS:
                row = {**pair, "pair_id": study.digest(pair), "arm": arm}
                row["id"] = study.digest([study.NAMESPACE, row])
                plans[arm].append(row)
    # Serial per-phase schedule is label-blind; root seeds paired across three arms.
    report = {"source_revision": source.REVISION, "source_parquet_sha256": source.PARQUET_SHA,
        "eligible": len(pool), "eligible_per_label": dict(Counter(row["label"] for row in pool)),
        "selected_records": 128, "selected_per_label": dict(Counter(row["label"] for row in selected)),
        "contexts": 8, "records_per_context": 16, "questions_per_context": 2, "episodes": 48,
        "class_balance_scope": "whole128 only; never within context", "grouping_uses_gold": False,
        "selection_uses_model_outcomes": False, "normalization": "NFKC casefold whitespace and word tokens",
        "canonical_exposure_files": sources, "exposed_source_id_overlap": 0, "normalized_overlap": 0,
        "full_context_max_token_length": max(len(tokenizer.encode(c["text"], add_special_tokens=False)) for c in contexts),
        "max_B4_prompt_plus_1024": max(len(row["body"]["token_ids"]) + 1024 for rows in requests.values() for row in rows),
        "base_pretraining_exposure": "unknown", "license": "source card research/non-commercial; redistribution rights unconfirmed",
        "publication": "No source news text in Git or public reports", "host_answer_distribution": {op: dict(Counter(g["answers"][op] for g in gold.values())) for op in ("count", "weight_sum")}}
    return contexts, gold, plans, requests, provenance, report


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or study.INPUTS.exists():
        raise ValueError("CUDAhidden, one new immutable input freeze required")
    contexts, gold, plans, requests, provenance, report = build()
    for name, value in (("PUBLIC.json", contexts), ("HOST_GOLD.json", gold), ("PLANS.json", plans),
                        ("HELPER_REQUESTS.json", requests), ("PROVENANCE.json", provenance), ("MANIFEST.json", report)):
        study.write_x(study.INPUTS / name, value)
    by_id = {row["id"]: row for c in contexts for row in c["records"]}
    study.write_x(study.INPUTS / "PUBLIC_EXPOSURE.json", {"records": [
        {"dataset": "ag_news", "id": row["id"], "source_id": row["source_id"],
         "text": by_id[row["id"]]["text"]} for row in provenance]})
    (study.INPUTS / "HOST_GOLD.json").chmod(0o600)
    print({key: value for key, value in report.items() if key not in ("canonical_exposure_files",)})


if __name__ == "__main__":
    main()
