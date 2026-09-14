"""Additive v2: answerable MuSiQue and source-indexed typed breadth cases."""

import argparse
import json
import random
import re
import zipfile
from pathlib import Path

import pandas as pd

import prepare as v1


ROOT = Path(__file__).parent
CACHE = v1.CACHE
SEED = v1.SEED


def musique():
    archive = CACHE / "musique-v1.0-922ac98f19a201998dbdae6d7f2887a5258dbdeb/musique_data_v1.0.zip"
    with zipfile.ZipFile(archive) as zf:
        raw = [json.loads(line) for line in zf.read("data/musique_ans_v1.0_dev.jsonl").splitlines()]
    indexed = list(enumerate(raw))
    random.Random(SEED + 1).shuffle(indexed)
    rows = []
    for source_row_index, item in indexed[:512]:
        docs = []
        for paragraph in item["paragraphs"]:
            title = paragraph.get("title")
            text = f"{title}\n{paragraph['paragraph_text']}" if title else paragraph["paragraph_text"]
            docs.append({"id": str(paragraph["idx"]), "text": text})
        rows.append(v1.record(
            f"musique-answerable-dev-{item['id']}", "musique", "dev_answerable", item["question"], docs,
            "string", item["answer"], item["id"], answer_aliases=item.get("answer_aliases", []),
            answerable=bool(item["answerable"]), source_row_index=source_row_index,
            campaign_status="exploratory_prior_exposed",
        ))
    return v1.tier(rows)


def _finqa_type(value):
    normalized = str(value).strip()
    if normalized.lower() in {"yes", "no", "true", "false"}:
        return "boolean", normalized.lower() in {"yes", "true"}
    if re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?%?", normalized.replace(",", "")):
        return "number", normalized
    return "string", normalized


def finqa():
    path = Path("/project/alex_phd/research-cache/repos/FinQA-0f16e2867befa6840783e58be38c9efb9229d742/dataset/dev.json")
    indexed = list(enumerate(json.loads(path.read_text())))
    random.Random(SEED + 2).shuffle(indexed)
    rows = []
    for source_row_index, item in indexed[:512]:
        table = "\n".join("\t".join(map(str, line)) for line in item["table"])
        docs = [{"id": "table", "text": table}]
        docs += [{"id": f"pre-{i}", "text": text} for i, text in enumerate(item["pre_text"])]
        docs += [{"id": f"post-{i}", "text": text} for i, text in enumerate(item["post_text"])]
        qa = item["qa"]
        answer_type, gold = _finqa_type(qa["exe_ans"])
        rows.append(v1.record(
            f"finqa-dev-{item['id']}", "finqa", "dev", qa["question"], docs, answer_type, gold, item["id"],
            filename=item.get("filename"), source_row_index=source_row_index,
            annotation_note="raw exe_ans retained; FinQA annotations may contain known inconsistencies",
            campaign_status="exploratory_prior_exposed",
        ))
    return v1.tier(rows)


def boolq():
    raw = pd.read_parquet(CACHE / "boolq-20260911/validation.parquet").to_dict("records")
    indexed = list(enumerate(raw))
    random.Random(SEED + 3).shuffle(indexed)
    rows = [v1.record(
        f"boolq-validation-{source_row_index}", "boolq", "validation", item["question"],
        [{"id": "passage", "text": item["passage"]}], "boolean", bool(item["answer"]), str(source_row_index),
        source_row_index=source_row_index,
    ) for source_row_index, item in indexed[:512]]
    return v1.tier(rows)


def ag_news():
    raw = pd.read_parquet(CACHE / "fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4/test.parquet").to_dict("records")
    indexed = list(enumerate(raw))
    random.Random(SEED + 4).shuffle(indexed)
    names, sizes, rows, cursor = ["World", "Sports", "Business", "Science and Technology"], (8, 24, 64), [], 0
    for group_index in range(512):
        size = sizes[group_index % 3]
        if cursor + size > len(indexed):
            break
        group = indexed[cursor:cursor + size]
        cursor += size
        target = group_index % 4
        gold = sum(article["label"] == target for _, article in group)
        source_indices = [source_index for source_index, _ in group]
        rows.append(v1.record(
            f"ag_news-test-group-{group_index:03d}", "ag_news", "test", 
            f"How many of these {size} articles are about {names[target]}? Return one integer.",
            [{"id": str(i), "text": article["text"]} for i, (_, article) in enumerate(group)], "integer", gold,
            ",".join(map(str, source_indices)), source_row_index=source_indices,
            group_size=size, target_class=names[target], sampling="seeded_disjoint_article_groups",
        ))
    return v1.tier(rows)


def fixture():
    return [v1.record("fixture-0", "fixture", "fixture", "What is asked?", [{"id": "d", "text": "Fixture Title\nVisible evidence."}], "string", "fixture-answer", "fixture-source", answer_aliases=["fixture alias"], answerable=True, source_row_index=0)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "cases-v2.jsonl")
    parser.add_argument("--fixture", action="store_true")
    args = parser.parse_args()
    rows = fixture() if args.fixture else musique() + finqa() + boolq() + ag_news() + v1.longbench_v2()
    v1.write(rows, args.output)
    print(f"wrote {len(rows)} cases to {args.output}")


if __name__ == "__main__":
    main()
