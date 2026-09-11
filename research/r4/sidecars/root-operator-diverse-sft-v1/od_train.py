"""Six fixed full72 updates; unchanged qualified current-action numerical objective."""
import argparse
import math
import os
from pathlib import Path
import random
import time
import traceback
from types import SimpleNamespace
import od_study as s
import od_learning as l
SEED=981451003

def load_model(output):
    selected=s.starting_policy();j=s.joint()
    view=SimpleNamespace(**{**vars(j),'START':Path(selected['checkpoint']),'START_SHA':selected['adapter_sha256']})
    old=s.load('od_qualified_model_loader',s.JOINT/'train.py','6491520cf407642f9607413621591cb1dd5c6b139f96c90d784880f4f1f6e405',{'joint_study':view,'joint_learning':l})
    old.SEED=SEED
    return old.load_model(output)

def projection(rows):return sum(t['forward_seconds'] for r in rows for t in r['roles'])/6*72*6*3+300

def gate(model,episodes,deadline):
    import torch
    if len(episodes)!=6:raise ValueError('exact predetermined6 gate')
    model.eval();rows=[];started=time.time()
    with torch.no_grad():
        for episode in episodes:
            result=dict(episode_id=episode['episode_id'],roles=[])
            for turn,_ in l.weighted_turns(episode,'joint'):
                if time.time()>=deadline:raise TimeoutError('gate stage cap')
                before=time.time();ce=l.losses(model,turn,'cuda:0');torch.cuda.synchronize()
                row=dict(kind=turn['kind'],target_nll=float(ce.mean()),tokens=len(ce),prefix_tokens=turn['prompt_length'],forward_seconds=time.time()-before)
                if turn['kind']!='terminal':
                    spans=turn['span_indices']
                    if sorted(i for indices in spans.values() for i in indices)!=list(range(len(ce))) or not spans['mechanism'] or spans.get('payload'):raise ValueError('native code/literal partition')
                    for key,indices in spans.items():row[key+'_nll']=float(ce[indices].mean()) if indices else None
                if turn['kind']=='corrective':result['corrective']=row
                result['roles'].append(row);del ce
            rows.append(result)
    objective=l.objective_gate([r['corrective'] for r in rows]);estimate=projection(rows);remaining=deadline-time.time()
    return dict(complete=True,pass_gate=objective['pass'] and estimate<=remaining,objective=objective,cost_pass=estimate<=remaining,
        projected_training_seconds=estimate,remaining_training_stage_seconds=remaining,projection_method='six measured full trajectories /6 x72 x6 x3 plus300 load/checkpoint proxy; estimate not guarantee',
        rows=rows,elapsed_seconds=time.time()-started,gradients_performed=0,optimizer_steps=0,
        mechanism_definition='actual executable code excluding string AND numeric literal token spans; no map payload or gradient-share claim')

def train(model,params,helper,episodes,output,deadline,identity):
    import torch
    if len(episodes)!=72:raise ValueError('complete fixed72 admission')
    start=s.starting_policy();corpus=s.sha(s.ATTEMPT/'capture/CORPUS_READY.json')
    optimizer=torch.optim.AdamW(params,lr=1e-4,weight_decay=0.)
    if optimizer.state:raise ValueError('fresh Adam')
    model.train();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    initial=[p.detach().cpu().clone() for p in params];states=[];started=time.time()
    for index in range(6):
        order=list(range(72));random.Random(SEED+index).shuffle(order)
        metric=l.update(model,optimizer,[episodes[i] for i in order],'joint','cuda:0',deadline)
        delta=math.sqrt(sum(float((p.detach().cpu()-v).square().sum()) for p,v in zip(params,initial)))
        if not math.isfinite(delta) or delta<=0 or {int(v['step']) for v in optimizer.state.values()}!={index+1}:raise ValueError('actual Adam step/delta')
        metric.update(step=index+1,example_order=[episodes[i]['episode_id'] for i in order],delta_l2_from_start=delta)
        previous=s.sha(output/f'checkpoint-{index:04}/state.json') if index else None
        path=helper.old.save_checkpoint(model,optimizer,output,dict(identity=identity,arm='joint',corpus_sha256=corpus,epoch=index+1,cursor=0,step=index+1,metric=metric,previous_state_sha256=previous,starting_adapter_sha256=start['adapter_sha256'],optimizer_origin='fresh at0; complete72 current-action pass',elapsed_training_seconds=time.time()-started))
        states.append(helper.checkpoint_state(path,identity,corpus));print(dict(step=index+1,weighted_ce=metric['weighted_ce'],target_tokens=metric['target_tokens']),flush=True)
    path=output/'checkpoint-0006';selected=dict(rule='fixed final6; no validation selection or partial substitute',checkpoint=str(path),step=6,adapter_sha256=s.sha(path/'adapter_model.safetensors'),config_sha256=s.sha(path/'adapter_config.json'),state_sha256=s.sha(path/'state.json'))
    s.write(output/'SELECTION.json',selected)
    return dict(identity=identity,complete=True,selected=selected,optimizer_steps=6,example_exposures=432,root_turn_exposures=sum(x['metric']['root_turns'] for x in states),target_token_exposures=sum(x['metric']['target_tokens'] for x in states),starting_adapter_sha256=start['adapter_sha256'],corpus_sha256=corpus,fresh_optimizer=True,child_loaded=False,child_updated=False,files_sha256=states[-1]['files_sha256'],elapsed_training_seconds=time.time()-started)

def run(args):
    started=time.time();ready=s.verify();episodes=s.corpus();lookup={x['episode_id']:x for x in episodes}
    args.output.mkdir(parents=True,exist_ok=False)
    s.write(args.output/'RUN.json',dict(identity=ready['identity'],seed=SEED,learning_rate=1e-4,weight_decay=0,gradient_clip=1.,producer_weight=.45,reduction_weight=.50,stop_weight=.05,starting=s.starting_policy(),deadline_epoch=args.deadline,started_epoch=started,mode=args.mode))
    try:
        model,params,helper=load_model(args.output)
        gate_rows=[lookup[r['id']] for r in s.read(s.ROOT/'inputs/GATE_PLAN.json')]
        result=gate(model,gate_rows,args.deadline);s.write(args.output/'GATE.json',result)
        if args.mode=='gate':s.write(args.output/'RESULT.json',result);return
        if not result['pass_gate']:raise ValueError('fixed objective/cost gate stop, no gradients')
        result=train(model,params,helper,episodes,args.output,args.deadline,ready['identity'])
        result['total_elapsed_seconds']=time.time()-started;s.write(args.output/'RESULT.json',result)
    except BaseException as error:
        s.write(args.output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),elapsed_seconds=time.time()-started));raise

def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('gate','train'),default='train');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);return ap.parse_args(argv)
if __name__=='__main__':run(parse_args())
