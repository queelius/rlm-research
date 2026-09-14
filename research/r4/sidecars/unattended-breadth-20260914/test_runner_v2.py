"""Exercise the installed tokenizer, not a simplified return-type double."""
import importlib.util
from pathlib import Path

def test_actual_tokenizer_returns_plain_json_serializable_prefix(tmp_path):
    path=Path(__file__).with_name('runner_v2.py')
    assert path.exists(), 'explicit-token-list runner missing'
    spec=importlib.util.spec_from_file_location('actual_token_runner',path)
    r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554',local_files_only=True)
    client=r.Client(tokenizer,'http://127.0.0.1:1','unused',tmp_path,0)
    ids=client.encode('A short scientific question.')
    assert isinstance(ids,list) and len(ids)>4 and all(type(x) is int for x in ids)
    assert 'A short scientific question.' in tokenizer.decode(ids)
