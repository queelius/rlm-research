"""CPU causal-shift, tokenizer-boundary and teacher-history regressions."""
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace
import pytest
import torch
from transformers import GPT2Config, GPT2LMHeadModel

def module():
    path=Path(__file__).parent/'replay.py'
    assert path.exists(),'replay implementation absent'
    loader=importlib.util.spec_from_file_location('local_cue_replay_fixture',path)
    value=importlib.util.module_from_spec(loader);loader.loader.exec_module(value);return value

def test_scores_causal_preceding_logits_only_in_eval_without_gradients():
    r=module();torch.manual_seed(123)
    model=GPT2LMHeadModel(GPT2Config(vocab_size=16,n_positions=32,n_embd=8,n_layer=1,n_head=1,
        resid_pdrop=.7,embd_pdrop=.7,attn_pdrop=.7));model.train()
    original={k:v.detach().clone() for k,v in model.state_dict().items()}
    got=r.score_candidate(model,[1,2,3,4,5],3,'cpu')
    with torch.inference_mode():logits=model(torch.tensor([[1,2,3,4,5]]),use_cache=False).logits.float()
    want=[torch.log_softmax(logits[0,2],-1)[4].item(),torch.log_softmax(logits[0,3],-1)[5].item()]
    assert got['token_logprobs']==pytest.approx(want) and got['sequence_logprob']==pytest.approx(sum(want))
    assert got['predicted_positions']==[3,4] and got['conditioning_positions']==[2,3]
    assert not model.training and all(p.grad is None for p in model.parameters())
    assert all(torch.equal(v,original[k]) for k,v in model.state_dict().items())

def test_shared_prefix_backs_off_merged_boundary_without_scoring_candidate_prefix():
    r=module()
    class Tokenizer:
        def encode(self,text,add_special_tokens=False):return {'X:':[10,11],'X:a!':[10,12,14],'X:b!':[10,13,14]}[text]
    got=r.encode_candidates(Tokenizer(),[1,2],'X:',['a','b'],'!')
    assert got['unmerged_prefix_ids']==[10,11] and got['shared_output_prefix_ids']==[10]
    assert got['backed_off_prefix_tokens']==1 and got['score_start']==3
    assert got['candidates']['a']['input_ids']==[1,2,10,12,14]
    assert got['candidates']['a']['scored_token_ids']==[12,14]
    assert got['candidates']['b']['scored_token_ids']==[13,14]

def test_teacher_history_has_only_prior_gold_and_current_tag():
    r=module();records=[{'id':f'q{i+1000}','gold_label':str(i)} for i in range(64)]
    prefix=r.history_prefix(records,16,'matching')
    assert prefix.endswith('{"tag":"q1015","label":"')
    assert prefix.count('"tag":"p0000"')==15
    changed=[dict(x) for x in records]
    for item in changed[15:]:item['gold_label']='DO_NOT_LEAK'
    assert r.history_prefix(changed,16,'matching')==prefix
    assert r.history_prefix(records,16,'shifted').endswith('{"tag":"q1032","label":"')

def test_rejects_nonfinite_values_and_invalid_scoring_span():
    r=module()
    class Bad(torch.nn.Module):
        def forward(self,input_ids,**kwargs):return SimpleNamespace(logits=torch.full((*input_ids.shape,8),float('nan')))
    with pytest.raises(ValueError):r.score_candidate(Bad(),[1,2,3],2,'cpu')
    for prefix in [0,3,4]:
        with pytest.raises(ValueError):r.score_candidate(Bad(),[1,2,3],prefix,'cpu')
    with pytest.raises(ValueError):r.normalize_scores({'a':float('-inf'),'b':-2})

def test_finite_class_normalization_uses_sum_not_length_mean():
    r=module();got=r.normalize_scores({'a':-3.,'b':-2.})
    assert got['a']==pytest.approx(1/(1+math.e)) and got['b']==pytest.approx(math.e/(1+math.e))
    assert sum(got.values())==pytest.approx(1)

def test_partial_unit_checkpoint_preserves_missing_conditions_at_deadline(tmp_path):
    path=Path(__file__).parent/'run.py';assert path.exists(),'bounded runner absent'
    loader=importlib.util.spec_from_file_location('local_runner_fixture',path)
    runner=importlib.util.module_from_spec(loader);loader.loader.exec_module(runner)
    model=GPT2LMHeadModel(GPT2Config(vocab_size=16,n_positions=32,n_embd=8,n_layer=1,n_head=1))
    unit={'id':'fixture','dataset':'sst2','context_index':0,'position':16,'displayed_gold':'a','named_shifted_gold':'b',
        'conditions':{arm:{'score_start':2,'candidates':{'a':{'input_ids':[1,2,3]},'b':{'input_ids':[1,2,4]}}} for arm in ('matching','constant','shifted')}}
    ticks=iter([0,0,5,5,5]);result=runner.evaluate_units(model,[unit],tmp_path,1,'cpu',lambda:next(ticks,5))
    import json
    saved=json.loads((tmp_path/'units/fixture.json').read_text())
    assert result['stop_reason']=='work_deadline' and not saved['complete']
    assert saved['conditions']['matching']['candidates']['a']['sequence_logprob']<0
    assert saved['conditions']['matching']['normalized_probabilities'] is None
    assert saved['conditions']['constant'] is None and saved['conditions']['shifted'] is None
