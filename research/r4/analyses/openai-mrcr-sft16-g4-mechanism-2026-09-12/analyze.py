"""Thin cp16 binding of the reviewed G4 scorer plus paired cp32 diagnostics."""
import argparse
import importlib.util
import os
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1]
PRIOR=STORE/'analyses/openai-mrcr-sft32-g4-mechanism-2026-09-12'
spec=importlib.util.spec_from_file_location('cp16_reviewed_g4_core',PRIOR/'analyze.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
core.ROOT=ROOT;core.SIDE=STORE/'sidecars/openai-mrcr-procedural-sft16-onpolicy-screen-v1'
BASELINE=PRIOR/'REPORT-001.json'
BASELINE_SHA='6539a13739262e4fc5be4714c43bed2e41265aa1457f7d975807d60497bd37a4'

def pair_sample(old,new):
    for key in ('record_id','repeat','seed','temperature'):
        assert old['coordinate'][key]==new['coordinate'][key],key
    both=old['available'] and new['available']
    a=old['turns'][0] if old['turns'] else None;b=new['turns'][0] if new['turns'] else None
    return {'record_id':new['coordinate']['record_id'],'repeat':new['coordinate']['repeat'],
            'seed':new['coordinate']['seed'],'both_available':both,
            'cp32_available':old['available'],'cp16_available':new['available'],
            'cp32_reward':old['binary_reward'],'cp16_reward':new['binary_reward'],
            'cp16_win':bool(both and new['binary_reward']>old['binary_reward']),
            'cp16_loss':bool(both and new['binary_reward']<old['binary_reward']),
            'returned_answer_changed':bool(both and old['returned_final_sha256']!=new['returned_final_sha256']),
            'initial_prompt_equal':bool(a and b and a['prompt_ids_sha256']==b['prompt_ids_sha256']),
            'first_action_equal':bool(a and b and a['action_ids_sha256']==b['action_ids_sha256']),
            'cp32_failure_category':old['failure_category'],'cp16_failure_category':new['failure_category'],
            'cp32_teacher_first_AST':old['first_teacher_AST_exact'],'cp16_teacher_first_AST':new['first_teacher_AST_exact'],
            'cp32_clean_target_stdout':old['clean_target_stdout'],'cp16_clean_target_stdout':new['clean_target_stdout'],
            'cp32_root_actions':old['root_actions'],'cp16_root_actions':new['root_actions']}

def build():
    report=core.build()
    if report['status']=='PENDING':return report
    report['condition']='checkpoint16_temperature0.5'
    assert core.sha(BASELINE)==BASELINE_SHA
    baseline=core.read(BASELINE)
    assert baseline['available']==32 and baseline['raw_exact_available']==28 and baseline['mixed_groups']==0
    old={(s['coordinate']['record_id'],s['coordinate']['repeat']):s for g in baseline['groups'] for s in g['samples']}
    pairs=[pair_sample(old[(s['coordinate']['record_id'],s['coordinate']['repeat'])],s) for g in report['groups'] for s in g['samples']]
    # Full arrays, not a sum-only equality claim, for the algebraic cancellation diagnostic.
    desc=core.read(ROOT/'SOURCE.json')
    native=[core.read(p) for p in sorted((Path(desc['output'])/'science/native-calls').glob('*-result.json'))]
    by_index={r['index']:r for r in native if r['status']=='returned'}
    for g in report['groups']:
        hashes=[core.digest(by_index[s['turns'][0]['native_index']]['response']['tokens']['completion_logprobs'])
                for s in g['samples'] if s['turns']]
        g['first_turn_native_logps_identical']=len(hashes)==4 and len(set(hashes))==1
        g['identical_first_action_token_TIS_cancellation_candidate']=bool(g['complete_group'] and g['same_first_native_path'] and g['first_turn_native_logps_identical'])
    report['paired_cp32']={'planned_pairs':32,'context_units':8,'recorded_pairs':len(pairs),
        'both_available':sum(p['both_available'] for p in pairs),'cp16_wins':sum(p['cp16_win'] for p in pairs),
        'cp16_losses':sum(p['cp16_loss'] for p in pairs),'changed_answers_available':sum(p['returned_answer_changed'] for p in pairs),
        'all_recorded_initial_prompts_equal':all(p['initial_prompt_equal'] for p in pairs),
        'first_actions_unchanged':sum(p['first_action_equal'] for p in pairs),'pairs':pairs,
        'baseline_report_sha256':BASELINE_SHA,'cp32_physical':baseline['physical'],
        'cp32_owner_seconds':baseline['owner']['elapsed_seconds'],
        'cross_service_and_cache_history_caveat':True,'missing_pairs_not_imputed_wrong':True}
    report['limits'] += ['cp16 was chosen adaptively after cp32 collapse but before any cp16 outcome; original training primary remains32.',
        'Identical initial actions with identical native logps cancel their token-TIS RLOO gradient within a complete group; no distinct-mask benefit is assumed.',
        'This readout does not compute HF gradients, entropy, behavior-policy qualification or optimizer updates.']
    report['source_sha256']=dict(core.PINS)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','check']);p.add_argument('--output',type=Path);a=p.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';ready=core.verify()
    if a.command=='verify':print({'identity':ready['identity']})
    else:
        report=build();report['analyzer_READY_sha256']=core.sha(ROOT/'READY.json');report['created_epoch']=time.time()
        if a.output:core.write(a.output,report)
        print({k:v for k,v in report.items() if k in ('status','complete_groups','mixed_groups','raw_exact_available','decision_proposal_not_training_admission')})

