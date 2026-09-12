from pathlib import Path
import importlib
import copy
import pytest

ROOT=Path(__file__).resolve().parent

def modules():
    assert (ROOT/'study.py').exists(), 'fixed endpoint evaluator not implemented'
    return tuple(importlib.import_module(n) for n in ('study','checkpoint','collect'))

def test_actual48_payloads_and_model_context_preserve_original_contract():
    s,c,collector=modules()
    for phase,count,original in [('held',32,s.short),('long',16,s.long)]:
        assert s.schedule(phase)==original.schedule(phase)
        assert len(s.schedule(phase))==count
        assert s.input_dir(phase)==original.input_dir(phase)
        assert s.environment_config(phase)==original.environment_config(phase)
        tasks=s.read(s.input_dir(phase)/'tasks.json');prefixes=s.read(s.input_dir(phase)/'PREFIXES.json')
        assert len(tasks)==len(prefixes)==count
        for coord in s.schedule(phase):
            endpoint={'model_alias':s.ADAPTED_ALIAS,'host':'127.0.0.1','port':1,'api_key_env':'FIXTURE_KEY','base_model':{'path':str(s.BASE)}}
            context=collector.source.model_context(endpoint,coord)
            sampling=context.sampling.model_dump(mode='json')
            assert sampling['temperature']==.5 and sampling['seed']==coord['seed'] and sampling['max_tokens']==2048
            assert sampling['extra_body']['top_k']==-1 and sampling['extra_body']['min_p']==0
            assert prefixes[coord['id']]['token_ids']
        native=s.read(sorted((s.BASELINES[phase]/'science/native-calls').glob('*-result.json'))[0])
        assert native['status']=='returned'
        collector.source.validate_native_response(native['response'])
        assert native['response']['tokens']['prompt_ids'] in [v['token_ids'] for v in prefixes.values()]
        broken=copy.deepcopy(native['response']);broken['tokens']['completion_ids'][0]=-1
        with pytest.raises(ValueError):collector.source.validate_native_response(broken)
    assert collector.source.study is s and collector.source.checkpoint is c
    assert collector.source.verify_ready is collector.verify_ready
    suite=s.dependencies();expected=s.SIDE/'runtime-an22-5801-v1/service_wrapper_v2.py'
    assert suite.SERVE==expected and suite.life.ALLOCATION_SERVICE==expected

def test_fixed_step_qualification_rejects_outcome_or_wrong_root_binding():
    s,c,_=modules()
    state={'status':'UPDATED','optimizer_steps':1,'fresh_AdamW':True,'optimizer_state_steps':[1],
        'optimizer_state_empty_before_step':True,'parent_sft_step':32,'groups':8,'trajectories':32,
        'exact_reward_positive':28,'exact_reward_negative':4,'baseline':.5,'denominator':32,
        'actual_final_tokens':10420,'zero_loss_other_root_tokens':6716,'child_loss_tokens':0,
        'replay_passed':True,'replay_actions':32,'learning_rate':1e-5,'token_TIS_cap':2.,
        'token_TIS_biased':True,'mixed_group_gate':False,'adapter_delta_l2':.001,
        'parent_adapter_sha256':s.train.ADAPTER_SHA}
    binding={'role_map':{'root':s.ADAPTED_ALIAS,'children':[s.BASE_ALIAS]},'fixed_child':s.BASE_ALIAS,
        'models':{s.ADAPTED_ALIAS:{'path':str(c.CHECKPOINT),'adapter_sha256':'a','config_sha256':'b'},
                  s.BASE_ALIAS:s.read(s.TRAINING/'PARENT_BINDING.json')['models'][s.BASE_ALIAS]}}
    c.validate_state_binding(state,binding)
    broken=copy.deepcopy(state);broken['optimizer_steps']=0
    with pytest.raises((AssertionError,ValueError)):c.validate_state_binding(broken,binding)
    wrong=copy.deepcopy(binding);wrong['models'][s.ADAPTED_ALIAS]['path']=str(s.train.CHECKPOINT)
    with pytest.raises((AssertionError,ValueError)):c.validate_state_binding(state,wrong)
