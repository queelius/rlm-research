"""Narrow contracts for answerable MuSiQue and typed v2 host scoring."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent


def test_v2_fixture_keeps_gold_host_only_and_titles_public(tmp_path: Path) -> None:
    output = tmp_path / "fixture.jsonl"
    subprocess.run(
        [sys.executable, str(ROOT / "prepare_v2.py"), "--fixture", "--output", str(output)], check=True
    )
    row = json.loads(output.read_text())
    assert row["answer"] is None
    assert row["metadata"]["gold"] == "fixture-answer"
    assert row["metadata"]["answer_aliases"] == ["fixture alias"]
    assert row["documents"][0]["text"].startswith("Fixture Title\n")


def test_v2_actual_rows_preserve_indices_and_answerable_musique(tmp_path: Path) -> None:
    output = tmp_path / "cases.jsonl"
    subprocess.run([sys.executable, str(ROOT / "prepare_v2.py"), "--output", str(output)], check=True)
    with output.open() as handle:
        rows = [json.loads(line) for line in handle]
    musique_rows = [row for row in rows if row["dataset"] == "musique"]
    boolq_rows = [row for row in rows if row["dataset"] == "boolq"]
    ag_news_rows = [row for row in rows if row["dataset"] == "ag_news"]
    assert len(musique_rows) == 512
    assert all(row["metadata"]["answerable"] is True for row in musique_rows)
    assert all("\n" in row["documents"][0]["text"] for row in musique_rows)
    assert all(row["documents"][0]["text"].split("\n", 1)[0] for row in musique_rows)
    assert all(isinstance(row["metadata"]["source_row_index"], int) for row in boolq_rows)
    assert all(all(isinstance(index, int) for index in row["metadata"]["source_row_index"]) for row in ag_news_rows)
    assert all(row["answer"] is None and "gold" in row["metadata"] for row in rows)
