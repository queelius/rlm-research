"""Container-only explicit submission channel, independent of stdout/display."""
from __future__ import annotations

import copy
import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from queue import Empty

MIME = 'application/vnd.rlm.explicit-submission.v1+json'
_state = None


def install_kernel(byte_cap):
    from IPython import get_ipython
    shell = get_ipython()
    state = {'attempts': [], 'candidate': None, 'rejection': None}
    global _state
    _state = state

    def reset(info):
        state.update(attempts=[], candidate=None, rejection=None)

    def submit_text(value):
        attempt = {'type': type(value).__name__}
        state['attempts'].append(attempt)
        reason = None
        if len(state['attempts']) > 1:
            reason = 'duplicate'
        elif type(value) is not str:
            reason = 'non_string'
        else:
            try:
                raw = value.encode('utf-8', errors='strict')
                attempt.update(utf8_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                if len(raw) > byte_cap:
                    reason = 'oversize'
                else:
                    attempt['value'] = value
            except UnicodeEncodeError:
                reason = 'invalid_utf8'
        if reason:
            state.update(rejection=reason, candidate=None)
            if reason == 'non_string':
                raise TypeError('submit_text requires one plain str; no coercion')
            raise ValueError('submit_text rejected: ' + reason)
        if state['rejection'] is None:
            state['candidate'] = value

    shell.events.register('pre_run_cell', reset)
    shell.user_ns['submit_text'] = submit_text


class SubmissionEnvelope:
    def _repr_mimebundle_(self, include=None, exclude=None):
        return {MIME: copy.deepcopy(_state)}


def envelope():
    if _state is None:
        raise RuntimeError('submission channel is not installed')
    return SubmissionEnvelope()


def shell_reply(repl, msg_id, timeout=5):
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('missing matching Jupyter execute_reply')
        reply = repl._kc.get_shell_msg(timeout=remaining)
        if reply['parent_header'].get('msg_id') == msg_id:
            return reply['content']


def execute_locked(repl, code, timeout):
    from rlm.tools.ipython import _ANSI_RE
    repl.submission_record = None
    msg_id = repl._kc.execute(code)
    deadline = None if timeout is None else time.monotonic() + timeout
    outputs, aborted = [], False
    while True:
        if repl._interrupt_requested.is_set():
            repl._interrupt_and_recover()
            aborted = True
            break
        remaining = None if deadline is None else deadline - time.monotonic()
        if remaining is not None and remaining <= 0:
            repl._interrupt_and_recover()
            outputs.append(f'\n[execution timed out after {timeout}s and was interrupted]')
            aborted = True
            break
        try:
            msg = repl._kc.get_iopub_msg(timeout=0.1 if remaining is None else min(remaining, 0.1))
        except Empty:
            continue
        if msg['parent_header'].get('msg_id') != msg_id:
            continue
        kind, content = msg['msg_type'], msg['content']
        if kind == 'stream':
            outputs.append(content['text'])
        elif kind == 'execute_result':
            value = content.get('data', {}).get('text/plain', '')
            if value:
                outputs.append(value + '\n')
        elif kind == 'error':
            outputs.append(_ANSI_RE.sub('', '\n'.join(content.get('traceback', []))))
        elif kind == 'status' and content['execution_state'] == 'idle':
            break
    reply = shell_reply(repl, msg_id)
    # A separate silent user-expression query also works after a failing cell.
    # Its MIME payload is JSON data, never a repr/stdout conversion.
    query = repl._kc.execute('', silent=True, user_expressions={
        'rlm_submission': "__import__('rlm.mrcr_submission',fromlist=['envelope']).envelope()"})
    payload = shell_reply(repl, query)['user_expressions']['rlm_submission']
    if payload.get('status') != 'ok' or MIME not in payload.get('data', {}):
        raise RuntimeError('structured submission reply missing')
    state = payload['data'][MIME]
    reason = state['rejection']
    if reason is None:
        if aborted or reply.get('status') != 'ok':
            reason = 'cell_error'
        elif not state['attempts']:
            reason = 'absent'
    accepted = reason is None and len(state['attempts']) == 1
    repl.submission_record = {'schema': 'explicit-submission-v1', 'accepted': accepted,
        'candidate': state['candidate'] if accepted else None, 'reason': reason,
        'attempts': state['attempts'], 'cell_status': reply.get('status'), 'aborted': aborted}
    return ''.join(outputs)


def install():
    from rlm.tools.base import ToolOutcome
    from rlm.tools.ipython import IPythonREPL, IpythonTool
    if getattr(IPythonREPL, '_computed_submission_installed', False):
        return
    old_startup, old_execute = IPythonREPL._inject_startup, IpythonTool.execute

    @dataclass
    class SubmissionOutcome(ToolOutcome):
        submission: dict | None = None

    def startup(repl):
        old_startup(repl)
        cap = int(os.environ['MRCR_SUBMISSION_BYTE_CAP'])
        repl._execute_silent('from rlm.mrcr_submission import install_kernel; install_kernel(' + str(cap) + ')')

    def tool_execute(tool, args, context):
        if context.repl is not None:
            context.repl.submission_record = None
        value = old_execute(tool, args, context)
        record = None if context.repl is None else context.repl.submission_record
        return SubmissionOutcome(content=value.content, metric_events=value.metric_events, submission=record)

    IPythonREPL._inject_startup = startup
    IPythonREPL._execute_locked = execute_locked
    IPythonREPL._computed_submission_installed = True
    IpythonTool.execute = tool_execute


def persist(path, value):
    path = Path(path)
    temporary = path.with_suffix('.pending')
    with temporary.open('x') as stream:
        json.dump(value, stream, sort_keys=True, ensure_ascii=True, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def record_submission(engine, record, turn):
    directory = Path(engine.cwd) / 'computed-submissions'
    directory.mkdir(exist_ok=True)
    path = directory / f'turn-{turn + 1}.json'
    if path.exists():
        raise RuntimeError('submission turn already recorded')
    persist(path, record)


async def finalize_pair(engine, messages, record, turn):
    if not record['accepted'] or type(record['candidate']) is not str:
        raise ValueError('finalizer requires an accepted explicit string')
    candidate = record['candidate']
    payload = candidate.encode('utf-8')
    path = Path(engine.cwd) / 'computed-commit-pair.json'
    if path.exists():
        raise RuntimeError('paired terminal already committed; never double-restates')
    value = {'schema': 'computed-commit-pair-v1', 'candidate': candidate,
        'candidate_utf8_base64': base64.b64encode(payload).decode('ascii'),
        'candidate_sha256': hashlib.sha256(payload).hexdigest(),
        'candidate_utf8_bytes': len(payload), 'submission': record,
        'common_messages': copy.deepcopy(messages), 'prefix_root_turns': turn + 1,
        'restatement': {'status': 'not_called', 'valid_terminal': False}}
    persist(path, value)
    request_messages = copy.deepcopy(messages)
    request_messages.append({'role': 'user', 'content':
        'Return the exact value of answer_utf8 below as final text, decoding JSON escapes. '
        'Do not use tools, explain, correct, or add any text.\n' +
        json.dumps({'answer_utf8': candidate}, ensure_ascii=False)})
    engine._computed_restatement = True
    try:
        response, usage = await engine._complete(request_messages, turn + 1)
        choice = response.choices[0]
        message = choice.message
        text = message.content
        oversize = isinstance(text, str) and len(text.encode('utf-8')) > int(os.environ.get('MRCR_SUBMISSION_BYTE_CAP', '65536'))
        value['restatement'] = {'status': 'returned', 'message': message.model_dump(exclude_none=True),
            'response': response.model_dump(exclude_none=True), 'finish_reason': choice.finish_reason,
            'text': text, 'oversize': oversize, 'tool_requested': bool(message.tool_calls),
            'valid_terminal': choice.finish_reason == 'stop' and not message.tool_calls
                              and isinstance(text, str) and not oversize,
            'request_messages': request_messages}
        engine._turn = turn + 2
        engine._metrics.stop_reason = 'computed_commit_pair'
        if getattr(engine, 'session', None) is not None:
            engine.session.log_assistant(turn + 1, None, text)
        persist(path, value)
        # This is the observed restatement, never the committed candidate fallback.
        return text if isinstance(text, str) else ''
    except BaseException as error:
        value['restatement'] = {'status': 'error', 'valid_terminal': False,
            'error_type': type(error).__name__, 'error': str(error),
            'request_messages': request_messages}
        persist(path, value)
        raise
