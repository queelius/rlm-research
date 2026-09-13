"""Seal the bounded trainer and fixed future readout inputs; no model/GPU launch."""
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import sys
import study as s

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not s.READY.exists()
    data=s.read(s.INPUTS);s.validate_inputs(data)
    closure=dict(s.read(s.WIDTH/'READY_RUN.json')['closure_sha256'])
    paths=[s.WIDTH/'READY_RUN.json',s.CONFIG_SOURCE,s.PRIOR/'math_core.py',s.PRIOR/'trainer.py',s.PRIOR/'study.py',s.OLD/'owner.py',
        s.REVIEW/'readout-001.json',s.REVIEW/'REWARD_CONTRAST.json',s.REVIEW/'reward_contrast.py',
        s.PYTHON,s.PYTHON.parent.parent/'pyvenv.cfg']
    import peft.mapping_func,peft.tuners.lora.layer,torch.optim.adamw,torch.utils.checkpoint
    import transformers.models.qwen3.modeling_qwen3
    for module in (peft.mapping_func,peft.tuners.lora.layer,torch.optim.AdamW,torch.utils.checkpoint,transformers.models.qwen3.modeling_qwen3):
        paths.append(Path(inspect.getfile(module)))
    paths+=list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+list(s.ROOT.glob('*.json'))
    paths+=list((s.ROOT/'cpu-fixture-002').rglob('*.pt'))
    for p in paths:closure[str(p)]=s.sha(p)
    closure.update(data['source_pins'])
    for p,h in closure.items():assert s.sha(p)==h,p
    ready=dict(schema='b05-flat-selection-BA18-ready-v1',status='CPU_READY_MAIN_REVIEW_NOT_GPU_ADMITTED',
        start='released base; fresh seeded zero-B LoRA config only',no_SFT_checkpoint_loaded=True,
        init_seed=s.INIT_SEED,learning_rate=1e-4,optimizer_steps=1,groups=9,group_size=2,denominator=18,
        nonzero_actions=8,zero_actions=10,selected_loss_tokens=1845,token_TIS_cap=2.,token_TIS_biased=True,
        science_seconds=900,owner_seconds=1100,external_seconds=1200,
        output=str(s.OUTPUT),argv=[str(s.PYTHON),str(s.ROOT/'owner.py'),'run'],
        expected_fixed_checkpoint=str(s.OUTPUT/'checkpoint-0001'),
        future_evaluation=dict(fresh_base36=True,fresh_cp1_36=True,train18=True,held18=True,total_calls=72,
            tasks_sha256=s.sha(s.ROOT/'EVAL_TASKS.json'),requires_separate_conditional_evaluator_READY=True),
        python=sys.version,packages={n:importlib.metadata.version(n) for n in ('torch','transformers','peft','safetensors')},
        closure_sha256=dict(sorted(closure.items())))
    ready['identity']=s.digest(ready);s.write_x(s.READY,ready)
    import train
    try:train.run(s.OUTPUT,900)
    except RuntimeError as error:assert str(error)=='CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training'
    else:raise AssertionError('CPU guard missing')
    assert not s.OUTPUT.exists()
    receipt=dict(status='PASS',actual_train_preflight_unmocked=True,actual_GPU_guard_reached=True,
        output_absent=True,ready_sha256=s.sha(s.READY),identity=ready['identity'],pins=len(closure),GPU_calls=0)
    s.write_x(s.ROOT/'ENTRY_PROOF.json',receipt);print(json.dumps(receipt))

if __name__=='__main__':main()
