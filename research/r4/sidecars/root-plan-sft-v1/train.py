"""Four full authored-example mean CE passes; fresh optimizer, no RL fields."""
import argparse
import importlib.metadata
import math
import os
import random
import time
import traceback
from pathlib import Path
import study as s

helper=s.private('train.py',view=s.old)
update=helper.update


def corpus(arm):
    rows=s.read(s.ROOT/'prepared-v2'/f'ROWS_{arm}.json')
    if len(rows)!=16 or len({r['id'] for r in rows})!=16 or any(r['arm']!=arm for r in rows):raise ValueError('exact16 authored targets')
    for r in rows:s.validate_authored(r)
    return [dict(episode_id=r['id'],turns=[r]) for r in rows]


def run(arm,output):
    started=time.monotonic();deadline=started+360
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM
    ready=s.verify();episodes=corpus(arm);recipe=s.read(s.ROOT/'RECIPE_V2.json')
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or not torch.cuda.is_available() or torch.cuda.device_count()!=1:raise ValueError('MAIN assigns one GPU')
    output.mkdir(parents=True,exist_ok=False)
    identity=ready['identity'];corpus_sha=s.sha(s.ROOT/'prepared-v2'/f'ROWS_{arm}.json')
    s.write(output/'RUN.json',dict(identity=identity,arm=arm,corpus_sha256=corpus_sha,seed=s.TRAIN_SEED,
      learning_rate=recipe['learning_rate'],fresh_optimizer=True,starting_adapter_sha256=s.START_SHA,started_epoch=time.time()))
    try:
        manifest=s.read(s.prior().BASE/'local-research-manifest.json')
        for filename,expected in manifest['files'].items():s.check(s.prior().BASE/filename,expected)
        random.seed(s.TRAIN_SEED);torch.manual_seed(s.TRAIN_SEED);torch.cuda.manual_seed_all(s.TRAIN_SEED)
        base=AutoModelForCausalLM.from_pretrained(s.prior().BASE,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'})
        model=PeftModel.from_pretrained(base,s.START,is_trainable=True,autocast_adapter_dtype=True)
        s.write(output/'LOAD_AUDIT.json',helper.old.audit(model,s.START))
        params=[p for p in model.parameters() if p.requires_grad]
        if (not params or any(p.dtype!=torch.float32 for p in params) or any(p.requires_grad for n,p in model.named_parameters() if 'lora_' not in n)
            or any(c.lora_dropout!=0 or c.r!=8 for c in model.peft_config.values())):raise ValueError('rank8 FP32 LoRA-only recipe')
        optimizer=torch.optim.AdamW(params,lr=recipe['learning_rate'],weight_decay=0.)
        if optimizer.state:raise ValueError('not fresh Adam')
        model.train();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        initial=[p.detach().cpu().clone() for p in params];states=[]
        for index in range(4):
            order=list(range(16));random.Random(s.TRAIN_SEED+index).shuffle(order)
            metric=update(model,optimizer,[episodes[i] for i in order],'cuda:0',deadline)
            delta=math.sqrt(sum(float((p.detach().cpu()-v).square().sum()) for p,v in zip(params,initial)))
            if not math.isfinite(delta) or delta<=0 or {int(v['step']) for v in optimizer.state.values()}!={index+1}:raise ValueError('adapter/Adam step')
            metric.update(step=index+1,example_order=[episodes[i]['episode_id'] for i in order],delta_l2_from_start=delta)
            previous=s.sha(output/f'checkpoint-{index:04d}/state.json') if index else None
            checkpoint=helper.old.save_checkpoint(model,optimizer,output,dict(identity=identity,arm=arm,corpus_sha256=corpus_sha,
              epoch=index+1,cursor=0,step=index+1,metric=metric,previous_state_sha256=previous,
              optimizer_origin='fresh at campaign0; persisted across four complete passes',elapsed_training_seconds=time.monotonic()-started))
            states.append(helper.checkpoint_state(checkpoint,identity,corpus_sha))
            print({'arm':arm,'step':index+1,'weighted_ce':metric['weighted_ce'],'target_tokens':metric['target_tokens']},flush=True)
        checkpoint=output/'checkpoint-0004'
        selected=dict(rule='fixed final4; no validation selection',checkpoint=str(checkpoint),step=4,
          adapter_sha256=s.sha(checkpoint/'adapter_model.safetensors'),config_sha256=s.sha(checkpoint/'adapter_config.json'),state_sha256=s.sha(checkpoint/'state.json'))
        s.write(output/'SELECTION.json',selected)
        result=dict(identity=identity,arm=arm,complete=True,selected=selected,optimizer_steps=4,example_exposures=64,root_turn_exposures=64,
          target_token_exposures=sum(st['metric']['target_tokens'] for st in states),starting_adapter_sha256=s.START_SHA,
          fresh_optimizer=True,child_loaded=False,child_updated=False,files_sha256=states[-1]['files_sha256'],
          elapsed_training_seconds=time.monotonic()-started,peak_memory_allocated=torch.cuda.max_memory_allocated(),
          versions={k:importlib.metadata.version(k) for k in ('torch','transformers','peft')})
        s.write(output/'RESULT.json',result);return result
    except BaseException as error:
        s.write(output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),elapsed_seconds=time.monotonic()-started));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('run',));p.add_argument('--arm',choices=s.ARMS,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.arm,a.output.resolve())
