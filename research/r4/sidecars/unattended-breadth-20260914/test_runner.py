"""Focused contract tests: reject leakage/unsafe arithmetic and exercise native HTTP."""
import importlib.util
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

PATH = Path(__file__).with_name('runner.py')

def module():
    assert PATH.exists(), 'campaign runner is not implemented'
    spec = importlib.util.spec_from_file_location('breadth_runner', PATH)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

def test_primary_grades_do_not_count_invalid_answers_as_unknown():
    r = module()
    case = {'answer_type':'boolean','answer':False,'metadata':{}}
    assert r.grade('{"answer":false}', case)['correct'] is True
    assert r.grade('{"answer":"false"}', case)['valid'] is False
    assert r.grade('nonsense', case)['correct'] is False
    assert r.grade('{"answer":"Paris"}', {'answer_type':'string','answer':'Paris','metadata':{}})['correct'] is True

def test_calculator_is_arithmetic_only():
    r = module()
    assert r.calculate('(120 - 100) / 100') == .2
    for expression in ('__import__("os").getcwd()', '2**9999999', '1/0', '[1][0]'):
        with pytest.raises((ValueError, ZeroDivisionError)):
            r.calculate(expression)

def test_public_prompt_never_serializes_gold_or_metadata():
    r = module()
    case = {'question':'Where?','documents':[{'id':'p1','text':'a passage'}],
            'answer':'GOLD_SENTINEL','metadata':{'support':'SECRET_SUPPORT'}}
    prompt = r.public_text(case)
    assert 'GOLD_SENTINEL' not in prompt and 'SECRET_SUPPORT' not in prompt
    assert 'a passage' in prompt and 'Where?' in prompt

def test_native_http_decoding_accounting_and_resume(tmp_path, monkeypatch):
    r = module()
    class Tokenizer:
        def apply_chat_template(self, messages, **kwargs): return [11,12,13]
        def decode(self, ids, **kwargs): return '{"answer":false}'
    received = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            received.append(body)
            assert self.path == '/inference/v1/generate'
            response = {'model':'model','request_id':'fixture-1',
                'choices':[{'token_ids':[20,21], 'finish_reason':'stop'}],
                'usage':{'prompt_tokens':3,'completion_tokens':2}}
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(response).encode())
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        client = r.Client(Tokenizer(),f'http://127.0.0.1:{server.server_port}', 'model',tmp_path,time.time()+10,max_context=16)
        value = client.call('a','question',1,8)
        assert value['text'] == '{"answer":false}' and value['available']
        assert value['usage']['prompt_tokens'] == 3
        assert client.call('a','question',1,8) == value and len(received) == 1
        with pytest.raises(ValueError): client.call('too-long','question',2,16)
    finally: server.shutdown(); server.server_close()

def test_partition_keeps_every_document_once():
    r = module()
    docs = [{'id':str(i),'text':'x'*(i+1)} for i in range(7)]
    chunks = r.partition(docs, 3)
    assert sorted(d['id'] for c in chunks for d in c) == ['0','1','2','3','4','5','6']

def test_long_single_document_is_partitioned_without_losing_text():
    r = module()
    text = 'a useful sentence.\n' * 1000
    chunks = r.partition([{'id':'original','text':text}], 4)
    assert len(chunks) >= 3
    assert ''.join(d['text'] for c in chunks for d in c) == text

def test_campaign_extension_requires_actual_signal():
    path=Path(__file__).with_name('campaign.py')
    assert path.exists(), 'campaign owner not implemented'
    spec=importlib.util.spec_from_file_location('breadth_campaign',path)
    c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
    assert not c.extend([{'available':False,'correct':False}]*20)
    assert not c.extend([{'available':True,'correct':False}]*20)
    assert c.extend([{'available':True,'correct':True},{'available':True,'correct':False}]*10)
