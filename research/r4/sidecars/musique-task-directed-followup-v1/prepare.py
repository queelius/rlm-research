"""Fresh outcome-blind train12 freeze; annotations remain private host inputs."""
from collections import Counter
import hashlib
import json
import os
import zipfile
import study as s


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert s.sha(s.ARCHIVE) == s.ARCHIVE_SHA
    if s.INPUTS.exists(): raise FileExistsError('inputs already frozen')
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(s.MODEL, local_files_only=True)
    old = s.read(s.PRIOR / 'inputs/host/HOST_GOLD.json')
    seen_questions = {' '.join(v['source_row']['question'].lower().split()) for v in old.values()}
    seen_components = {d['id'] for v in old.values() for d in v['source_row']['question_decomposition']}
    seen_supports = {s.digest([p['title'], p['paragraph_text']]) for v in old.values() for p in v['source_row']['paragraphs'] if p['is_supporting']}
    with zipfile.ZipFile(s.ARCHIVE) as archive:
        rows = [(json.loads(raw), raw) for raw in archive.open('data/musique_ans_v1.0_train.jsonl')]
    ranked = sorted(rows, key=lambda pair: s.digest([s.NAMESPACE, s.digest(pair[0])]))
    counts, skips, selected, gold = Counter(), Counter(), [], {}
    for row, raw in ranked:
        hop = len(row['question_decomposition'])
        if hop not in (2,3,4) or counts[hop] >= 4: continue
        components = {d['id'] for d in row['question_decomposition']}
        supports = {s.digest([p['title'], p['paragraph_text']]) for p in row['paragraphs'] if p['is_supporting']}
        question = ' '.join(row['question'].lower().split())
        if question in seen_questions or components & seen_components or supports & seen_supports:
            skips['exact_question_component_support_overlap'] += 1; continue
        public = s.public_row(row)
        rendered = json.dumps(public, ensure_ascii=False, separators=(',', ':'))
        ntokens = len(tokenizer.encode(rendered, add_special_tokens=False))
        if ntokens > 5500: skips['public_token_bound'] += 1; continue
        opaque = 'q' + s.digest([s.NAMESPACE, 'opaque', s.digest(row)])[:20]
        halves = s.partition(public, opaque)
        # All source paragraphs remain; only the supplied partition changes access per child.
        assert sorted(p['idx'] for half in halves for p in half) == list(range(len(public['paragraphs'])))
        initial = {r: s.request(s.report_messages(public, halves, i), r, s.seed(len(selected), r), len(public['paragraphs']), tokenizer)
                   for i, r in enumerate(('report_left', 'report_right'))}
        initial['full_source'] = s.request(s.messages(public, s.FINAL), 'full_source', s.seed(len(selected), 'full_source'), len(public['paragraphs']), tokenizer)
        s.write_x(s.INPUTS / 'public' / (opaque + '.json'), public)
        s.write_x(s.INPUTS / 'static' / (opaque + '.json'), initial)
        selected.append({'record_id': opaque, 'source_id': row['id'], 'source_split': 'MuSiQue-Ans v1.0 train',
            'raw_line_sha256': hashlib.sha256(raw).hexdigest(), 'canonical_row_sha256': s.digest(row),
            'rank_sha256': s.digest([s.NAMESPACE, s.digest(row)]), 'hop_count': hop,
            'paragraph_count': len(public['paragraphs']), 'public_qwen_tokens': ntokens,
            'public_path': str(s.INPUTS / 'public' / (opaque + '.json')),
            'public_sha256': s.sha(s.INPUTS / 'public' / (opaque + '.json')),
            'partition_indices': [[p['idx'] for p in half] for half in halves],
            'component_ids': sorted(components), 'support_paragraph_sha256': sorted(supports),
            'static_max_prefix_plus_output': max(len(v['token_ids']) + v['sampling_params']['max_tokens'] for v in initial.values())})
        gold[opaque] = {'answer': row['answer'], 'answer_aliases': row['answer_aliases'],
                        'support_idxs': [p['idx'] for p in row['paragraphs'] if p['is_supporting']],
                        'source_row': row, 'raw_line_utf8': raw.decode()}
        seen_questions.add(question); seen_components.update(components); seen_supports.update(supports); counts[hop] += 1
        if len(selected) == 12: break
    assert len(selected) == 12 and dict(counts) == {2:4,3:4,4:4}
    schedule = []
    for index, item in enumerate(selected):
        for role in s.roles():
            coordinate = {'record_id': item['record_id'], 'question_index': index, 'role': role,
                'seed': s.seed(index, role), 'max_tokens': s.output_cap(role), 'temperature': .5}
            schedule.append({**coordinate, 'call_id': s.digest([s.NAMESPACE, coordinate])})
    s.write_x(s.INPUTS / 'SCHEDULE.json', schedule)
    s.write_x(s.INPUTS / 'host/HOST_GOLD.json', gold); (s.INPUTS / 'host/HOST_GOLD.json').chmod(0o600)
    s.write_x(s.INPUTS / 'MANIFEST.json', {'namespace': s.NAMESPACE, 'selected': selected, 'archive_sha256': s.ARCHIVE_SHA,
        'source_member': 'data/musique_ans_v1.0_train.jsonl', 'source_commit': '922ac98f19a201998dbdae6d7f2887a5258dbdeb',
        'license': 'CC-BY-4.0 per official repository; retain underlying-source attribution',
        'excluded_prior_manifest_sha256': s.sha(s.PRIOR / 'inputs/MANIFEST.json'), 'skips': dict(skips),
        'selection': 'full canonical row hash rank, four per hop, <=5500 public Qwen tokens; no exact normalized-question/component/support reuse against prior12 or selected12',
        'partition': 'opaque ID + original paragraph index hash ranking; balanced halves, original relative order within each half',
        'no_model_queries': True, 'no_model_output_selection': True, 'gold_in_prompts': False,
        'public_original_paragraphs_preserved': True, 'pretraining_exposure_unknown': True,
        'dynamic_prefix_bound': 'Each actual native prefix plus requested output must fit8192; no truncation or fallback.'})
    print({'selected': len(selected), 'hop_counts': dict(counts), 'calls': len(schedule), 'static_context_max': max(r['static_max_prefix_plus_output'] for r in selected)})


if __name__ == '__main__': main()
