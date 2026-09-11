"""Authored CE only. No sampled-policy logprob, reward, or admission construction."""
import math
import time

def terminal_row(identity,prefix,target,evidence):
    if not prefix or not target or target[-1]!=151645 or len(prefix)+len(target)>8192:
        raise ValueError('exact native terminal boundary; no truncation')
    return dict(id=identity,kind='terminal',input_ids=prefix+target,labels=[-100]*len(prefix)+target,
                loss_mask=[0]*len(prefix)+[1]*len(target),prompt_length=len(prefix),target_tokens=len(target),
                provenance='operator-authored terminal CE on actual native observation',evidence=evidence)

def update(model,optimizer,episodes,device,deadline=None,terminal_weight=0.):
    import torch
    import torch.nn.functional as F
    if terminal_weight not in (0.,.1) or not episodes or any(len(e['turns'])!=2 for e in episodes):raise ValueError('paired action/terminal corpus')
    optimizer.zero_grad(set_to_none=True);ledger=[];totals={'action':0,'terminal':0};objective=0.;raw_total=0.
    for episode in episodes:
        for kind,turn,weight in zip(('action','terminal'),episode['turns'],(1.,terminal_weight)):
            if weight==0:continue
            if deadline is not None and time.monotonic()>=deadline:raise TimeoutError('no partial optimizer step')
            ids=turn['input_ids'];k=turn['prompt_length'];count=len(ids)-k
            if not 0<k<len(ids)<=8192 or turn['labels']!=[-100]*k+ids[k:] or turn['loss_mask']!=[0]*k+[1]*count:raise ValueError('root suffix only; scaffolding masked')
            if any(key in turn for key in ('old_logprobs','reward','advantage','behavior_logprobs')):raise ValueError('authored corpus cannot carry RL fields')
            x=torch.tensor([ids],device=device);labels=torch.tensor([turn['labels']],device=device)
            logits=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False).logits
            ce=F.cross_entropy(logits[:,:-1].float().reshape(-1,logits.size(-1)),labels[:,1:].reshape(-1),ignore_index=-100,reduction='sum')
            coefficient=ce.new_tensor(weight/(len(episodes)*count));weighted=ce*coefficient
            if not torch.isfinite(weighted):raise ValueError('nonfinite loss')
            weighted.backward();value=float(weighted.detach());raw=float(ce.detach());objective+=value;raw_total+=raw;totals[kind]+=count
            ledger.append(dict(episode_id=episode['episode_id'],turn_id=turn['id'],kind=kind,target_tokens=count,
              coefficient_fp32=float(coefficient),nominal_turn_mass=weight/len(episodes),actual_turn_mass=float(coefficient)*count,ce_sum=raw,weighted_ce=value))
            del logits,ce,weighted,x,labels
    norm=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.)
    if not torch.isfinite(norm) or norm<=0:raise ValueError('nonfinite/zero gradient')
    if deadline is not None and time.monotonic()>=deadline:raise TimeoutError('no partial optimizer step')
    optimizer.step();targets=sum(totals.values())
    return dict(weighted_ce=objective,token_nll=raw_total/targets,target_tokens=targets,
      action_target_tokens=totals['action'],terminal_target_tokens=totals['terminal'],terminal_weight=terminal_weight,
      action_objective=sum(x['weighted_ce'] for x in ledger if x['kind']=='action'),
      terminal_objective_weighted=sum(x['weighted_ce'] for x in ledger if x['kind']=='terminal'),
      episodes=len(episodes),root_turns=len(ledger),gradient_norm=float(norm),mass_sum=sum(x['actual_turn_mass'] for x in ledger),turn_losses=ledger)
