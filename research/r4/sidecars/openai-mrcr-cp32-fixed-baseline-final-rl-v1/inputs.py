"""Recompute the complete source audit and retain only actual native final actions for loss."""
import os
from pathlib import Path
import sys
import study

def qualified_source():
    old={n:sys.modules.get(n) for n in ('study','checkpoint','collect')};paths=list(sys.path)
    sys.modules['study']=study.load('fixedbaseline_raw_g4_study',study.SCREEN/'study.py')
    for name in ('checkpoint','collect'):sys.modules.pop(name,None)
    try:
        audit=study.load('fixedbaseline_source_g4_audit',study.REVIEW/'analyze.py');audit.verify();report=audit.build()
        collector=audit.bindings()
        return report,collector.checkpoint.verify_checkpoint(),collector.checkpoint.binding('checkpoint32')
    finally:
        sys.path[:]=paths
        for n,v in old.items():
            if v is None:sys.modules.pop(n,None)
            else:sys.modules[n]=v

def build():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.INPUTS.exists()
    report,cp,binding=qualified_source()
    assert report['owner_qualified'] and report['available']==32 and report['complete_groups']==8
    assert report['raw_exact_available']==28 and report['mixed_groups']==0
    study.write_x(study.ROOT/'PARENT_CHECKPOINT_QUALIFICATION.json',cp)
    assert binding['models'][binding['role_map']['root']]['adapter_sha256']==study.ADAPTER_SHA
    study.write_x(study.ROOT/'PARENT_BINDING.json',binding)
    native={r['index']:(p,r) for p in sorted((study.SOURCE_OUTPUT/'science/native-calls').glob('*-result.json')) if (r:=study.read(p))['status']=='returned'}
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(study.BASE),local_files_only=True)
    rows=[];pins=dict(report['source_sha256'])
    for group in report['groups']:
        for sample in group['samples']:
            assert sample['available'] and sample['actual_final_text'] and sample['clean_target_stdout']
            assert sample['first_teacher_AST_exact'] and len(sample['turns'])==2 and sample['child_actions']==0
            turns=[]
            for i,info in enumerate(sample['turns']):
                path,r=native[info['native_index']];pins[str(path)]=study.sha(path)
                assert r['model']==binding['role_map']['root']
                sam=r['sampling'];assert sam['seed']==sample['coordinate']['seed'] and sam['temperature']==.5 and sam['top_p']==1
                assert sam['max_tokens']==2048 and sam['extra_body']['top_k']==-1 and sam['extra_body']['min_p']==0
                tokens=r['response']['tokens'];prompt=tokens['prompt_ids'];action=tokens['completion_ids'];full=prompt+action
                assert study.digest(prompt)==info['prompt_ids_sha256'] and study.digest(action)==info['action_ids_sha256']
                final=i==1
                if final:assert info['actual_final_text_turn'] and info['bare_semantic_final_span']
                parts=['eos' if t in tok.all_special_ids else 'whitespace' if tok.decode([t]) and not tok.decode([t]).strip() else 'body' for t in action]
                turns.append({'native_result_path':str(path),'native_result_sha256':study.sha(path),'native_index':r['index'],
                    'prompt_ids':prompt,'action_ids':action,'input_ids':full,'old_logprobs':tokens['completion_logprobs'],
                    'labels':[-100]*len(prompt)+action if final else [-100]*len(full),
                    'loss_mask':[0]*len(prompt)+[1]*len(action) if final else [0]*len(full),
                    'diagnostic_token_parts':parts,'depth':0,'credited':final,'sampling':sam})
            rows.append({'episode_id':sample['coordinate']['id'],'group_id':group['record_id'],'coordinate':sample['coordinate'],
                'reward':sample['binary_reward'],'advantage':sample['binary_reward']-.5,'baseline':.5,'available':True,
                'actual_bare_final':True,'root_turns':[turns[1]],'zero_loss_root_turns':[turns[0]],'child_loss_tokens':0})
    data={'schema':'cp32-fixed-baseline-final-native-inputs-v1','episodes':rows,'baseline':.5,'denominator':32,
          'groups':8,'source_reward_variation':'zero within-group RLOO; fixed baseline is a new objective',
          'selected_action_tokens':10420,'unselected_root_action_tokens':6716,'source_sha256':pins,
          'source_g4_ready_sha256':study.sha(study.SCREEN/'CPU_READY_V4.json'),
          'source_report_sha256':study.sha(study.REVIEW/'REPORT-001.json'),'parent_adapter_sha256':study.ADAPTER_SHA,
          'gold_text_in_training_targets':False,'targets_are_unchanged_sampled_native_tokens':True}
    study.validate_inputs(data);study.write_x(study.INPUTS,data)
    return data

if __name__=='__main__':print({'episodes':len(build()['episodes'])})
