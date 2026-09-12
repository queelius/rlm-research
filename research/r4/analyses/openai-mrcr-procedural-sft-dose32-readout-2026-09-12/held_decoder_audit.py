"""Held extension: inert native-final fidelity and lexical-selector diagnosis."""

import ast
import argparse
import json
from pathlib import Path

import decoder_audit as audit


def assigned_literal(program, name):
    """Read a literal AST node only. Never evaluate or execute generated Python."""
    for node in ast.walk(ast.parse(program)):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            if isinstance(node.value, ast.Constant):
                return node.value.value
    return None


def compact_differences(source, destination):
    result = audit.differences(source, destination)
    for row in result:
        for name in ('source_text','destination_text'):
            value=row[name]
            row[name+'_utf8_sha256']=audit.sha_text(value)
            if len(value)>120:
                row[name]=None
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    read, digest = audit.read, audit.sha_text
    report_path = audit.ROOT/'main-final-held-snapshot-001/REPORT.json'
    report = read(report_path)
    assert audit.SOURCE_SHA256[str(report_path)] == '32b72266cf8d2484f4c21db55650d38274990afc88f60dfe2ccfeb2a16bc3a51'
    golds = read(audit.SIDE/'openai-mrcr-procedural-sft-eval-v1/inputs/held/HOST_GOLD.json')
    train_audit = read(audit.ROOT/'DECODER_SEAM.json')
    tokenizer = audit.AutoTokenizer.from_pretrained(str(audit.BASE), local_files_only=True)
    renderer = audit.Qwen3Renderer(tokenizer)
    stops = {renderer._im_end, renderer._endoftext}
    arms = {}
    for arm in ('held_base', 'held_checkpoint32'):
        stage = report['stages'][arm]
        native = [(p,read(p)) for p in sorted((Path(stage['attempt'])/'science/native-calls').glob('*-result.json'))]
        rows = []
        for old in stage['rows']:
            episode = read(old['episode_path'])
            trace = episode['episode']['traces'][0]
            final = trace.get('root_reply')
            gold = golds[old['record_id']]['answer']
            assert old['raw_exact'] == (isinstance(final,str) and final == gold)
            root_alias = trace['agent']['config']['model']
            candidates = [(p,n) for p,n in native if n.get('status')=='returned'
                          and n.get('session_id')==trace['id'] and n.get('model')==root_alias
                          and not n['response']['message'].get('tool_calls')]
            assert len(candidates) <= 1
            row = {'record_id':old['record_id'], 'coordinate_id':old['coordinate_id'],
                   'seed':old['seed'], 'available':old['available'], 'original_raw_exact':old['raw_exact'],
                   'episode_path':old['episode_path'], 'episode_sha256':audit.SOURCE_SHA256[old['episode_path']],
                   'gold_utf8_sha256':digest(gold), 'root_final_utf8_sha256':digest(final) if isinstance(final,str) else None,
                   'role_ordinal_successor_candidate':old['any_role_ordinal_successor_pattern'],
                   'held_teacher_ast_exact':'NOT_APPLICABLE_NO_HELD_TEACHERS',
                   'clean_correct_target_observed':old['retrieval_copy']['clean_correct_target_observed'],
                   'native_final_present':bool(candidates), 'failure_class':old['failure_class'],
                   'gold_to_root_diff':compact_differences(gold,final) if isinstance(final,str) else None}
            if candidates:
                path,n = candidates[0]
                ids=n['response']['tokens']['completion_ids']; saved=n['response']['message']['content']
                parsed=renderer.parse_response(ids)
                assert (parsed.content or None)==saved
                assert (saved or '')==(final or '')
                assert audit.canonical_sha(ids)==n['evidence']['completion_ids_sha256']
                content_ids=audit._strip_stop_tokens(ids,stops)
                wire=tokenizer.decode(content_ids,skip_special_tokens=False)
                special=[i for i,t in enumerate(content_ids) if t in tokenizer.all_special_ids]
                markers=[m for m in ('<think>','</think>','<tool_call>','</tool_call>','<tool_response>','</tool_response>') if m in wire]
                bare=not special and not markers and not parsed.reasoning_content and not parsed.tool_calls
                row.update({'native_path':str(path),'native_sha256':audit.SOURCE_SHA256[str(path)],
                            'completion_ids_sha256':audit.canonical_sha(ids),'completion_tokens':len(ids),
                            'first_stop_position':next((i for i,t in enumerate(ids) if t in stops),None),
                            'raw_action_before_stop_utf8_sha256':digest(wire),
                            'saved_native_content_utf8_sha256':digest(saved) if isinstance(saved,str) else None,
                            'actual_parser_reproduces_saved_native':True,
                            'special_positions':special,'protocol_markers':markers,
                            'parsed_tool_statuses':[str(t.status) for t in parsed.tool_calls],
                            'bare_semantic_final_span':bare,
                            'bare_semantic_exact_DIAGNOSTIC_ONLY':wire==gold if bare else None,
                            'semantic_to_native_diff':compact_differences(wire,saved or '') if bare else None,
                            'gold_to_semantic_diff':compact_differences(gold,wire) if bare else None})
                if not bare:
                    row['semantic_scope_note']='Tool/reasoning/protocol-bearing wire is not credited as final-answer content.'
                row['category']=('original_raw_exact' if old['raw_exact'] else
                                 'parser_only_lost_exact' if bare and wire==gold else
                                 'model_edge_whitespace_difference' if bare and wire.strip()==gold.strip() else
                                 'model_other_text_difference' if bare else 'not_bare_final_span')
            else:
                row['category']='no_native_final_unavailable'
            if arm=='held_checkpoint32' and not old['retrieval_copy']['clean_correct_target_observed']:
                context=audit.SIDE/'openai-mrcr-procedural-sft-eval-v1/inputs/held/contexts'/f"{old['context_sha256']}.json"
                doc=read(context)
                requests=[assigned_literal(p['code_inert'],'request_text') for p in old['programs']]
                observed_errors=[(n.get('message') or {}).get('content') for n in trace['nodes']
                                 if (n.get('message') or {}).get('role')=='tool']
                row['selector_diagnosis']={
                    'context_path':str(context),'context_sha256':audit.SOURCE_SHA256[str(context)],
                    'task_question':doc[-1]['content'], 'generated_request_text_literals':requests,
                    'generated_program_utf8_sha256':[digest(p['code_inert']) for p in old['programs']],
                    'request_literal_matches':[sum(m.get('role')=='user' and m.get('content','').strip().casefold()==value.casefold() for m in doc[:-1]) for value in requests],
                    'actual_user_records_excluding_intro':[{'index':i,'content':m['content']} for i,m in enumerate(doc[:-1]) if i and m.get('role')=='user'],
                    'gold_assistant_indices':old['retrieval_copy']['gold_document_indices'],
                    'tool_error_observations':observed_errors,
                    'cause':'Generated email-to-message lexical substitution leaves zero matching user records. Repair attempts retain the wrong request literal.'}
            rows.append(row)
        arms[arm]={'original_summary':stage['summary'], 'category_counts':{c:sum(r['category']==c for r in rows) for c in sorted({r['category'] for r in rows})},
                   'bare_semantic_exact_DIAGNOSTIC_ONLY':sum(r.get('bare_semantic_exact_DIAGNOSTIC_ONLY') is True for r in rows),
                   'bare_semantic_rows':sum(r.get('bare_semantic_final_span') is True for r in rows), 'rows':rows}
    for p,want in train_audit['source_sha256'].items():
        if '/research-cache/' in p:
            assert audit.sha_bytes(Path(p).read_bytes())==want,p
            audit.SOURCE_SHA256[p]=want
    for p in (Path(__file__),audit.ROOT/'decoder_audit.py'):
        audit.SOURCE_SHA256[str(p)]=audit.sha_bytes(p.read_bytes())
    result={'schema':'procedural_sft_fixed_held_decoder_extension_v1',
                      'source_report':str(report_path),'source_report_sha256':audit.SOURCE_SHA256[str(report_path)],
                      'original_metrics_unchanged':True,'arms':arms,'paired_result':{k:v for k,v in report['held_pairing'].items() if not isinstance(v,list)},
                      'source_sha256':audit.SOURCE_SHA256,'generated_programs_executed':False,'model_calls':0,'gpu_used':False,
                      'scope':'Exact bare semantic content before configured first stop only; protocol-bearing action wire never treated as an answer. Diagnostic only, no score rewrite.',
                      'limits':['Fixed exploratory held panel, 16 contexts with two seeds each, not 32 independent contexts.',
                                'Earlier adaptive exposure possible; no confirmatory generalization claim.',
                                'Held teacher AST exact field is not applicable, not failed acquisition.']}
    payload=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    if args.output:
        with args.output.open('x') as output:
            output.write(payload)
        print(json.dumps({'path':str(args.output),'sha256':audit.sha_text(payload),
                          'arms':{k:{'counts':v['category_counts'],'bare_exact':v['bare_semantic_exact_DIAGNOSTIC_ONLY'],'bare_rows':v['bare_semantic_rows']} for k,v in arms.items()}}))
    else:
        print(payload,end='')


if __name__=='__main__':
    main()
