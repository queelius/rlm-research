"""Outcome-independent public DBpedia test freeze; no model calls."""

from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parent.parent
REVISION = "9abd46cf7fc8b4c64290f26993c540b92aa145ac"
CACHE = Path("/project/alex_phd/research-cache/datasets/fancyzhx--dbpedia_14--" + REVISION)
PARQUET = CACHE / "dbpedia_14/test-00000-of-00001.parquet"
SOURCE_SHA = "05fed41640e97f93ffd442757f6a84170348cf0c7500ecbda9e95ddcd928c631"
HISTORICAL = ROOT.parent / "root-c32-helper-batchsize-v1/inputs/SOURCES.json"
MODEL = Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554")
NAMESPACE = "helper-dbpedia224-transfer-data-v1|20260912"
LABELS = ["Company", "EducationalInstitution", "Artist", "Athlete", "OfficeHolder",
          "MeanOfTransportation", "Building", "NaturalPlace", "Village", "Animal",
          "Plant", "Album", "Film", "WrittenWork"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def norm(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def deduplicate(rows):
    contents, titles = defaultdict(list), defaultdict(list)
    rejected = set()
    for row in rows:
        content, title = norm(row["content"]), norm(row["title"])
        if not content:
            rejected.add(row["source_id"])
        contents[content].append(row["source_id"])
        if title:
            titles[title].append(row["source_id"])
    for groups in (contents, titles):
        for members in groups.values():
            if len(members) > 1:
                rejected.update(members)
    return [row for row in rows if row["source_id"] not in rejected], rejected


def choose(rows, labels, quota):
    selected = []
    for label in labels:
        candidates = sorted((row for row in rows if row["label_id"] == label),
                            key=lambda row: digest(NAMESPACE + "|select|" + row["source_id"]))
        if len(candidates) < quota:
            raise ValueError("insufficient unique source rows for fixed class quota")
        selected.extend(candidates[:quota])
    return sorted(selected, key=lambda row: digest(NAMESPACE + "|order|" + row["source_id"]))


def write_x(path, value, private=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    if private:
        path.chmod(0o600)


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (ROOT / "inputs").exists():
        raise ValueError("require CPU-only unused data freeze")
    if sha(PARQUET) != SOURCE_SHA:
        raise ValueError("pinned source parquet differs")
    import pyarrow.parquet as pq
    from transformers import AutoTokenizer

    raw = pq.read_table(PARQUET, columns=["label", "title", "content"]).to_pylist()
    if len(raw) != 70000 or Counter(row["label"] for row in raw) != Counter({i: 5000 for i in range(14)}):
        raise ValueError("official test inventory differs")
    rows = [{"source_id": f"dbpedia14:test:{i}", "source_row_0based": i,
             "title": row["title"], "content": row["content"], "label_id": row["label"]}
            for i, row in enumerate(raw)]
    eligible, rejected = deduplicate(rows)
    selected = choose(eligible, range(14), 16)
    public, gold, provenance = [], {}, []
    for row in selected:
        key = "d" + digest(NAMESPACE + "|id|" + row["source_id"])[:16]
        text = "Title: " + row["title"] + "\nDescription: " + row["content"]
        public.append({"dataset": "dbpedia14", "id": key, "source_id": row["source_id"], "text": text})
        gold[key] = LABELS[row["label_id"]]
        provenance.append({"id": key, "source_id": row["source_id"],
                           "source_row_0based": row["source_row_0based"], "label_id": row["label_id"],
                           "title_sha256": digest(row["title"]), "content_sha256": digest(row["content"])})
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    historical = json.loads(HISTORICAL.read_text())["contexts"]["question-sensitive-sft-train-05"]["partitions"]["4"]["0"]
    old = tokenizer.encode(historical["request_text"], add_special_tokens=False)
    body = historical["body"]
    ids = body["token_ids"]
    offsets = [i for i in range(len(ids) - len(old) + 1) if ids[i:i + len(old)] == old]
    if len(offsets) != 1:
        raise ValueError("historical generic chat wrapper boundary differs")
    start = offsets[0]
    prefix, suffix = ids[:start], ids[start + len(old):]
    requests = []
    for offset in range(0, 224, 4):
        group = public[offset:offset + 4]
        keys = [row["id"] for row in group]
        schema = {"type": "object", "properties": {key: {"type": "string", "enum": LABELS} for key in keys},
                  "required": keys, "additionalProperties": False}
        text = ("Classify the entity described by each encyclopedia entry into one DBpedia category.\n"
                "Use its title and description, and select its main entity type rather than another mentioned entity.\n"
                "Return only one JSON object mapping every supplied id exactly once to one label.\n"
                "No missing or extra ids. Allowed labels: " + json.dumps(LABELS, separators=(",", ":"))
                + "\nEntries: " + json.dumps([{"id": row["id"], "text": row["text"]} for row in group],
                                               separators=(",", ":"), ensure_ascii=False))
        native = {"model": "strict-rlm-qwen3-4b-role-sft-selected-v1",
                  "token_ids": prefix + tokenizer.encode(text, add_special_tokens=False) + suffix,
                  "sampling_params": {**body["sampling_params"], "temperature": 0.0,
                                      "seed": 202609123500 + len(requests), "max_tokens": 1024,
                                      "structured_outputs": {"json": schema}}, "cache_salt": "0"}
        if len(native["token_ids"]) + 1024 > 8192:
            raise ValueError("fixed request exceeds qualified native context cap; do not resample silently")
        requests.append({"request_id": digest(NAMESPACE + "|request|" + str(offset)),
                         "dataset": "dbpedia14", "start": offset, "ids": keys, "request_text": text,
                         "schema_ordered_json": json.dumps(schema, separators=(",", ":")),
                         "body_template": native})
    audit = {"source_rows": len(raw), "eligible": len(eligible), "rejected_duplicate_or_empty_rows": len(rejected),
             "selected": 224, "per_class": dict(Counter(gold.values())), "planned_B4_calls": 56,
             "max_prompt_plus_1024": max(len(row["body_template"]["token_ids"]) + 1024 for row in requests),
             "selection_used_model_outcomes": False, "training_split_acquired": False,
             "prior_exposure_boundary": "No DBpedia records found in scoped r4 question/idea/source-manifest search before acquisition; unknown pretraining and unrecorded history are not excluded."}
    write_x(ROOT / "inputs/PUBLIC.json", {"contains_gold": False, "records": public})
    write_x(ROOT / "inputs/HOST_GOLD.json", {"never_include_in_model_prompt": True, "labels": gold}, private=True)
    write_x(ROOT / "inputs/SELECTED_PROVENANCE.json", provenance)
    write_x(ROOT / "inputs/REQUESTS.json", requests)
    write_x(ROOT / "inputs/EXCLUSION_AUDIT.json", audit)
    sources = [PARQUET, CACHE / "README.md", HISTORICAL, ROOT / "prepare.py", ROOT / "test_prepare.py", ROOT / "DESIGN.md",
               STORE / "operations/2026-09-12-dbpedia-transfer-acquisition/RECEIPT_V2.json"]
    ready = {"schema": "dbpedia224-transfer-data-ready-v1", "status": "CPU_FROZEN_NO_MODEL_CALLS",
             "namespace": NAMESPACE, "source_revision": REVISION, "source_license": "CC-BY-SA-3.0; card also names GNU FDL",
             "question": "Does news RL alter helper classification in a different domain and14-label vocabulary?",
             "intended_fixed_arms": ["c32", "rl_step8", "sft_step8", "rl_seed2_step8"],
             "source_sha256": {str(path): sha(path) for path in sources},
             "artifact_sha256": {str(path): sha(path) for path in sorted((ROOT / "inputs").iterdir())},
             "inventory": audit, "model_or_gpu_calls": 0,
             "claim_boundary": "Different domain and category vocabulary, still short-text classification; not planning or recursion; unknown base pretraining exposure."}
    ready["identity"] = digest(json.dumps(ready, sort_keys=True, separators=(",", ":")))
    write_x(ROOT / "DATA_READY.json", ready)
    print(json.dumps({"data_ready_sha256": sha(ROOT / "DATA_READY.json"), "identity": ready["identity"], **audit}))


if __name__ == "__main__":
    main()
