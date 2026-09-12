"""Authenticate all 32 native trajectories; never turn unavailable finals into zero reward."""
import os
import study

def build():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.INPUTS.exists()
    assert study.sha(study.REVIEW/'REPORT.json')==study.REPORT_SHA
    report=study.read(study.REVIEW/'REPORT.json')
    assert report['owner']['complete'] and report['owner']['released']
    assert report['available']==32 and report['raw_exact']==7 and report['mixed_groups']==3
    audit=study.load('fresh8rloo_source_audit',study.REVIEW/'analyze.py');c=audit.bindings();s=c.study
    c.verify_ready();cp=c.checkpoint.verify_checkpoint();binding=c.checkpoint.binding('checkpoint32')
    assert binding==study.read(study.SOURCE_OUTPUT/'owned-service/BINDING.json')
    assert binding['models'][binding['role_map']['root']]['adapter_sha256']==study.ADAPTER_SHA
    study.write_x(study.ROOT/'PARENT_CHECKPOINT_QUALIFICATION.json',cp)
    study.write_x(study.ROOT/'PARENT_BINDING.json',binding)
    assert study.read(study.SOURCE_OUTPUT/'science/TERMINAL_STRIP_CONTRACT.json')==c.hooks.qualify()
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    tok=AutoTokenizer.from_pretrained(str(study.BASE),local_files_only=True);renderer=Qwen3Renderer(tok)
    gold=study.read(s.input_dir('train')/'HOST_GOLD.json');prefix=study.read(s.input_dir('train')/'PREFIXES.json')
    plan={r['id']:r for r in s.schedule('train')}
    native={r['index']:(p,r) for p in sorted((study.SOURCE_OUTPUT/'science/native-calls').glob('*-result.json')) if (r:=study.read(p))['status']=='returned'}
    assert len(native)==66
    rows=[];pins=dict(report['source_sha256']);pins[str(study.REVIEW/'REPORT.json')]=study.REPORT_SHA
    for group in report['groups']:
        total=sum(v['binary_reward'] for v in group['samples'])
        for sample in group['samples']:
            path=sample['episode_path'];item=study.read(path);assert item['coordinate']==plan[sample['coordinate']['id']]
            checked=audit.core.episode(item,[v[1] for v in native.values()],gold[group['record_id']],
                prefix[sample['coordinate']['id']]['token_ids'],None,c,tok,renderer)
            for key in ('available','binary_reward','actual_final_text','turns'):
                assert checked[key]==sample[key],key
            assert checked['available'] and checked['child_actions']==0
            advantage=(4*sample['binary_reward']-total)/3
            credited=[];zero=[];pins[path]=study.sha(path)
            for i,info in enumerate(checked['turns']):
                nativepath,r=native[info['native_index']];pins[str(nativepath)]=study.sha(nativepath)
                assert r['model']==binding['role_map']['root']
                sam=r['sampling'];assert sam['seed']==sample['coordinate']['seed']
                assert sam['temperature']==.5 and sam['top_p']==1 and sam['max_tokens']==2048
                assert sam['extra_body']['top_k']==-1 and sam['extra_body']['min_p']==0
                tokens=r['response']['tokens'];prompt=tokens['prompt_ids'];action=tokens['completion_ids'];full=prompt+action
                assert study.digest(prompt)==info['prompt_ids_sha256'] and study.digest(action)==info['action_ids_sha256']
                final=advantage!=0 and i==len(checked['turns'])-1
                if final:
                    assert checked['actual_final_text'] and checked['clean_target_stdout']
                    assert info['actual_final_text_turn'] and info['bare_semantic_final_span']
                parts=['eos' if t in tok.all_special_ids else 'whitespace' if tok.decode([t]) and not tok.decode([t]).strip() else 'body' for t in action]
                turn={'native_result_path':str(nativepath),'native_result_sha256':study.sha(nativepath),'native_index':r['index'],
                    'prompt_ids':prompt,'action_ids':action,'input_ids':full,'old_logprobs':tokens['completion_logprobs'],
                    'labels':[-100]*len(prompt)+action if final else [-100]*len(full),
                    'loss_mask':[0]*len(prompt)+[1]*len(action) if final else [0]*len(full),
                    'diagnostic_token_parts':parts,'depth':0,'credited':final,'sampling':sam}
                (credited if final else zero).append(turn)
            rows.append({'episode_id':sample['coordinate']['id'],'group_id':group['record_id'],'coordinate':sample['coordinate'],
                'reward':sample['binary_reward'],'baseline':total/4,'advantage':advantage,'available':True,
                'actual_bare_final':bool(credited),'source_actual_final_text':checked['actual_final_text'],
                'root_turns':credited,'zero_loss_root_turns':zero,'child_loss_tokens':0})
    data={'schema':'cp32-fresh8-final-rloo-native-inputs-v1','episodes':rows,'denominator':32,'groups':8,
        'selected_action_tokens':sum(len(t['action_ids']) for r in rows for t in r['root_turns']),
        'unselected_root_action_tokens':sum(len(t['action_ids']) for r in rows for t in r['zero_loss_root_turns']),
        'source_sha256':pins,'source_report_sha256':study.REPORT_SHA,
        'parent_adapter_sha256':study.ADAPTER_SHA,'gold_text_in_training_targets':False,
        'targets_are_unchanged_sampled_native_tokens':True,'zero_advantage_trajectories':20,
        'nonzero_final_actions':12,'all_source_native_returns':66,'source_unavailable':0}
    study.validate_inputs(data);study.write_x(study.INPUTS,data);return data

if __name__=='__main__':print({k:v for k,v in build().items() if k not in ('episodes','source_sha256')})
