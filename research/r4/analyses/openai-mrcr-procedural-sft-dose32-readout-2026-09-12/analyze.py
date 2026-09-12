"""One-shot, CPU-only fixed-dose readout analysis. Generated Python is never executed."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time


ROOT = Path(__file__).resolve().parent
STORE = Path('/project/alex_phd/runs/rlm-research-r4')
SIDE = STORE / 'sidecars'
OLD_TRAIN = SIDE / 'openai-mrcr-procedural-sft-warmstart-v1'
NEW_TRAIN = SIDE / 'openai-mrcr-procedural-sft-continue32-v1'
OLD_EVAL = SIDE / 'openai-mrcr-procedural-sft-eval-v1'
NEW_EVAL = SIDE / 'openai-mrcr-procedural-sft-continue32-eval-v1'
CORPUS = OLD_TRAIN / 'TEACHER_CORPUS_V2.json'
PRIOR = STORE / 'analyses/openai-mrcr-procedural-sft-observer-2026-09-12/observe.py'
READY = ROOT / 'CPU_READY.json'
STAGES = {
    'train_checkpoint4': (OLD_EVAL / 'outputs/train-readout-001', 'train', 4),
    'train_checkpoint32': (NEW_EVAL / 'outputs/train32-001', 'train', 32),
    'held_base': (NEW_EVAL / 'outputs/held-base-001', 'held', 0),
    'held_checkpoint32': (NEW_EVAL / 'outputs/held-checkpoint32-001', 'held', 32),
}
SOURCE_SHA256 = {}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def read(path):
    path = Path(path)
    payload = path.read_bytes()
    SOURCE_SHA256[str(path)] = hashlib.sha256(payload).hexdigest()
    return json.loads(payload)


def load_prior():
    spec = importlib.util.spec_from_file_location('dose32_prior_observer', PRIOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def program_features(code, teacher_code):
    """Pattern flags are diagnostics, not a proof that arbitrary code is correct."""
    result = {'code_sha256': digest(code), 'characters': len(code), 'parseable': False,
              'teacher_ast_exact': False, 'role_tests': False, 'successor_index': False,
              'ordinal_index': False, 'top_level_dict_assumption': False,
              'broad_document_dump': False}
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return result
    nodes = list(ast.walk(tree))
    result['parseable'] = True
    if teacher_code:
        result['teacher_ast_exact'] = ast.dump(tree) == ast.dump(ast.parse(teacher_code))
    # Track the actual names assigned a parsed JSON document. Existing actions commonly
    # retain data/messages across REPL turns, so those two names remain diagnostic aliases.
    documents = {'data', 'messages'}
    for node in nodes:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            fn = node.value.func
            if isinstance(fn, ast.Attribute) and fn.attr in {'load', 'loads'}:
                documents.update(t.id for t in node.targets if isinstance(t, ast.Name))
    literal = lambda n, value: isinstance(n, ast.Constant) and n.value == value
    is_document = lambda n: isinstance(n, ast.Name) and n.id in documents
    constants = {n.value for n in nodes if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    result['role_tests'] = 'role' in constants and {'user', 'assistant'} <= constants
    for node in nodes:
        if isinstance(node, ast.Subscript):
            sl = node.slice
            result['successor_index'] |= isinstance(sl, ast.BinOp) and isinstance(sl.op, ast.Add) and (literal(sl.left, 1) or literal(sl.right, 1))
            result['ordinal_index'] |= isinstance(sl, ast.BinOp) and isinstance(sl.op, ast.Sub) and literal(sl.right, 1)
            result['top_level_dict_assumption'] |= is_document(node.value) and isinstance(sl, ast.Constant) and isinstance(sl.value, str)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            result['top_level_dict_assumption'] |= is_document(node.func.value) and node.func.attr in {'get', 'keys', 'items', 'values'}
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
            for arg in node.args:
                result['broad_document_dump'] |= is_document(arg) or (isinstance(arg, ast.Subscript) and is_document(arg.value) and isinstance(arg.slice, (ast.Slice, ast.Constant)))
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'dumps':
                    result['broad_document_dump'] |= any(is_document(v) for v in arg.args)
    return result


def native_evidence(trace_id, reply, root_alias, native_rows, expected_prefix):
    rows = sorted((r for r in native_rows if r.get('session_id') == trace_id and r.get('model') == root_alias), key=lambda r: r['index'])
    returned = [r for r in rows if r.get('status') == 'returned']
    prefix = ((returned[0].get('response') or {}).get('tokens') or {}).get('prompt_ids') if returned else None
    finals = [(r.get('response') or {}).get('message') or {} for r in returned]
    finals = [m for m in finals if not m.get('tool_calls')]
    # A nonempty scored answer must be independently present in a raw native final.
    match = any(m.get('content') == reply for m in finals) if isinstance(reply, str) and reply else None
    return {'native_initial_prefix_exact': prefix == expected_prefix,
            'native_initial_prefix_sha256': digest(prefix) if prefix is not None else None,
            'native_final_exact_to_trace': match, 'native_root_returned': len(returned),
            'native_error_rows': [{'index': r['index'], 'error': r.get('error')} for r in rows if r.get('status') != 'returned']}


def validate_binding(binding, step):
    base_alias = 'Qwen3-4B-Instruct-2507-procedural-eval-zero'
    expected_alias = f'Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step{step}' if step else base_alias
    eval_root = OLD_EVAL if step == 4 else NEW_EVAL
    training = OLD_TRAIN if step == 4 else NEW_TRAIN
    path = training/f'outputs/attempt-001/checkpoint-{step:04d}' if step else eval_root/'checkpoint-artifacts/base-zero-adapter'
    model = binding.get('models', {}).get(expected_alias, {})
    if (binding.get('role_map') != {'root':expected_alias,'children':[base_alias]}
            or binding.get('fixed_child') != base_alias or model.get('path') != str(path)
            or binding.get('selection_path') != str(eval_root/'checkpoint-artifacts/CHECKPOINT_READY.json')):
        raise ValueError('fixed root/child binding differs')
    return expected_alias


def retrieval_copy_evidence(observations, reply, gold, document):
    marker, answer = gold['random_string_to_prepend'], gold['answer']
    target = answer.removeprefix(marker)
    # Exact clean stdout with its optional single print newline, never reward repair.
    matches = lambda text, value: text == value or text == value+'\n'
    correct = any(matches(v, answer) or matches(v, target) for v in observations)
    printed = sorted({i for i,m in enumerate(document) for v in observations
                      if matches(v,m.get('content','')) or matches(v,marker+m.get('content',''))})
    expected = {i for i,m in enumerate(document) if m.get('content')==target}
    return {'clean_correct_target_observed':correct,'clean_printed_document_indices':printed,
            'gold_document_indices':sorted(expected),
            'clean_wrong_record_printed':bool(set(printed)-expected) and not correct,
            'correct_print_then_nonempty_wrong_final':bool(correct and isinstance(reply,str) and reply and reply!=answer),
            'correct_print_then_final_absent':bool(correct and not reply),
            'newline_only_repair_would_match_DIAGNOSTIC_ONLY':isinstance(reply,str) and reply!=answer and reply.replace('\\n','\n')==answer}


def stage_report(directory, phase, step, teachers, prior):
    public = read(OLD_EVAL / 'inputs' / phase / 'PUBLIC.json')
    plan = {c['id']: c for c in public['plan']}
    result_path, owner_path = directory / 'science/RESULT.json', directory / 'OWNER_TERMINAL.json'
    base = {'attempt': str(directory), 'phase': phase, 'fixed_step': step, 'rows': [], 'integrity_errors': [],
            'status': 'PENDING_NO_TERMINAL_SNAPSHOT', 'summary': {'planned': len(plan), 'recorded': 0, 'available': 0, 'raw_exact': 0},
            'train_gate': prior.train_gate([]) if phase == 'train' else None}
    # Never race a live writer or infer a final result from partial episode/checkpoint files.
    if not (result_path.exists() and owner_path.exists()):
        return base
    collector, owner = read(result_path), read(owner_path)
    binding = read(directory/'owned-service/BINDING.json')
    expected_root_alias = validate_binding(binding, step)
    selection_path = Path(binding['selection_path']); receipt = read(selection_path)
    if (binding['selection_sha256'] != SOURCE_SHA256[str(selection_path)]
            or collector.get('checkpoint_receipt_sha256') != SOURCE_SHA256[str(selection_path)]
            or receipt.get('identity') != digest({k:v for k,v in receipt.items() if k!='identity'})
            or receipt.get('fixed_primary_step') != (4 if step == 4 else 32)):
        raise ValueError('fixed checkpoint evaluation receipt differs')
    gold = read(OLD_EVAL / 'inputs' / phase / 'HOST_GOLD.json')
    prefixes = read(OLD_EVAL / 'inputs' / phase / 'PREFIXES.json')
    native = [read(p) for p in sorted((directory / 'science/native-calls').glob('*-result.json'))]
    rows, issues = [], []
    for path in sorted((directory / 'science/episodes').glob('*.json')):
        item = read(path); coordinate = item['coordinate']; ident = coordinate['id']
        if ident not in plan or coordinate != plan[ident] or path.stem != ident or digest(item['episode']) != item['episode_sha256']:
            raise ValueError('episode is outside frozen coordinate/raw export: ' + str(path))
        truth = gold[coordinate['record_id']]
        raw = item['episode']; traces = raw.get('traces') or []; trace = traces[0] if len(traces) == 1 else {}
        reply = trace.get('root_reply'); teacher = teachers.get(coordinate['record_id']) if phase == 'train' else None
        context = OLD_EVAL / 'inputs' / phase / 'contexts' / (coordinate['context_sha256'] + '.json')
        document = read(context)
        if SOURCE_SHA256[str(context)] != coordinate['context_sha256']:
            raise ValueError('context bytes differ from fixed coordinate')
        row = prior.score_episode(item, truth)
        row['raw_exact'] = isinstance(reply, str) and reply == truth['answer']
        row['available'] = bool(row['available'])
        programs = []; first = None
        for index, node in enumerate(trace.get('nodes') or []):
            message = node.get('message') or {}
            if message.get('role') == 'assistant' and first is None:
                first = message
            for call in message.get('tool_calls') or []:
                if call.get('name') != 'ipython':
                    continue
                args = call.get('arguments'); args = json.loads(args) if isinstance(args, str) else args
                code = args.get('code', '')
                programs.append({'node': index, 'code_inert': code, **program_features(code, teacher['authored_code'] if teacher else None)})
        obs = prior.observations(trace, truth, len(context.read_text()))
        observations = [(n.get('message') or {}).get('content', '') for n in trace.get('nodes') or [] if (n.get('message') or {}).get('role') == 'tool']
        schema_errors = [v for v in observations if re.search(r"(AttributeError: 'list' object|TypeError: list indices must be integers|KeyError:)", v)]
        root_alias = ((trace.get('agent') or {}).get('config') or {}).get('model')
        if trace and root_alias != expected_root_alias:
            issues.append({'coordinate':ident,'native_root_alias_differs':root_alias})
        evidence = native_evidence(trace.get('id'), reply, root_alias, native, prefixes[ident]['token_ids'])
        first_code = programs[0] if programs and first and first.get('tool_calls') else {}
        marker = truth['random_string_to_prepend']; body = reply[len(marker):] if isinstance(reply, str) and reply.startswith(marker) else None
        row.update(coordinate_id=ident, record_id=coordinate['record_id'], context_sha256=coordinate['context_sha256'],
                   repeat=coordinate['repeat'], seed=coordinate['seed'], episode_path=str(path),
                   first_action_sha256=digest(first), first_action=first, programs=programs, observations=obs,
                   first_teacher_ast_exact=first_code.get('teacher_ast_exact', False),
                   first_top_level_dict_assumption=first_code.get('top_level_dict_assumption', False),
                   any_successor_pattern=any(p['successor_index'] for p in programs),
                   any_role_ordinal_successor_pattern=any(p['role_tests'] and p['successor_index'] and p['ordinal_index'] for p in programs),
                   any_broad_dump=any(p['broad_document_dump'] for p in programs),
                   actual_schema_error_observations=len(schema_errors),
                   schema_error_tails=[v[-250:] for v in schema_errors],
                   final_body_document_indices=[i for i,m in enumerate(document) if body and m.get('content') == body],
                   final_body_intro_substring=bool(body and body in document[0].get('content', '')),
                   retrieval_copy=retrieval_copy_evidence(observations,reply,truth,document),
                   **evidence)
        row['teacher_program_success_evidence'] = bool(row['available'] and row['raw_exact'] and row['first_teacher_ast_exact']
                                                      and obs['tool_error_count'] == 0 and not row['any_broad_dump']
                                                      and evidence['native_final_exact_to_trace'] is True)
        # Other correct programs need inspection: AST pattern presence is deliberately not promoted.
        row['other_procedure_candidate_requires_review'] = bool(row['raw_exact'] and row['any_role_ordinal_successor_pattern'] and not row['teacher_program_success_evidence'])
        derived = item.get('derived') or {}
        for field, value in [('scientifically_available',row['available']), ('raw_exact',row['raw_exact']), ('reward',row['official_score'])]:
            if derived.get(field) != value:
                issues.append({'coordinate': ident, 'collector_disagreement': field})
        if (evidence['native_initial_prefix_sha256'] is not None and not evidence['native_initial_prefix_exact']) or evidence['native_final_exact_to_trace'] is False:
            issues.append({'coordinate': ident, 'native_prefix_or_final_disagreement': evidence})
        rows.append(row)
    if len({r['coordinate_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate frozen coordinate')
    available = [r for r in rows if r['available']]
    summary = {'planned':len(plan), 'recorded':len(rows), 'available':len(available),
               'raw_exact':sum(r['raw_exact'] for r in available), 'unavailable_recorded':len(rows)-len(available),
               'missing_coordinates':len(plan)-len(rows), 'first_teacher_ast_exact':sum(r['first_teacher_ast_exact'] for r in rows),
               'first_top_level_dict_assumption':sum(r['first_top_level_dict_assumption'] for r in rows),
               'any_successor_pattern':sum(r['any_successor_pattern'] for r in rows),
               'role_ordinal_successor_candidates':sum(r['any_role_ordinal_successor_pattern'] for r in rows),
               'episodes_with_actual_schema_error':sum(r['actual_schema_error_observations']>0 for r in rows),
               'episodes_with_broad_dump':sum(r['any_broad_dump'] for r in rows),
               'teacher_program_success_evidence':sum(r['teacher_program_success_evidence'] for r in rows),
               'exact_after_broad_dump':sum(r['raw_exact'] and r['available'] and r['any_broad_dump'] for r in rows),
               'exact_after_python_error':sum(r['raw_exact'] and r['available'] and r['observations']['tool_error_count']>0 for r in rows)}
    summary['clean_correct_target_observed'] = sum(r['retrieval_copy']['clean_correct_target_observed'] for r in rows)
    summary['correct_print_then_wrong_final_available'] = sum(r['available'] and r['retrieval_copy']['correct_print_then_nonempty_wrong_final'] for r in rows)
    summary['clean_wrong_record_printed'] = sum(r['retrieval_copy']['clean_wrong_record_printed'] for r in rows)
    for field in ('recorded','raw_exact'):
        if collector.get(field) != summary[field]: issues.append({'collector_summary_disagreement':field})
    if collector.get('scientifically_available') != summary['available']: issues.append({'collector_summary_disagreement':'scientifically_available'})
    gate = prior.train_gate(rows) if phase == 'train' else None
    if gate and gate['eligible'] != (collector.get('manipulation_gate') or {}).get('eligible'):
        issues.append({'collector_gate_disagreement':True})
    return {**base, 'status':'TERMINAL_SNAPSHOT', 'summary':summary, 'rows':rows, 'integrity_errors':issues,
            'train_gate':gate, 'owner_terminal':owner, 'collector_result':collector,
            'native_unknown_cost_calls':sum(r.get('status') != 'returned' for r in native)}


def paired(left, right):
    a, b = {r['coordinate_id']:r for r in left}, {r['coordinate_id']:r for r in right}
    pairs = []
    for ident in sorted(set(a)&set(b)):
        x,y = a[ident],b[ident]
        keys = ('record_id','context_sha256','repeat','seed')
        if any(x.get(k) != y.get(k) for k in keys):
            raise ValueError('paired coordinate/prefix differs: '+ident)
        left_prefix, right_prefix = x.get('native_initial_prefix_sha256'), y.get('native_initial_prefix_sha256')
        if left_prefix is not None and right_prefix is not None and left_prefix != right_prefix:
            raise ValueError('paired coordinate/prefix differs: '+ident)
        both = x['available'] and y['available'] and left_prefix is not None and right_prefix is not None
        pairs.append({'coordinate_id':ident,'record_id':x['record_id'],'paired_available':both,
                      'left_exact':x['raw_exact'] if both else None,'right_exact':y['raw_exact'] if both else None,
                      'first_action_equal':x['first_action_sha256']==y['first_action_sha256']})
    return {'matched_coordinates':len(pairs),'paired_available':sum(p['paired_available'] for p in pairs),
            'wins_right':sum(p['right_exact'] is True and p['left_exact'] is False for p in pairs),
            'losses_right':sum(p['left_exact'] is True and p['right_exact'] is False for p in pairs),
            'first_actions_equal':sum(p['first_action_equal'] for p in pairs), 'pairs':pairs}


def training_fit():
    output = {}
    for label,directory,step in [('checkpoint4',OLD_TRAIN,4),('checkpoint32',NEW_TRAIN,32)]:
        path = directory/'outputs/attempt-001/RESULT.json'
        if not path.exists():
            output[label] = {'status':'PENDING_FIXED_FINAL_RESULT'}; continue
        result = read(path)
        if result['optimizer_steps'] != step or result['primary_checkpoint'] != str(directory/f'outputs/attempt-001/checkpoint-{step:04d}'):
            raise ValueError('not the fixed training result')
        commit_path = Path(result['step_commits'][-1]['path']); commit = read(commit_path)
        if SOURCE_SHA256[str(commit_path)] != result['step_commits'][-1]['sha256']:
            raise ValueError('training final commit differs')
        state_path = commit_path.parent/'state.json'; state = read(state_path)
        if SOURCE_SHA256[str(state_path)] != commit['files_sha256']['state.json'] or state['optimizer_steps'] != step:
            raise ValueError('training fixed final state differs')
        metrics = [{k:v for k,v in metric.items() if k in ('step','action_objective','terminal_objective_weighted','weighted_ce','gradient_norm','delta_l2_from_start','delta_l2_from_resume_checkpoint4')} for metric in result['metrics']]
        output[label] = {'status':result['status'],'optimizer_steps':step,'corpus_sha256':result['corpus_sha256'],
                         'result_sha256':SOURCE_SHA256[str(path)],'final_commit_sha256':SOURCE_SHA256[str(commit_path)],'metrics':metrics}
    output['metric_timing'] = 'Teacher CE is measured before each update, not a post-checkpoint likelihood test; unchanged repeated train corpus, not transfer.'
    return output


def build_report():
    SOURCE_SHA256.clear()
    prior = load_prior(); corpus = read(CORPUS)
    teachers = {e['episode_id']:e['teacher'] for e in corpus['episodes']}
    stages = {name:stage_report(directory,phase,step,teachers,prior) for name,(directory,phase,step) in STAGES.items()}
    fit = training_fit(); new = stages['train_checkpoint32']; gate = new['train_gate']
    issues = [issue for stage in stages.values() for issue in stage['integrity_errors']]
    held_recorded = sum(stages[k]['summary']['recorded'] for k in ('held_base','held_checkpoint32'))
    train_owner = new.get('owner_terminal') or {}
    gate_open = bool(gate['eligible'] and train_owner.get('complete') is True and train_owner.get('released') is True and not train_owner.get('errors'))
    if held_recorded and not gate_open: issues.append({'held_records_without_eligible_completed_train_gate':held_recorded})
    receipt_path = NEW_EVAL/'checkpoint-artifacts/CHECKPOINT_READY.json'
    if any(stages[k]['status']=='TERMINAL_SNAPSHOT' for k in ('train_checkpoint32','held_base','held_checkpoint32')):
        if not receipt_path.exists():
            issues.append({'checkpoint32_evaluation_receipt_absent':True})
        else:
            receipt = read(receipt_path)
            if receipt.get('fixed_primary_step') != 32 or receipt['training']['training_result_sha256'] != fit['checkpoint32'].get('result_sha256'):
                issues.append({'checkpoint32_evaluation_receipt_training_link_differs':True})
    if issues:
        decision = 'HOLD_INTERPRETATION_SOURCE_OR_NATIVE_EVIDENCE_DISAGREEMENT'
    elif new['status'] != 'TERMINAL_SNAPSHOT':
        decision = 'PENDING_CHECKPOINT32_TRAIN_READOUT; lower teacher loss alone does not establish procedure acquisition'
    elif new['summary']['teacher_program_success_evidence']:
        decision = 'Some train episodes executed the exact authored teacher AST with raw-exact final and no Python error/dump; quantify extent separately from held transfer'
    elif new['summary']['role_ordinal_successor_candidates']:
        decision = 'Procedure-pattern candidates need inert human inspection; AST flags alone do not establish correct retrieval'
    else:
        decision = 'No observed role/ordinal/successor procedure evidence; any lower teacher loss or dump/copy exacts do not establish procedure acquisition'
    return {'schema':'procedural-sft-fixed-dose32-readout-analysis-v1','created_epoch':time.time(),
            'training':fit,'stages':stages,'train_dose_pairing':paired(stages['train_checkpoint4']['rows'],new['rows']),
            'held_pairing':paired(stages['held_base']['rows'],stages['held_checkpoint32']['rows']),
            'held_gate_open':gate_open,'interpretation':decision,'integrity_errors':issues,'source_sha256':dict(SOURCE_SHA256),
            'limits':['Generated code is parsed as text/AST only; no exec/eval, model call or GPU.',
                      'Exact teacher AST plus saved clean execution and raw exact is narrower evidence than arbitrary program correctness; pattern flags need review.',
                      'Train checkpoint4/32 comparisons require identical coordinates, seeds and physical initial token prefixes. No unmatched base regression claim.',
                      'Held comparison is only genuine fixed final32 versus its matched base,16 contexts x2 repeats; not32 independent contexts.',
                      'Availability uses the previously checked observer taxonomy conditional on collector causal mapping; raw finals and initial prefixes independently checked.',
                      'Checkpoint32 full adapter/Adam/RNG qualification is reused from the evaluator receipt, not rehashed or replayed here.',
                      'Teacher loss and collected gradient metrics are not independent backprop verification. No checkpoint selection or feedback into training.']}


def markdown(report):
    lines = ['# Fixed procedural-SFT dose: checkpoint4 versus checkpoint32','',report['interpretation'],'',
             '| Stage | Raw exact / available / planned | First teacher AST | Schema-error episodes | Dump episodes |',
             '| --- | ---: | ---: | ---: | ---: |']
    for name,stage in report['stages'].items():
        s=stage['summary']; lines.append(f"| {name} ({stage['status']}) | {s['raw_exact']} / {s['available']} / {s['planned']} | {s.get('first_teacher_ast_exact',0)} | {s.get('episodes_with_actual_schema_error',0)} | {s.get('episodes_with_broad_dump',0)} |")
    pair=report['train_dose_pairing']; held=report['held_pairing']
    lines += ['',f"Matched train dose comparison: {pair['paired_available']} available pairs; checkpoint32 wins/losses {pair['wins_right']}/{pair['losses_right']}; {pair['first_actions_equal']}/{pair['matched_coordinates']} first actions unchanged.",
              f"Fixed held gate open: {report['held_gate_open']}. Genuine held base/checkpoint32: {held['paired_available']} available pairs, wins/losses {held['wins_right']}/{held['losses_right']}. Missing held results are not transfer failures.",
              '', '## Teacher-forced fit versus execution', '']
    train = report['stages']['train_checkpoint32']['summary']
    if report['stages']['train_checkpoint32']['status']=='TERMINAL_SNAPSHOT':
        lines.append(f"Checkpoint32 clean correct target observations: {train['clean_correct_target_observed']}; correct print followed by an available nonempty wrong final: {train['correct_print_then_wrong_final_available']}; clean wrong-record prints: {train['clean_wrong_record_printed']}. These distinguish selector evidence from the final-copy boundary; broad dumps do not count as clean retrieval prints.")
    for label,value in report['training'].items():
        if not isinstance(value,dict): continue
        metrics=value.get('metrics') or []
        lines.append(f"- {label}: {value['status']}" + (f"; pre-update action CE {metrics[0]['action_objective']:.6f} → {metrics[-1]['action_objective']:.6f}." if metrics else '.'))
    lines += ['', 'Lower teacher loss alone is not procedure acquisition. Inspect exact teacher-AST clean successes separately from other role/ordinal candidates and broad dump/copy outcomes. Train fit is teacher-exposed; any transfer statement must use the actual final32 held pair. No unmatched baseline supports a regression claim.',
              '',f"Integrity findings: {len(report['integrity_errors'])}. Full evidence and fixed source hashes are in REPORT.json.",'',*('- '+v for v in report['limits']), '']
    return '\n'.join(lines)


def verify_ready():
    ready = read(READY)
    if ready['identity'] != digest({k:v for k,v in ready.items() if k!='identity'}):
        raise ValueError('analyzer READY identity differs')
    for raw,expected in ready['closure_sha256'].items():
        if hashlib.sha256(Path(raw).read_bytes()).hexdigest() != expected:
            raise ValueError('analyzer fixed input/source changed: '+raw)
    return ready


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'));parser.add_argument('--output',type=Path)
    args=parser.parse_args(); ready=verify_ready()
    if args.command=='verify': print(json.dumps({'identity':ready['identity']}))
    else:
        if args.output is None or args.output.resolve().parent != ROOT or args.output.exists():
            raise ValueError('supply a new direct child output directory beneath this analyzer')
        report=build_report();report['analyzer_ready_identity']=ready['identity']
        report['analyzer_ready_sha256']=hashlib.sha256(READY.read_bytes()).hexdigest()
        report['source_sha256'].update(ready['closure_sha256'])
        args.output.mkdir()
        for name,value in [('REPORT.json',json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n'),('REPORT.md',markdown(report))]:
            with (args.output/name).open('x') as stream: stream.write(value)
        print(json.dumps({'output':str(args.output),'interpretation':report['interpretation'],'integrity_errors':len(report['integrity_errors'])}))
