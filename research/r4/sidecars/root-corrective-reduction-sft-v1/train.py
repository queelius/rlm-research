"""Forward-only8 gate or four complete32-example updates; qualified native LoRA checkpointing."""
import argparse
import importlib.metadata
import math
import os
from pathlib import Path
import random
import time
import traceback
import study as s
import learning as l

SEED=981351002

def load_model(output):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM
    helper=s.original.plan.private('train.py',view=s.original.plan.old)
    if not os.environ.get('CUDA_VISIBLE_DEVICES') or not torch.cuda.is_available() or torch.cuda.device_count()!=1:raise ValueError('MAIN must assign exactly one GPU')
    base_path=s.original.prior().BASE;base_manifest=s.read(base_path/'local-research-manifest.json')
    for filename,expected in base_manifest['files'].items():
        if s.sha(base_path/filename)!=expected:raise ValueError('base weights changed')
    random.seed(SEED);torch.manual_seed(SEED);torch.cuda.manual_seed_all(SEED)
    base=AutoModelForCausalLM.from_pretrained(base_path,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda:0'})
    model=PeftModel.from_pretrained(base,s.START,is_trainable=True,autocast_adapter_dtype=True)
    s.write(output/'LOAD_AUDIT.json',helper.old.audit(model,s.START))
    params=[p for p in model.parameters() if p.requires_grad]
    if not params or any(p.dtype!=torch.float32 for p in params) or any(p.requires_grad for n,p in model.named_parameters() if 'lora_' not in n) or any(c.lora_dropout!=0 or c.r!=8 for c in model.peft_config.values()):raise ValueError('rank8 FP32 LoRA only')
    return model,params,helper

def gate(model,episodes,deadline):
    import torch
    if len(episodes)!=8:raise ValueError('fixed first8 gate')
    model.eval();rows=[];started=time.time()
    with torch.no_grad():
        for episode in episodes:
            if time.time()>=deadline:raise TimeoutError('gate cap')
            result={'episode_id':episode['episode_id']}
            for arm in s.ARMS:
                turn=l.selected_turn(episode,arm);before=time.time();ce=l.losses(model,turn,'cuda:0');torch.cuda.synchronize()
                result[arm]=dict(target_nll=float(ce.mean()),tokens=len(ce),prefix_tokens=turn['prompt_length'],forward_seconds=time.time()-before)
                if arm=='corrective':
                    spans=turn['span_indices'];flat=[i for values in spans.values() for i in values]
                    if sorted(flat)!=list(range(len(ce))) or not spans.get('mechanism') or not spans.get('payload'):raise ValueError('complete disjoint native span mask required')
                    for key,indices in spans.items():result[arm][key+'_nll']=float(ce[indices].mean()) if indices else None
                del ce
            terminal=episode['turns']['terminal'];ce=l.losses(model,terminal,'cuda:0')
            result['masked_terminal_diagnostic']=dict(target_nll=float(ce.mean()),tokens=len(ce),training_weight=0.)
            del ce
            rows.append(result)
    decision=l.objective_gate([r['corrective'] for r in rows])
    projection={arm:sum(r[arm]['forward_seconds'] for r in rows)/8*32*4*3 for arm in s.ARMS}
    # Three times measured forward is a transparent planning proxy, not a promised training time.
    cost_pass=max(projection.values())<=600
    return dict(complete=True,pass_gate=decision['pass'] and cost_pass,objective=decision,cost_pass=cost_pass,
        projected_training_seconds_per_arm=projection,projection_method='mean measured first8 forward seconds x32examples x4updates x3 forward/backward factor; startup/checkpoint overhead excluded',
        rows=rows,elapsed_seconds=time.time()-started,gradients_performed=0,optimizer_steps=0,
        mechanism_definition='merge, actual user scope, reduction and print lines; Python string literals excluded into copied_literals, literal map payload separate; boundary tokens other; no gradient contribution claim')

def train(model,params,helper,episodes,arm,output,deadline,identity):
    import torch
    corpus=s.sha(s.ATTEMPT/'capture/CORPUS_READY.json');optimizer=torch.optim.AdamW(params,lr=1e-4,weight_decay=0.)
    if optimizer.state:raise ValueError('fresh Adam required')
    model.train();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    initial=[p.detach().cpu().clone() for p in params];states=[];started=time.time()
    for index in range(4):
        order=list(range(32));random.Random(SEED+index).shuffle(order)
        metric=l.update(model,optimizer,[episodes[i] for i in order],arm,'cuda:0',deadline)
        delta=math.sqrt(sum(float((p.detach().cpu()-v).square().sum()) for p,v in zip(params,initial)))
        if not math.isfinite(delta) or delta<=0 or {int(v['step']) for v in optimizer.state.values()}!={index+1}:raise ValueError('adapter/Adam step')
        metric.update(step=index+1,example_order=[episodes[i]['episode_id'] for i in order],delta_l2_from_start=delta)
        previous=s.sha(output/f'checkpoint-{index:04}/state.json') if index else None
        path=helper.old.save_checkpoint(model,optimizer,output,dict(identity=identity,arm=arm,corpus_sha256=corpus,epoch=index+1,cursor=0,step=index+1,metric=metric,previous_state_sha256=previous,starting_adapter_sha256=s.START_SHA,optimizer_origin='fresh at0; complete32-example current-action passes',elapsed_training_seconds=time.time()-started))
        states.append(helper.checkpoint_state(path,identity,corpus));print({'arm':arm,'step':index+1,'weighted_ce':metric['weighted_ce'],'target_tokens':metric['target_tokens']},flush=True)
    path=output/'checkpoint-0004';selected=dict(rule='fixed final4; no validation selection',checkpoint=str(path),step=4,adapter_sha256=s.sha(path/'adapter_model.safetensors'),config_sha256=s.sha(path/'adapter_config.json'),state_sha256=s.sha(path/'state.json'))
    s.write(output/'SELECTION.json',selected)
    return dict(identity=identity,arm=arm,complete=True,selected=selected,optimizer_steps=4,example_exposures=128,root_turn_exposures=128,target_token_exposures=sum(x['metric']['target_tokens'] for x in states),terminal_weight=0.,starting_adapter_sha256=s.START_SHA,corpus_sha256=corpus,fresh_optimizer=True,child_loaded=False,child_updated=False,files_sha256=states[-1]['files_sha256'],elapsed_training_seconds=time.time()-started)

def run(args):
    started=time.time();ready=s.verify();episodes=s.corpus(8 if args.mode=='gate' else None)
    args.output.mkdir(parents=True,exist_ok=False)
    s.write(args.output/'RUN.json',dict(identity=ready['identity'],mode=args.mode,arm=args.arm,seed=SEED,learning_rate=1e-4,terminal_weight=0.,starting_adapter_sha256=s.START_SHA,deadline_epoch=args.deadline,started_epoch=started))
    try:
        model,params,helper=load_model(args.output)
        result=gate(model,episodes,args.deadline) if args.mode=='gate' else train(model,params,helper,episodes,args.arm,args.output,args.deadline,ready['identity'])
        import torch
        result.update(peak_memory_allocated=torch.cuda.max_memory_allocated(),versions={k:importlib.metadata.version(k) for k in ('torch','transformers','peft')},total_elapsed_seconds=time.time()-started)
        s.write(args.output/'RESULT.json',result)
    except BaseException as error:
        s.write(args.output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),elapsed_seconds=time.time()-started));raise

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('gate','train'),required=True);ap.add_argument('--arm',choices=s.ARMS,default='corrective');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);run(ap.parse_args())
