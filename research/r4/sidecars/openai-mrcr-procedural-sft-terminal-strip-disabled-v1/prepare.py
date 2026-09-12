"""CPU-only additive seal, reusing the fully qualified completed cp32 lineage."""
import json
from functools import lru_cache
import os
from pathlib import Path
import sys
import time

import hooks
import owner
import study


def main():
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('hide CUDA for CPU preparation')
    if study.READY.exists() or owner.OUTPUT.exists():raise FileExistsError('fixed READY/output already exists')
    tested=study.read(study.ROOT/'CPU_TESTS.json')
    if tested['returncode']!=0 or tested['passed']!=6:raise ValueError('six focused regressions must pass')
    old=sys.modules.get('study');sys.modules['study']=study.previous
    try:
        previous_checkpoint=study.load('terminal_strip_qualified_prior_checkpoint',study.PRIOR/'checkpoint.py')
    finally:
        if old is None:sys.modules.pop('study',None)
        else:sys.modules['study']=old
    # Authenticate true resume once in CPU preparation; execution pins the resulting
    # receipt and current committed cp32 bytes without replaying all28 ancestry files.
    previous_checkpoint.verify_checkpoint=lru_cache(maxsize=1)(previous_checkpoint.verify_checkpoint)
    receipt=previous_checkpoint.verify_checkpoint()
    binding=previous_checkpoint.binding('checkpoint32')
    baseline_binding=study.BASELINE/'owned-service/BINDING.json'
    if binding!=study.read(baseline_binding):raise ValueError('baseline binding differs from qualified cp32')
    if not owner.held_gate()['eligible']:raise ValueError('completed train32 gate is not eligible')
    baseline_result=study.read(study.BASELINE/'science/RESULT.json')
    terminal=study.read(study.BASELINE/'OWNER_TERMINAL.json')
    if not terminal['complete'] or not terminal['released'] or baseline_result['raw_exact']!=17 or baseline_result['scientifically_available']!=32:
        raise ValueError('fixed completed held comparator differs')
    schedule=study.schedule('held')
    if len(schedule)!=32 or len({r['record_id'] for r in schedule})!=16 or sorted(r['seed'] for r in schedule)!=list(range(2026091700,2026091732)):
        raise ValueError('fixed held16 x2 seeds differ')
    prefixes=study.read(study.input_dir('held')/'PREFIXES.json')
    natives=[study.read(p) for p in sorted((study.BASELINE/'science/native-calls').glob('*-result.json'))]
    episodes=[study.read(p) for p in sorted((study.BASELINE/'science/episodes').glob('*.json'))]
    if {e['coordinate']['id'] for e in episodes}!={r['id'] for r in schedule}:raise ValueError('baseline coordinates differ')
    for episode in episodes:
        coordinate=episode['coordinate'];trace=episode['episode']['traces'][0]
        if coordinate!=next(r for r in schedule if r['id']==coordinate['id']):raise ValueError('baseline coordinate changed')
        rows=sorted((n for n in natives if n.get('session_id')==trace['id'] and n.get('status')=='returned' and n.get('model')==study.ADAPTED_ALIAS),key=lambda n:n['index'])
        if not rows or rows[0]['response']['tokens']['prompt_ids']!=prefixes[coordinate['id']]['token_ids']:
            raise ValueError('baseline physical initial prefix differs')
    prior_ready_path=study.PRIOR/'CPU_READY.json';prior_ready=study.read(prior_ready_path)
    closure=dict(prior_ready['closure_sha256'])
    paths=list(study.ROOT.glob('*.py'))+[study.ROOT/'CPU_TESTS.json',study.ROOT/'RUNBOOK.md',
        prior_ready_path,previous_checkpoint.RECEIPT,baseline_binding,
        study.BASELINE/'science/RESULT.json',study.BASELINE/'OWNER_TERMINAL.json',
        study.BASELINE/'owned-service/PREFLIGHT.json',study.TRAIN_READOUT/'science/RESULT.json',
        study.TRAIN_READOUT/'OWNER_TERMINAL.json',study.TRAIN_OUTPUT/'RESULT.json',
        study.TRAIN_OUTPUT/'checkpoint-0032/STEP_COMMIT.json']
    for name in study.read(study.TRAIN_OUTPUT/'checkpoint-0032/STEP_COMMIT.json')['files_sha256']:
        paths.append(study.TRAIN_OUTPUT/'checkpoint-0032'/name)
    paths+=list((study.BASELINE/'science/episodes').glob('*.json'))
    paths+=list((study.BASELINE/'science/native-calls').glob('*-result.json'))
    paths+=list((study.ROOT/'cpu-green-002').rglob('*.json'))
    closure.update(hooks.SOURCE_SHA256)
    closure.update({str(p):study.sha(p) for p in paths})
    for raw,want in closure.items():
        if study.sha(Path(raw))!=want:raise ValueError('closure differs at preparation: '+raw)
    ready={'schema':'procedural-sft-terminal-strip-disabled-cpu-ready-v1',
        'status':'CPU_READY_FIXED_CP32_MATCHED_HELD32','created_epoch':time.time(),
        'condition':hooks.qualify(),'checkpoint_receipt_sha256':study.sha(previous_checkpoint.RECEIPT),
        'checkpoint_receipt_identity':receipt['identity'],'baseline_binding_sha256':study.sha(baseline_binding),
        'checkpoint32_commit_sha256':study.sha(study.TRAIN_OUTPUT/'checkpoint-0032/STEP_COMMIT.json'),
        'source_ready_sha256':study.sha(prior_ready_path),'source_ready_identity':prior_ready['identity'],
        'inputs':prior_ready['inputs'],
        'baseline':{'attempt':str(study.BASELINE),'result_sha256':study.sha(study.BASELINE/'science/RESULT.json'),
                    'raw_exact':17,'available':32,'original_primary_unchanged':True,
                    'binding_exact_to_qualified_cp32':True,'all32_initial_physical_prefixes_exact':True},
        'fixed_checkpoint':{'step':32,'selection':False,'true_resume_preparation_verified':True,
                            'receipt_reused_from_completed_evaluation':str(previous_checkpoint.RECEIPT)},
        'comparison':'One new held16 x2 arm against completed same-cp32 same-seed/prompt/prefix/engine-source arm; full token equality remains an empirical post-run check.',
        'sampling':prior_ready['sampling'],'caps':{'science':600,'owner':900,'external':1000},
        'stage_argv':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--stage',owner.STAGE,'--output',str(owner.OUTPUT),'--outer-seconds','900'],
        'held_gate':owner.held_gate(),'optimizer_steps':0,'new_model_calls_in_preparation':0,
        'cpu_fake_provider_calls':8,'generated_code_executed':False,
        'fixture_code':'Only authored print(CPU_TOOL_OK); no generated/retrieval/gold execution.',
        'no_shared_source_edits':True,'source_ancestry_verification':'Full cp4-to32 qualifier once during CPU seal; owner/collector pin receipt and current cp32 commit bytes.',
        'closure_sha256':closure,'launch_authority':'MAIN only after independent focused review'}
    ready['identity']=study.digest(ready);study.write_x(study.READY,ready)
    print(json.dumps({'path':str(study.READY),'sha256':study.sha(study.READY),'identity':ready['identity'],'closure_files':len(closure)},sort_keys=True))


if __name__=='__main__':main()
