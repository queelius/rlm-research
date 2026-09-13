"""Actual tiny scorer path with the repaired V3 namespace."""
import copy, importlib.util
from pathlib import Path
from transformers import Qwen3Config,Qwen3ForCausalLM

def load_study():
    path=Path(__file__).resolve().parents[1]/"b05-vector-credit-local-v3/study.py"
    spec=importlib.util.spec_from_file_location("vector_credit_v3_tiny_study",path);study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study);return study

def test_actual_scorer_logprobs_diagnostics_and_namespace():
    study=load_study();trainer=study.load("vector_credit_v3_tiny_trainer",study.SHARED/"trainer.py");core,_=trainer.dependencies(study)
    names={"BASE","BRANCHES","CAP_SECONDS","DENOMINATOR","INPUTS","NP_SEED","OUTPUT","SEED","TEMPERATURE","TOKEN_TIS_CAP","load_sealed_inputs","positions_and_targets","sha","write_x"}
    assert not names-set(vars(study));assert study.TEMPERATURE==.5
    model=Qwen3ForCausalLM(Qwen3Config(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=8,attention_dropout=0.))
    turn={"prompt_ids":[1,2,3],"action_ids":[4,5],"input_ids":[1,2,3,4,5],"labels":[-100,-100,-100,4,5],"loss_mask":[0,0,0,1,1],"old_logprobs":[-1.,-1.]}
    rows=[{"episode_id":f"tiny-{i}","group_id":"tiny","root_turns":[copy.deepcopy(turn)],"reward":[1,0],"advantage":[.5,-.5]} for i in range(4)]
    baseline=core.scorer._all_logprobs(model,rows)
    for row,values in zip(rows,baseline,strict=True):row["root_turns"][0]["old_logprobs"]=values[0]
    weights,diagnostics=core.scorer._build_token_diagnostics(rows,baseline)
    assert len(weights)==4 and diagnostics["episodes"]==4 and diagnostics["cap"]==2.
    assert diagnostics["episodes_detail"][0]["reward"]==[1,0]
