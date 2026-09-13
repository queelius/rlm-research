"""Reviewed selected-logp/TIS/replay/Adam/RNG math with a fixed non-gold array mask."""
import study
math=study.load('selection_existing_token_math',study.PRIOR/'math_core.py')
with study.aliases({'study':study,'math_core':math},study.PRIOR):
    scorer=study.load('selection_existing_HF_scorer',study.PRIOR/'trainer.py')
selected_logprobs=scorer.selected_logprobs
replay_check=scorer.replay_check
save_rng=scorer.save_rng
restore_rng=scorer.restore_rng

def initialize(base):
    import torch
    from peft import LoraConfig,get_peft_model
    config=LoraConfig.from_json_file(str(study.CONFIG_SOURCE))
    config.update(inference_mode=False,init_lora_weights=True)
    torch.manual_seed(study.INIT_SEED)
    model=get_peft_model(base,LoraConfig(**config))
    for module in model.modules():
        if isinstance(module,torch.nn.Dropout):module.eval()
    trainable={n:p for n,p in model.named_parameters() if p.requires_grad}
    assert trainable and all('.lora_A.' in n or '.lora_B.' in n for n in trainable)
    assert all(torch.count_nonzero(p)==0 for n,p in trainable.items() if '.lora_B.' in n)
    assert all(torch.count_nonzero(p)>0 for n,p in trainable.items() if '.lora_A.' in n)
    return model

def selection_loss(values,weights,advantage,selection):
    assert values.numel()==len(weights)==len(selection)
    active=[i for i,v in enumerate(selection) if v]
    assert active
    return next(iter(math.token_tis_terms([[values[active]]],[[[weights[i] for i in active]]],
                                         [advantage],denominator=study.DENOMINATOR)))
