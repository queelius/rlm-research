"""Exact persisted Adam6→24; unchanged72 objective, no child model or recapture."""
import argparse
import copy
import math
from pathlib import Path
import random
import time
import traceback
import dose_study as s

def validate_saved(saved,names,step):
    import torch
    if len(saved['param_groups'])!=1:raise ValueError('exact one Adam group')
    group=saved['param_groups'][0];ids=group['params']
    if ids!=list(range(len(names))) or set(saved['state'])!=set(ids):raise ValueError('complete ordered saved Adam state')
    if (group['lr'],group['weight_decay'],tuple(group['betas']),group['eps'])!=(1e-4,0.,(.9,.999),1e-8):raise ValueError('saved Adam recipe differs')
    if any(group.get(k,False) for k in ('amsgrad','maximize','capturable','differentiable')):raise ValueError('Adam mode changed')
    for i,row in enumerate(names):
        state=saved['state'][i]
        if set(state)!={'step','exp_avg','exp_avg_sq'} or int(state['step'])!=step:raise ValueError('Adam entries/ordinal')
        for key in ('exp_avg','exp_avg_sq'):
            v=state[key]
            if list(v.shape)!=row['shape'] or v.dtype!=torch.float32 or not torch.isfinite(v).all():raise ValueError('Adam moment shape/dtype/finite')
        if (state['exp_avg_sq']<0).any():raise ValueError('negative second moment')

def restore_state(optimizer,named,saved,names,step):
    import torch
    actual=[dict(name=n,shape=list(p.shape),dtype=str(p.dtype)) for n,p in named]
    if actual!=names or len({n for n,p in named})!=len(names):raise ValueError('live named parameter mapping differs')
    if [id(p) for g in optimizer.param_groups for p in g['params']]!=[id(p) for n,p in named]:raise ValueError('optimizer parameter order differs')
    validate_saved(saved,names,step)
    optimizer.load_state_dict(copy.deepcopy(saved))
    for i,(_,param) in enumerate(named):
        state=optimizer.state[param]
        if int(state['step'])!=step:raise ValueError('restored ordinal')
        for key in ('exp_avg','exp_avg_sq'):
            if not torch.equal(state[key].cpu(),saved['state'][i][key].cpu()):raise ValueError('restored moment changed')
    return dict(restored=True,fresh_optimizer=False,actual_adam_steps=step,parameters=len(names),named_mapping_sha256=s.digest(names),all_moments_exact=True)

def restore_rng(rng,device):
    import torch
    if set(rng)!={'torch','cuda','python'}:raise ValueError('RNG state fields')
    torch.set_rng_state(rng['torch']);random.setstate(rng['python'])
    if str(device).startswith('cuda'):
        if len(rng['cuda'])!=1:raise ValueError('one CUDA RNG state')
        torch.cuda.set_rng_state_all(rng['cuda'])

def checkpoint(path,identity,previous,step):
    import torch
    state=s.read(path/'state.json')
    if (state['identity'],state['corpus_sha256'],state['epoch'],state['cursor'],state['step'],state['previous_state_sha256'])!=(identity,s.CORPUS_SHA,step,0,step,previous):raise ValueError('checkpoint ancestry/cursor')
    if path.name!=f'checkpoint-{step:04d}':raise ValueError('checkpoint directory ordinal')
    required={'adapter_model.safetensors','adapter_config.json','optimizer.pt','rng_state.pt'}
    if not required<=set(state['files_sha256']):raise ValueError('missing checkpoint members')
    for name,pin in state['files_sha256'].items():
        if Path(name).name!=name:raise ValueError('unsafe checkpoint member')
        s.check(path/name,pin)
    names=s.read(s.ROOT/'inputs/PARAMETER_MAP.json')['parameters']
    validate_saved(torch.load(path/'optimizer.pt',map_location='cpu',weights_only=True),names,step)
    return state

def diagnostic(model,episodes,deadline):
    import torch
    model.eval();rows=[];started=time.time();learning=s.learning()
    with torch.no_grad():
        for e in episodes:
            for turn,mass in learning.weighted_turns(e,'joint'):
                if time.time()>=deadline:raise TimeoutError('forward diagnostic cap')
                ce=learning.losses(model,turn,'cuda:0');torch.cuda.synchronize()
                row=dict(episode_id=e['episode_id'],kind=turn['kind'],target_tokens=len(ce),target_nll=float(ce.mean()),nominal_role_mass=mass)
                spans=turn.get('span_indices',{})
                if turn['kind']!='terminal':
                    if sorted(i for values in spans.values() for i in values)!=list(range(len(ce))):raise ValueError('complete source span partition')
                    row['spans']={k:dict(tokens=len(v),nll=float(ce[v].mean()) if v else None) for k,v in spans.items()}
                rows.append(row);del ce
    return dict(rows=rows,gradients=0,post_checkpoint=True,elapsed_seconds=time.time()-started)

def train(args):
    import torch
    ready=s.verify();started=time.time();args.output.mkdir(parents=True,exist_ok=False)
    s.write(args.output/'RUN.json',dict(identity=ready['identity'],start=str(s.START),first_step=7,final_step=24,fresh_optimizer=False,child_loaded=False,deadline_epoch=args.deadline,started_epoch=started))
    try:
        episodes=s.corpus();lookup={e['episode_id']:e for e in episodes}
        probes=[lookup[r['source_episode_id']] for r in s.read(s.ROOT/'inputs/TEACHER_DIAGNOSTIC_PLAN.json')]
        model,params,helper=s.model_loader(args.output)
        names=s.read(s.ROOT/'inputs/PARAMETER_MAP.json')['parameters'];named=[(n,p) for n,p in model.named_parameters() if p.requires_grad]
        if len(names)!=504 or [id(p) for n,p in named]!=[id(p) for p in params]:raise ValueError('exact504 trainable parameter identity')
        saved=torch.load(s.START/'optimizer.pt',map_location='cpu',weights_only=True)
        rng=torch.load(s.START/'rng_state.pt',map_location='cpu',weights_only=True)
        optimizer=torch.optim.AdamW(params,lr=1e-4,weight_decay=0.)
        restored=restore_state(optimizer,named,saved,names,6);del saved
        s.write(args.output/'RESTORED_ADAM.json',restored)
        post6=diagnostic(model,probes,min(args.deadline,time.time()+180));s.write(args.output/'POST6_TEACHER_NLL.json',post6)
        model.train();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        initial=[p.detach().cpu().clone() for p in params]
        # Restore AFTER all model construction and diagnostic/setup, immediately before pass7.
        restore_rng(rng,'cuda:0')
        s.write(args.output/'RNG_RESTORED.json',dict(after_diagnostic=True,before_global_update=7,source_sha256=s.sha(s.START/'rng_state.pt'),torch_equal=torch.equal(torch.get_rng_state(),rng['torch']),cuda_equal=all(torch.equal(a,b) for a,b in zip(torch.cuda.get_rng_state_all(),rng['cuda'])),python_equal=random.getstate()==rng['python']))
        previous=s.sha(s.START/'state.json');states=[];training_started=time.time()
        for index in range(6,24):
            order=list(range(72));random.Random(981451003+index).shuffle(order)
            metric=s.learning().update(model,optimizer,[episodes[i] for i in order],'joint','cuda:0',args.deadline-180)
            if len(optimizer.state)!=504 or {int(v['step']) for v in optimizer.state.values()}!={index+1}:raise ValueError('committed live Adam ordinal')
            delta=math.sqrt(sum(float((p.detach().cpu()-v).square().sum()) for p,v in zip(params,initial)))
            if not math.isfinite(delta) or delta<=0:raise ValueError('finite nonzero adapter change')
            metric.update(step=index+1,example_order=[episodes[i]['episode_id'] for i in order],delta_l2_from_checkpoint6=delta)
            metric['role_nll']={kind:sum(t['weighted_ce'] for t in metric['turn_losses'] if t['kind']==kind)/sum(t['nominal_turn_mass'] for t in metric['turn_losses'] if t['kind']==kind) for kind in {t['kind'] for t in metric['turn_losses']}}
            path=helper.old.save_checkpoint(model,optimizer,args.output,dict(identity=ready['identity'],arm='joint',corpus_sha256=s.CORPUS_SHA,epoch=index+1,cursor=0,step=index+1,metric=metric,previous_state_sha256=previous,starting_adapter_sha256=s.START_SHA,optimizer_origin='persisted exact6; no reset; unchanged72 global passes',named_parameter_mapping_sha256=s.digest(names),elapsed_training_seconds=time.time()-training_started))
            states.append(checkpoint(path,ready['identity'],previous,index+1));previous=s.sha(path/'state.json')
            print(dict(step=index+1,weighted_ce=metric['weighted_ce'],role_nll=metric['role_nll'],elapsed_seconds=time.time()-started),flush=True)
        final=args.output/'checkpoint-0024'
        optimizer_checkpoint_seconds=time.time()-training_started
        selected=dict(rule='fixed24 only; no heldout or partial selection',checkpoint=str(final),step=24,adapter_sha256=s.sha(final/'adapter_model.safetensors'),config_sha256=s.sha(final/'adapter_config.json'),state_sha256=s.sha(final/'state.json'))
        s.write(args.output/'SELECTION.json',selected)
        post24=diagnostic(model,probes,args.deadline);s.write(args.output/'POST24_TEACHER_NLL.json',post24)
        result=dict(identity=ready['identity'],complete=True,selected=selected,added_optimizer_steps=18,actual_final_adam_step=24,example_exposures=1296,root_turn_exposures=sum(x['metric']['root_turns'] for x in states),target_token_exposures=sum(x['metric']['target_tokens'] for x in states),fresh_optimizer=False,child_loaded=False,child_updated=False,elapsed_training_seconds=optimizer_checkpoint_seconds,post6_forward_seconds=post6['elapsed_seconds'],post24_forward_seconds=post24['elapsed_seconds'],elapsed_seconds=time.time()-started,files_sha256=states[-1]['files_sha256'])
        if (result['root_turn_exposures'],result['target_token_exposures'])!=(5832,411246):raise ValueError('unchanged72 exposure invariant')
        s.write(args.output/'RESULT.json',result);return result
    except BaseException as error:
        s.write(args.output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),elapsed_seconds=time.time()-started));raise

def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--deadline',type=float,required=True);return p.parse_args(argv)
if __name__=='__main__':train(parse_args())
