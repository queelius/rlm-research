"""Finalizer behavior; only the slow model response is substituted."""
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import submission


@pytest.mark.parametrize('mode', ['text', 'tool', 'length', 'error'])
def test_candidate_is_saved_before_exactly_one_restatement_and_tools_are_not_executed(tmp_path, mode):
    assert hasattr(submission, 'finalize_pair'), 'paired finalization does not exist yet'
    from openai.types.chat import ChatCompletion
    calls = []
    candidate = 'P: α\nline\\two'
    prefix = [{'role': 'user', 'content': 'the actual question'},
              {'role': 'assistant', 'tool_calls': [{'id': 'call1', 'type': 'function',
               'function': {'name': 'ipython', 'arguments': '{"code":"submit_text(value)"}'}}]},
              {'role': 'tool', 'tool_call_id': 'call1', 'content': ''}]
    async def complete(messages, turn):
        saved = json.loads((tmp_path / 'computed-commit-pair.json').read_text())
        assert saved['candidate'] == candidate and saved['restatement']['status'] == 'not_called'
        assert saved['common_messages'] == prefix
        calls.append((messages, turn))
        if mode == 'error':
            raise RuntimeError('fixture backend failure')
        message = {'role': 'assistant', 'content': candidate if mode != 'tool' else None}
        if mode == 'tool':
            message['tool_calls'] = [{'id': 'danger', 'type': 'function',
                'function': {'name': 'ipython', 'arguments': '{"code":"raise AssertionError()"}'}}]
        response = ChatCompletion(id='fixture', created=0, model='original', object='chat.completion',
            choices=[{'index': 0, 'finish_reason': 'length' if mode == 'length' else 'tool_calls' if mode == 'tool' else 'stop', 'message': message}])
        return response, SimpleNamespace()
    engine = SimpleNamespace(cwd=str(tmp_path), _complete=complete, _turn=1,
                             _metrics=SimpleNamespace(stop_reason=None))
    record = {'accepted': True, 'candidate': candidate, 'reason': None, 'attempts': []}
    if mode == 'error':
        with pytest.raises(RuntimeError, match='fixture backend'):
            asyncio.run(submission.finalize_pair(engine, prefix, record, 0))
    else:
        result = asyncio.run(submission.finalize_pair(engine, prefix, record, 0))
        assert result == (candidate if mode != 'tool' else '')
    saved = json.loads((tmp_path / 'computed-commit-pair.json').read_text())
    assert len(calls) == 1
    assert saved['candidate'] == candidate
    assert saved['restatement']['valid_terminal'] == (mode == 'text')
    assert prefix[-1]['content'] == ''  # No mutation of the actual common prefix.
    assert json.loads(calls[0][0][-1]['content'].split('\n', 1)[1]) == {'answer_utf8': candidate}
