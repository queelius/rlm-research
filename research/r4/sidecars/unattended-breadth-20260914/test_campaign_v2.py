"""Regression: Unicode line separators inside original evidence are not JSONL boundaries."""
import importlib.util
import json
from pathlib import Path

def test_jsonl_reader_preserves_unicode_line_separator(tmp_path):
    path=Path(__file__).with_name('campaign_v2.py')
    assert path.exists(), 'Unicode-safe owner not implemented'
    spec=importlib.util.spec_from_file_location('campaign_unicode',path)
    c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
    source=tmp_path/'input.jsonl'
    source.write_text(json.dumps({'text':'before\u2028after'},ensure_ascii=False)+'\n')
    assert c.read_cases(source)==[{'text':'before\u2028after'}]
