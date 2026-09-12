"""Additive CPU diagnosis. Emits JSON only; never executes generated programs."""

from __future__ import annotations

import asyncio
import difflib
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from transformers import AutoTokenizer
from renderers.qwen3 import Qwen3Renderer
from renderers.parsing import _strip_stop_tokens
from verifiers.v1.acp import ACPConfig, ACPHarnessSession


ROOT = Path(__file__).resolve().parent
STORE = Path('/project/alex_phd/runs/rlm-research-r4')
SIDE = STORE / 'sidecars'
DEPS = Path('/project/alex_phd/research-cache/repos/prime-rl/deps')
BASE = Path('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554')
SOURCE_SHA256 = {}


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_text(value):
    return sha_bytes(value.encode('utf-8'))


def canonical_sha(value):
    return sha_text(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False))


def read(path):
    path = Path(path)
    data = path.read_bytes()
    SOURCE_SHA256[str(path)] = sha_bytes(data)
    return json.loads(data)


def differences(source, destination):
    return [{'operation': op, 'source_start': i, 'source_end': j,
             'destination_start': k, 'destination_end': l,
             'source_text': source[i:j], 'destination_text': destination[k:l]}
            for op, i, j, k, l in difflib.SequenceMatcher(None, source, destination, autojunk=False).get_opcodes()
            if op != 'equal']


async def acp_proof(value):
    """Exercise the actual host ACP method with a typed fake transport packet."""
    class Process:
        async def write(self, packet):
            self.last_packet = packet

    class Reader:
        async def read(self):
            return {'ok': True, 'result': {'reply': value, 'stop_reason': 'end_turn',
                                          'response_metadata': {}, 'update_metadata': []}}

    session = object.__new__(ACPHarnessSession)
    session.config = ACPConfig(env={}, command=[], prompt='fixture')
    session._lock = asyncio.Lock()
    session._closed = False
    session.mcp_urls = {}
    session._process = Process()
    session._reader = Reader()
    session.trace = SimpleNamespace(calls=[], stop_condition='agent_completed', root_reply=None)
    session.harness = SimpleNamespace(_consume_protocol_metadata=lambda *args: None,
                                      acp_turn_result=lambda *args: None)
    result = await session._run(None)
    assert result.stdout == value and session.trace.root_reply == value.strip()
    return {'input_repr': repr(value), 'stdout_repr': repr(result.stdout),
            'scored_root_reply_repr': repr(session.trace.root_reply),
            'input_sha256': sha_text(value), 'stdout_sha256': sha_text(result.stdout),
            'root_reply_sha256': sha_text(session.trace.root_reply),
            'actual_host_ACPHarnessSession_run': True, 'fake_transport_only': True,
            'full_native_agent_roundtrip': False,
            'difference_stdout_to_root': differences(result.stdout, session.trace.root_reply)}


def main():
    report_path = ROOT / 'train32-terminal-snapshot-001/REPORT.json'
    report = read(report_path)
    stage = report['stages']['train_checkpoint32']
    gold_path = SIDE / 'openai-mrcr-procedural-sft-eval-v1/inputs/train/HOST_GOLD.json'
    golds = read(gold_path)
    science = SIDE / 'openai-mrcr-procedural-sft-continue32-eval-v1/outputs/train32-001/science'
    native = [(p, read(p)) for p in sorted((science / 'native-calls').glob('*-result.json'))]
    tokenizer = AutoTokenizer.from_pretrained(str(BASE), local_files_only=True)
    renderer = Qwen3Renderer(tokenizer)
    stop_ids = {renderer._im_end, renderer._endoftext}
    rows = []
    for old in stage['rows']:
        episode = read(old['episode_path'])
        trace = episode['episode']['traces'][0]
        root = trace['root_reply']
        matches = [(p, n) for p, n in native if n.get('session_id') == trace['id']
                   and n.get('status') == 'returned'
                   and n.get('model') == 'Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step32'
                   and not n['response']['message'].get('tool_calls')]
        assert len(matches) == 1
        path, n = matches[0]
        ids = n['response']['tokens']['completion_ids']
        parsed = renderer.parse_response(ids)
        saved_parsed = n['response']['message']['content']
        assert parsed.content == saved_parsed == root
        assert not parsed.reasoning_content and not parsed.tool_calls
        assert canonical_sha(ids) == n['evidence']['completion_ids_sha256']
        stop_positions = [i for i, token in enumerate(ids) if token in stop_ids]
        assert stop_positions == [len(ids) - 1], stop_positions
        semantic_ids = _strip_stop_tokens(ids, stop_ids)
        semantic = tokenizer.decode(semantic_ids, skip_special_tokens=False)
        special_positions = [{'index': i, 'token_id': token} for i, token in enumerate(semantic_ids)
                             if token in tokenizer.all_special_ids]
        markers = [marker for marker in ('<think>', '</think>', '<tool_call>', '</tool_call>',
                                         '<tool_response>', '</tool_response>', '<|im_start|>',
                                         '<|im_end|>', '<|endoftext|>') if marker in semantic]
        assert not markers and not special_positions
        gold = golds[old['record_id']]['answer']
        if root == gold:
            category = 'original_raw_exact'
        elif semantic == gold:
            category = 'parser_only_lost_exact'
        elif semantic == gold + '\n\n':
            category = 'model_added_two_newlines_and_parser_removed_gold_spaces'
        elif semantic == gold[:-2] and gold.endswith('  '):
            category = 'model_omitted_two_gold_spaces'
        else:
            category = 'model_other_text_change'
        rows.append({
            'record_id': old['record_id'], 'seed': old['seed'],
            'episode_path': old['episode_path'], 'episode_sha256': SOURCE_SHA256[old['episode_path']],
            'native_path': str(path), 'native_sha256': SOURCE_SHA256[str(path)],
            'completion_ids_sha256': canonical_sha(ids), 'completion_tokens': len(ids),
            'semantic_completion_ids_sha256': canonical_sha(semantic_ids),
            'stop_token_id': ids[-1], 'stop_positions': stop_positions,
            'special_tokens_inside_semantic_span': special_positions,
            'reasoning_or_tool_markers_inside_semantic_span': markers,
            'parsed_reasoning_content': parsed.reasoning_content, 'parsed_tool_calls': [],
            'decoded_semantic_final_sha256': sha_text(semantic),
            'native_parsed_final_sha256': sha_text(saved_parsed),
            'trace_root_final_sha256': sha_text(root), 'gold_utf8_sha256': sha_text(gold),
            'gold_characters': len(gold), 'semantic_characters': len(semantic),
            'native_parsed_characters': len(saved_parsed), 'root_final_characters': len(root),
            'teacher_ast_exact': old['first_teacher_ast_exact'],
            'clean_correct_target_observed': old['retrieval_copy']['clean_correct_target_observed'],
            'original_raw_exact': root == gold,
            'decoded_semantic_exact_DIAGNOSTIC_ONLY': semantic == gold,
            'actual_parser_reproduces_saved_native': parsed.content == saved_parsed,
            'category': category,
            'edits_gold_to_semantic': differences(gold, semantic),
            'edits_semantic_to_native_parsed': differences(semantic, saved_parsed),
            'edits_native_parsed_to_trace_root': differences(saved_parsed, root),
            'edits_gold_to_trace_root': differences(gold, root),
            'semantic_tail_repr': repr(semantic[-100:]), 'completion_token_tail': ids[-12:],
        })
    assert len(rows) == 32
    counts = {key: sum(r['category'] == key for r in rows) for key in sorted({r['category'] for r in rows})}
    assert counts == {'original_raw_exact': 24, 'parser_only_lost_exact': 3,
                      'model_added_two_newlines_and_parser_removed_gold_spaces': 1,
                      'model_omitted_two_gold_spaces': 3, 'model_other_text_change': 1}
    assert all(r['teacher_ast_exact'] and r['clean_correct_target_observed'] for r in rows)
    sources = [Path(__file__), BASE/'config.json', BASE/'tokenizer.json', BASE/'tokenizer_config.json']
    sources += [DEPS/'renderers/renderers'/n for n in ('__init__.py','base.py','parsing.py','qwen3.py','client.py')]
    sources += [DEPS/'verifiers/verifiers/v1'/n for n in ('clients/train.py','acp/__init__.py',
                                                       'harnesses/rlm/harness.py','trace.py','agent.py')]
    sources += [SIDE / s / 'collect.py' for s in ('openai-mrcr-procedural-sft-eval-v1',
                                                'openai-mrcr-procedural-sft-continue32-eval-v1')]
    for path in sources:
        SOURCE_SHA256[str(path)] = sha_bytes(path.read_bytes())
    result = {
        'schema': 'procedural_sft_train32_decoder_seam_v1',
        'source_report': str(report_path), 'source_report_sha256': SOURCE_SHA256[str(report_path)],
        'original_scoring_unchanged': True, 'train_available': 32, 'original_raw_exact': 24,
        'decoded_semantic_exact_DIAGNOSTIC_ONLY': 27,
        'all_final_actions_bare_content_with_one_terminal_stop': True,
        'semantic_scope': 'Exact tokenizer decode of action tokens before the first configured stop token; all 32 have no reasoning, tool, or special tokens in that span. No whitespace normalization.',
        'hash_conventions': {'text': 'SHA256 of exact UTF-8 bytes',
                             'token_ids': 'SHA256 of JSON sort_keys=True separators=comma-colon (integer list)',
                             'files': 'SHA256 of exact file bytes',
                             'diff_offsets': 'Zero-based Python Unicode code-point half-open ranges; SequenceMatcher autojunk=False'},
        'category_counts': counts, 'rows': rows,
        'actual_acp_host_fixtures': [asyncio.run(acp_proof(text)) for text in
                                    ('marker exact target  ', '  marker\ncurly ’ target  \n\n')],
        'source_sha256': SOURCE_SHA256,
        'generated_programs_executed': False, 'model_calls': 0, 'gpu_used': False,
        'limits': ['Train-fit diagnosis, not held transfer.',
                   '27/32 is an inert token-level diagnostic, not a new scored rollout.',
                   'Host ACP fixture is not a full native agent roundtrip.',
                   'Reasoning branch and tool parser are not modified; terminal-strip ablation would not be a general lossless parser.',
                   'No gold-dependent answer repair, checkpoint selection, or metric rewrite.'],
    }
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
