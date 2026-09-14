"""Focused contracts for the unattended breadth case preparation."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent


def test_public_cases_hide_gold_and_repeat_is_byte_identical(tmp_path: Path) -> None:
    output_a = tmp_path / "a.jsonl"
    output_b = tmp_path / "b.jsonl"
    command = [sys.executable, str(ROOT / "prepare.py"), "--fixture", "--output"]
    subprocess.run([*command, str(output_a)], check=True)
    subprocess.run([*command, str(output_b)], check=True)

    assert output_a.read_bytes() == output_b.read_bytes()
    record = json.loads(output_a.read_text().splitlines()[0])
    assert set(record) == {"id", "dataset", "split", "question", "documents", "answer", "answer_type", "metadata"}
    assert "gold" not in record["question"].lower()
    assert "gold" not in record["documents"][0]["text"].lower()
    assert record["metadata"]["gold"] == "fixture-answer"


def test_actual_preparation_keeps_answers_host_only(tmp_path: Path) -> None:
    output = tmp_path / "cases.jsonl"
    subprocess.run([sys.executable, str(ROOT / "prepare.py"), "--output", str(output)], check=True)
    with output.open() as handle:
        rows = [json.loads(line) for line in handle]

    assert {row["dataset"] for row in rows} == {"musique", "finqa", "boolq", "ag_news", "longbench_v2"}
    assert all(row["answer"] is None and "gold" in row["metadata"] for row in rows)
    assert all("answer_aliases" not in row["question"] and "question_decomposition" not in row["question"] for row in rows)
