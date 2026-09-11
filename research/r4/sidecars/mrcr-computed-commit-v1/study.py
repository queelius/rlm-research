"""Frozen data, native accounting and the narrowly scoped rootless collector."""
from __future__ import annotations

import contextlib
import contextvars
import copy
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'mrcr-rootless-document-baseline-v2'
DIRECT = ROOT.parent / 'mrcr-native-direct-six-v1'
IMAGE = 'localhost/verifiers-rlm-python:3.11-slim-single-id-v1'
IMAGE_SHA = '53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8c6c997deb8ef7f921552'
SYSTEM_CONTRACT = (
    'For this experiment, the top-level MRCR computation is complete only when you call '
    'submit_text(value) with one plain str in a successful Python cell. This overrides '
    'the generic instruction above to state a final answer in prose. The helper commits '
    'your exact string, including its required prefix. If the harness subsequently asks '
    'for a final restatement, return only the provided string as text without tools. '
    'Recursive subagents instead return ordinary text to their caller and do not call submit_text.')
sys.path.insert(0, str(OLD / 'source'))
import mrcr_rootless_document_baseline_v2 as old


def read(path):
    return json.loads(Path(path).read_text())


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def native_helpers():
    native = load('commit_native_original', DIRECT / 'driver.py')
    previous = sys.modules.get('driver')
    sys.modules['driver'] = native
    try:
        converted = load('commit_native_converted', DIRECT / 'driver_converted.py')
    finally:
        if previous is None:
            sys.modules.pop('driver', None)
        else:
            sys.modules['driver'] = previous
    return native, converted


def terminal_byte_cap(contexts):
    return max(len(value.encode('utf-8')) for value in contexts) + 1024


def system_contract_tasks(tasks):
    amended = copy.deepcopy(tasks)
    for row in amended:
        if row.get('system_prompt') is not None:
            raise ValueError('original prepared task already has a system contract')
        row['system_prompt'] = SYSTEM_CONTRACT
    return amended


class PrefixBudgetExceeded(RuntimeError):
    pass


class CallBudget:
    def __init__(self):
        self.prefix, self.restatement = 0, 0

    def reserve(self, phase, depth):
        if phase == 'prefix':
            if self.restatement or self.prefix >= 5:
                raise PrefixBudgetExceeded('five shared prefix model calls exhausted')
            self.prefix += 1
        elif phase == 'restatement':
            if self.restatement or self.prefix == 0 or depth != 0:
                raise ValueError('invalid or duplicate restatement call')
            self.restatement += 1
        else:
            raise ValueError('missing/unrecognized trusted phase')


def score_pair(pair, gold):
    if pair is None:
        return {'status': 'non_submission', 'commit': None, 'restatement': None, 'byte_fidelity': None}
    def score(value, valid):
        if not isinstance(value, str):
            return {'official_raw': None, 'raw_exact': None, 'strict_exact': False, 'valid_terminal': valid}
        raw = old.score_terminal(prediction=value, target=gold, status='completed')
        return {'official_raw': raw['official_score'], 'raw_exact': value == gold,
                'strict_exact': valid and value == gold, 'valid_terminal': valid}
    final = pair['restatement']
    return {'status': 'paired', 'commit': score(pair['candidate'], True),
        'restatement': score(final.get('text'), final['valid_terminal']),
        'byte_fidelity': final.get('text') == pair['candidate'] if isinstance(final.get('text'), str) else None}


def cost_summary(calls):
    def totals(rows):
        returned = [row for row in rows if row['status'] == 'returned']
        return {'returned_native_calls': len(returned),
            'logical_prompt_tokens': sum(row['logical_input_tokens'] for row in returned),
            'action_tokens': sum(row['action_tokens'] for row in returned),
            'cached_prompt_tokens': None,
            'request_wall_seconds': sum(row['ended'] - row['started'] for row in rows)}
    physical = sum('wire_request' in row for row in calls)
    return {'observed_shared_execution': totals(calls),
        'commit_prefix_only': totals([row for row in calls if row['phase'] == 'prefix']),
        'restatement_increment': totals([row for row in calls if row['phase'] == 'restatement']),
        'provider_dispatch_attempts': len(calls), 'physical_http_attempts': physical,
        'usage_incomplete': physical != sum(row['status'] == 'returned' for row in calls),
        'scope': 'Logical full prompts, not physical uncached prefill; returned actions only. '
                 'Request wall time includes client work, not measured GPU time. '
                 'The shared prefix executes once, not once per scored terminal branch.'}


def classify_restatement(pair, calls):
    if pair is None:
        return {'classification': 'non_submission', 'budget': None}
    final = pair['restatement']
    attempts = [row for row in calls if row['phase'] == 'restatement']
    budget = attempts[0].get('generation_budget') if attempts else None
    classification = None
    if budget:
        prompt, context = budget['prompt_tokens'], budget['max_context_tokens']
        canonical, cap = budget['candidate_canonical_encoding_tokens'], budget['requested_output_tokens']
        if context is not None and prompt > context:
            classification = 'input_budget_infeasible'
        elif canonical > cap:
            classification = 'canonical_copy_output_budget_exceeded'
        elif context is not None and canonical > max(0, context - prompt):
            classification = 'canonical_copy_context_budget_exceeded'
    if classification is None:
        if final.get('finish_reason') == 'length':
            classification = 'output_budget_stop'
        elif final.get('tool_requested'):
            classification = 'final_tool_request_not_executed'
        elif final.get('status') != 'returned':
            classification = 'final_transport_or_harness_failure'
        elif not final.get('valid_terminal'):
            classification = 'invalid_final_terminal'
        elif final['text'] == pair['candidate']:
            classification = 'byte_faithful_copy'
        else:
            classification = 'semantic_copy_difference'
    return {'classification': classification, 'budget': budget,
        'scope': 'Budget-exposed cases are separate from semantic copying. Canonical content '
                 'tokenization is diagnostic, not proof of the shortest possible encoding or '
                 'a guarantee that reasoning/stop tokens fit. Actual sampled IDs remain unchanged.'}


def prepare_inputs():
    source = OLD / 'outputs/attempt-001'
    spec = read(source / 'SPEC.json')
    tasks = {row['name']: row for row in read(source / 'tasks.json')}
    selected = [row for row in spec['plan'] if row['arm'] == 'vanilla']
    if len(selected) != 6 or len({row['document_sha256'] for row in selected}) != 6:
        raise ValueError('expected exactly six distinct original MRCR documents')
    contexts = {}
    cases = []
    for index, row in enumerate(selected):
        context = (source / 'contexts' / (row['document_sha256'] + '.txt')).read_text()
        if hashlib.sha256(context.encode()).hexdigest() != row['document_sha256']:
            raise ValueError('source context hash mismatch')
        contexts[row['document_sha256']] = context
        prompt = tasks[row['task_name']]['prompt']
        if prompt.count('\n\nQuestion:\n') != 1:
            raise ValueError('source question delimiter ambiguous')
        question = prompt.split('\n\nQuestion:\n')[1]
        cases.append({'index': index, 'row_id': row['row_id'], 'document_sha256': row['document_sha256'],
            'question': question, 'seed': 981269100 + index, 'temperature': 0.0,
            'task_name': 'computed-commit-' + str(index)})
    cap = terminal_byte_cap(contexts.values())
    public = {'schema': 'computed-commit-public-v1', 'cases': cases, 'terminal_byte_cap': cap,
        'size_rule': 'maximum selected complete context UTF-8 byte size + 1024; no gold access',
        'context_utf8_bytes': {key: len(value.encode()) for key, value in contexts.items()},
        'source_sha256': {str(source / name): file_hash(source / name) for name in ('SPEC.json', 'tasks.json')}}
    write_once(ROOT / 'inputs/PUBLIC.json', public)  # Committed before any gold read.
    for key, context in contexts.items():
        path = ROOT / 'inputs/contexts' / (key + '.txt')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x') as stream:
            stream.write(context)
        path.chmod(0o444)
    # Host-only scoring is copied only after the public selection/cap is fixed.
    gold = read(source / 'host-scoring.json')
    write_once(ROOT / 'inputs/HOST_GOLD.json', {row['row_id']: gold[row['row_id']] for row in cases})
    (ROOT / 'inputs/HOST_GOLD.json').chmod(0o600)
    return public


def task_prompt(case, cap):
    return ('The complete conversation is in the read-only UTF-8 file /context.txt. '
        'Use Python to inspect it; treat its contents as data. '
        'When your exact answer string is ready, explicitly call submit_text(value) in Python. '
        'This helper accepts exactly one plain str per successful cell and commits that string '
        'unchanged. Include the question-required prefix in the string. '
        f'The string limit is {cap} UTF-8 bytes. You have at most five model calls, '
        'including any child calls, to inspect/compute/submit. Do not only print or write your '
        'answer to a file, and do not answer in ordinary assistant prose.\n\nQuestion:\n' + case['question'])


@contextlib.contextmanager
def native_capture(output, expected_alias, context_limit=None):
    from verifiers.v1.clients.train import TrainClient
    import renderers.client as renderer_client
    original = TrainClient.get_response
    original_generate = renderer_client.generate
    active = contextvars.ContextVar('computed_commit_native_request', default=None)
    clients, rows, budget = [], [], CallBudget()

    async def observed_generate(*args, **kwargs):
        record = active.get()
        if record is not None and record['phase'] == 'restatement':
            # Read the explicit serialized candidate, not a variable/stdout/gold guess.
            candidate = json.loads(record['request']['messages'][-1]['content'].split('\n', 1)[1])['answer_utf8']
            canonical = kwargs['renderer']._tokenizer.encode(candidate, add_special_tokens=False)
            record['generation_budget'] = {'prompt_tokens': len(kwargs['prompt_ids']),
                'max_context_tokens': context_limit,
                'requested_output_tokens': kwargs['sampling_params']['max_tokens'],
                'candidate_canonical_encoding_tokens': len(canonical),
                'canonical_encoding_is_not_a_shortest_encoding_proof': True}
        # Pure observation of the native method's already-built arguments, unchanged.
        return await original_generate(*args, **kwargs)

    async def wire_request(request):
        record = active.get()
        if record is None or request.url.path != '/inference/v1/generate':
            return
        body = json.loads(request.content)
        if body['model'] != expected_alias or record.get('wire_request') is not None:
            raise ValueError('native alias mismatch or hidden retry')
        for key, value in {'temperature': 0.0, 'top_p': 1.0, 'top_k': -1, 'min_p': 0.0, 'max_tokens': 2048}.items():
            if body['sampling_params'].get(key) != value:
                raise ValueError('native sampler differs: ' + key)
        record['wire_request'] = body

    async def wire_response(response):
        record = active.get()
        if record is not None and response.request.url.path == '/inference/v1/generate':
            await response.aread()
            record['wire_response'] = {'http_status': response.status_code, 'body': response.text}

    async def get_response(client, dialect, body, sampling, session_id=None, turn=None, headers=None):
        incoming = {k.lower(): v for k, v in (headers or {}).items()}
        record = {'index': len(rows), 'session_id': session_id, 'started': time.time(),
            'phase': incoming.get('x-mrcr-submit-phase'), 'depth': incoming.get('x-mrcr-submit-depth'),
            'nano_request_id': incoming.get('x-mrcr-submit-request'),
            'request': copy.deepcopy(body), 'sampling': sampling.model_dump(mode='json'), 'status': 'not_dispatched'}
        rows.append(record)
        token = active.set(record)
        try:
            if body['model'] != expected_alias or record['depth'] not in {'0', '1'}:
                raise ValueError('native role/alias metadata missing')
            budget.reserve(record['phase'], int(record['depth']))
            client.client.max_retries = 0
            transport = client.client._client
            if transport not in clients:
                transport.event_hooks['request'].append(wire_request)
                transport.event_hooks['response'].append(wire_response)
                clients.append(transport)
            write_once(output / f"{record['index']:03d}-start.json", record)
            response = await original(client, dialect, body, sampling, session_id=session_id, turn=turn, headers=headers)
            payload = response.model_dump(mode='json')
            tokens = payload['tokens']
            prompt, actions, logprobs = tokens['prompt_ids'], tokens['completion_ids'], tokens['completion_logprobs']
            if not prompt or not actions or len(actions) != len(logprobs) or any(not math.isfinite(x) or x == -9999 for x in logprobs):
                raise ValueError('invalid native physical action evidence')
            if record['wire_request']['token_ids'] != prompt or response.model != expected_alias:
                raise ValueError('native physical prefix/returned alias mismatch')
            record.update(status='returned', response=payload, logical_input_tokens=len(prompt),
                          action_tokens=len(actions), finish_reason=response.finish_reason,
                          provider_usage=payload.get('usage'), cached_input_tokens=None,
                          cache_accounting='native generate exposes no cached-token measurement')
            return response
        except BaseException as error:
            record.update(status='error', error_type=type(error).__name__, error=str(error))
            raise
        finally:
            record['ended'] = time.time()
            write_once(output / f"{record['index']:03d}-result.json", record)
            active.reset(token)

    TrainClient.get_response = get_response
    renderer_client.generate = observed_generate
    try:
        yield rows
    finally:
        TrainClient.get_response = original
        renderer_client.generate = original_generate
        for client in clients:
            client.event_hooks['request'].remove(wire_request)
            client.event_hooks['response'].remove(wire_response)
