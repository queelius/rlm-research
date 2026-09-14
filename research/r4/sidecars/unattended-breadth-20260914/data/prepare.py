"""Build deterministic host-scored breadth-screen cases; never load a model."""

import argparse
import hashlib
import json
import random
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent
CACHE = Path("/project/alex_phd/research-cache/datasets")
SEED = 20260914


def record(case_id, dataset, split, question, documents, answer_type, gold, source_id, **metadata):
    """Keep scorer-only information out of the model-visible prompt fields."""
    return {
        "id": case_id,
        "dataset": dataset,
        "split": split,
        "question": question,
        "documents": documents,
        "answer": None,
        "answer_type": answer_type,
        "metadata": {"source_id": source_id, "gold": gold, **metadata},
    }


def tier(rows):
    for index, row in enumerate(rows):
        row["metadata"]["tier"] = "pilot" if index < 16 else "screen" if index < 272 else "reserve"
    return rows


def musique():
    archive = CACHE / "musique-v1.0-922ac98f19a201998dbdae6d7f2887a5258dbdeb/musique_data_v1.0.zip"
    with zipfile.ZipFile(archive) as zf:
        raw = [json.loads(line) for line in zf.read("data/musique_full_v1.0_dev.jsonl").splitlines()]
    random.Random(SEED + 1).shuffle(raw)
    return tier([
        record(
            f"musique-dev-{item['id']}", "musique", "dev", item["question"],
            [{"id": str(p["idx"]), "text": p["paragraph_text"]} for p in item["paragraphs"]],
            "string", item["answer"], item["id"], aliases=item.get("answer_aliases", []),
            campaign_status="exploratory_prior_exposed",
        ) for item in raw[:512]
    ])


def finqa():
    path = Path("/project/alex_phd/research-cache/repos/FinQA-0f16e2867befa6840783e58be38c9efb9229d742/dataset/dev.json")
    raw = json.loads(path.read_text())
    random.Random(SEED + 2).shuffle(raw)
    rows = []
    for item in raw[:512]:
        table = "\n".join("\t".join(map(str, line)) for line in item["table"])
        docs = [{"id": "table", "text": table}]
        docs += [{"id": f"pre-{i}", "text": text} for i, text in enumerate(item["pre_text"])]
        docs += [{"id": f"post-{i}", "text": text} for i, text in enumerate(item["post_text"])]
        qa = item["qa"]
        rows.append(record(
            f"finqa-dev-{item['id']}", "finqa", "dev", qa["question"], docs, "number",
            str(qa["exe_ans"]), item["id"], filename=item.get("filename"),
            annotation_note="raw exe_ans retained; FinQA annotations may contain known inconsistencies",
            campaign_status="exploratory_prior_exposed",
        ))
    return tier(rows)


def boolq():
    raw = pd.read_parquet(CACHE / "boolq-20260911/validation.parquet").to_dict("records")
    random.Random(SEED + 3).shuffle(raw)
    return tier([
        record(f"boolq-validation-{i}", "boolq", "validation", item["question"],
               [{"id": "passage", "text": item["passage"]}], "boolean", bool(item["answer"]), str(i))
        for i, item in enumerate(raw[:512])
    ])


def ag_news():
    raw = pd.read_parquet(CACHE / "fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4/test.parquet").to_dict("records")
    random.Random(SEED + 4).shuffle(raw)
    names = ["World", "Sports", "Business", "Science and Technology"]
    sizes = (8, 24, 64)
    rows, cursor = [], 0
    for group_index in range(512):
        size = sizes[group_index % len(sizes)]
        if cursor + size > len(raw):
            break
        group = raw[cursor:cursor + size]
        cursor += size
        target = group_index % len(names)
        gold = sum(article["label"] == target for article in group)
        rows.append(record(
            f"ag_news-test-group-{group_index:03d}", "ag_news", "test", 
            f"How many of these {size} articles are about {names[target]}? Return one integer.",
            [{"id": str(i), "text": article["text"]} for i, article in enumerate(group)],
            "integer", gold, ",".join(str(cursor - size + i) for i in range(size)),
            group_size=size, target_class=names[target], sampling="seeded_disjoint_article_groups",
        ))
    return tier(rows)


def longbench_v2():
    path = CACHE / "zai-org--LongBench-v2--2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9/data.json"
    raw = json.loads(path.read_text())
    random.Random(SEED + 5).shuffle(raw)
    rows = []
    for item in raw:
        choices = "\n".join(f"{key[-1]}. {item[key]}" for key in ("choice_A", "choice_B", "choice_C", "choice_D"))
        rows.append(record(
            f"longbench_v2-train-{item['_id']}", "longbench_v2", "train",
            f"{item['question']}\n\nChoices:\n{choices}", [{"id": "context", "text": item["context"]}],
            "choice", item["answer"], item["_id"], domain=item["domain"], sub_domain=item["sub_domain"],
            difficulty=item["difficulty"], length=item["length"], no_truncation_in_prep=True,
        ))
    return tier(rows)


def fixture():
    return [record("fixture-0", "fixture", "fixture", "What is asked?", [{"id": "d", "text": "Visible evidence."}], "string", "fixture-answer", "fixture-source")]


def write(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "cases.jsonl")
    parser.add_argument("--fixture", action="store_true")
    args = parser.parse_args()
    rows = fixture() if args.fixture else musique() + finqa() + boolq() + ag_news() + longbench_v2()
    write(rows, args.output)
    print(f"wrote {len(rows)} cases to {args.output}")


if __name__ == "__main__":
    main()
