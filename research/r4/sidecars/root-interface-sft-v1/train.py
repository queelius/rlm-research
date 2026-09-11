"""Exactly four authored root SFT updates; historical weights but explicitly fresh Adam."""
import argparse
import importlib.metadata
import math
import os
import random
import sys
import time
from pathlib import Path
import study as s
leaf=s.ROOT.parent/'trec-leaf-sft-v1/source'
data=s.load('data',leaf/'data.py','b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f')
old=s.load('interface_pinned_checkpoint',leaf/'experiment.py','c4a66731f544c57821b8f0bf81eb6f5785f12f943b61b8bc4e3916a1dcef041c')

def update(model,optimizer,rows,device,deadline=None):
    import torch
    params=[p for p in model.parameters() if p.requires_grad]
    denominator=sum(sum(v!=-100 for v in r['labels'][1:]) for r in rows)
    if denominator<=0:raise ValueError('zero supervised tokens')
    optimizer.zero_grad(set_to_none=True);total=0.
    for row in rows:
        if deadline is not None and time.monotonic()>deadline:raise TimeoutError('600s accumulated training cap')
        batch={k:v.to(device) for k,v in data.collate([row],0).items()}
        result=model(input_ids=batch['input_ids'],attention_mask=batch['attention_mask'],use_cache=False)
        loss,count=old.loss_sum(result.logits,batch['labels'])
        if not torch.isfinite(loss):raise ValueError('nonfinite SFT loss')
        (loss/denominator).backward();total+=float(loss.detach())
    norm=torch.nn.utils.clip_grad_norm_(params,1.)
    if not torch.isfinite(norm):raise ValueError('nonfinite gradient')
    if deadline is not None and time.monotonic()>deadline:raise TimeoutError('training cap before update')
    optimizer.step()
    return dict(nll=total/denominator,target_tokens=denominator,gradient_norm=float(norm))

def verify():
    ready=s.read(s.ROOT/'READY.json')
    for path,expected in ready['source_sha256'].items():s.check(path,expected)
    recipe=s.read(s.ROOT/'RECIPE.json');prepared=Path(recipe['prepared'])
    for path,expected in recipe['input_sha256'].items():s.check(path,expected)
    for name,expected in recipe['starting_files_sha256'].items():s.check(s.START/name,expected)
    rows=s.read(prepared/'TRAINING_ROWS_FINAL.json')
    if len(rows)!=32:raise ValueError('32 authored rows required')
    for r in rows:
        k=r['prompt_length']
        if r['labels']!=[-100]*k+r['input_ids'][k:] or r['input_ids'][-1]!=151645 or len(r['input_ids'])>8192:raise ValueError('current action mask/terminator changed')
    return recipe,rows,ready['identity']

def run(output):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM
    started=time.monotonic();recipe,rows,identity=verify()
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or not torch.cuda.is_available() or torch.cuda.device_count()!=1:raise ValueError('parent assigns one free GPU')
    output.mkdir(parents=True,exist_ok=False)
    manifest=s.read(s.BASE/'local-research-manifest.json')
    for filename,expected in manifest['files'].items():s.check(s.BASE/filename,expected)
    random.seed(981284002);torch.manual_seed(981284002);torch.cuda.manual_seed_all(981284002)
    base=AutoModelForCausalLM.from_pretrained(s.BASE,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'})
    model=PeftModel.from_pretrained(base,s.START,is_trainable=True,autocast_adapter_dtype=True)
    audit=old.audit(model,s.START);s.write(output/'LOAD_AUDIT.json',audit)
    params=[p for p in model.parameters() if p.requires_grad]
    if not all(p.dtype==torch.float32 for p in params):raise ValueError('FP32 adapter required')
    if any(p.requires_grad for name,p in model.named_parameters() if 'lora_' not in name):raise ValueError('base unexpectedly trainable')
    for config in model.peft_config.values():
        if config.lora_dropout!=0:raise ValueError('dropout must be zero')
    initial=[p.detach().cpu().clone() for p in params]
    optimizer=torch.optim.AdamW(params,lr=1e-4,weight_decay=0.)
    assert not optimizer.state
    model.train();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    train_started=time.monotonic();deadline=train_started+600;metrics=[];step=0
    for epoch in range(2):
        order=list(range(32));random.Random(981284002+epoch).shuffle(order)
        for offset in (0,16):
            metric=update(model,optimizer,[rows[i] for i in order[offset:offset+16]],'cuda:0',deadline)
            step+=1;next_epoch,next_cursor=(epoch,16) if offset==0 else (epoch+1,0)
            delta=math.sqrt(sum(float((p.detach().cpu()-v).square().sum()) for p,v in zip(params,initial)))
            if not math.isfinite(delta) or delta<=0:raise ValueError('invalid/no adapter delta')
            metric.update(step=step,epoch=epoch+1,example_ids=[rows[i]['id'] for i in order[offset:offset+16]],delta_l2_from_start=delta,elapsed_training_seconds=time.monotonic()-train_started)
            path=old.save_checkpoint(model,optimizer,output,dict(identity=identity,epoch=next_epoch,cursor=next_cursor,step=step,metric=metric,optimizer_origin='fresh Adam; historical optimizer/RNG not restored'))
            metric['checkpoint']=str(path);s.write(output/f'STEP-{step}.json',metric);metrics.append(metric)
            print(s.read(output/f'STEP-{step}.json'),flush=True)
    state=old.checkpoint_state(path,identity,[32,32])
    selected=dict(rule='fixed final update4, epoch2; no validation selection',checkpoint=str(path),step=4,adapter_sha256=s.sha(path/'adapter_model.safetensors'),config_sha256=s.sha(path/'adapter_config.json'),state_sha256=s.sha(path/'state.json'))
    s.write(output/'SELECTION.json',selected)
    result=dict(identity=identity,complete=True,selected=selected,steps=metrics,training_seconds=time.monotonic()-train_started,total_seconds=time.monotonic()-started,record_exposures=64,target_token_exposures=sum(r['target_tokens'] for r in metrics),starting_adapter_sha256=s.START_SHA,fresh_optimizer=True,child_loaded=False,child_updated=False,base_dtype='bfloat16',adapter_dtype='float32',peak_memory_allocated=torch.cuda.max_memory_allocated(),versions={k:importlib.metadata.version(k) for k in ('torch','transformers','peft')},files_sha256=state['files_sha256'])
    s.write(output/'RESULT.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--output',type=Path,default=s.ROOT/'outputs/attempt-001/training');a=p.parse_args()
    print({'verified':verify()[2]} if a.command=='verify' else run(a.output))
