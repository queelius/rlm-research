"""Role-balanced current-turn means; no gradient-share inference from token counts."""
import math
import time
import joint_study as s
old=s.load('joint_immutable_shifted_ce',s.BASE_CORRECTIVE/'learning.py','02599e6d4c49c67e5ffab7a617fc01055cebdb10bcb1eb16e63151d51326936b')
validate_turn,losses=old.validate_turn,old.losses

def weighted_turns(episode,arm):
    producers=[episode['turns']['first_producer']]+[t for t in episode['masked_history_turns'] if t['kind']=='producer_history']
    if arm=='joint':result=[(t,.45/len(producers)) for t in producers]+[(episode['turns']['corrective'],.50),(episode['turns']['terminal'],.05)]
    elif arm=='reduction_stop':result=[(episode['turns']['corrective'],.95),(episode['turns']['terminal'],.05)]
    else:raise ValueError('unknown role allocation')
    for turn,_ in result:validate_turn(turn)
    return result

def objective_gate(rows):
    if len(rows)!=4 or any(not math.isfinite(r[k]) for r in rows for k in ('mechanism_nll','target_nll')):raise ValueError('four fixed finite measurements required')
    active=sum(r['mechanism_nll']>.1 for r in rows)
    return dict(pass_gate=active>=3,mechanism_rows_above_point1=active,**{'pass':active>=3})

def update(model,optimizer,episodes,arm,device,deadline):
    import torch
    optimizer.zero_grad(set_to_none=True);ledger=[]
    for episode in episodes:
        for turn,mass in weighted_turns(episode,arm):
            if time.time()>=deadline:raise TimeoutError('no partial optimizer update')
            ce=losses(model,turn,device);weighted=ce.mean()*mass/len(episodes);weighted.backward()
            ledger.append(dict(episode_id=episode['episode_id'],kind=turn['kind'],target_tokens=len(ce),forward_tokens=len(turn['input_ids']),ce_sum=float(ce.detach().sum()),weighted_ce=float(weighted.detach()),nominal_turn_mass=mass/len(episodes)))
            del ce,weighted
    norm=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.)
    if not torch.isfinite(norm) or norm<=0:raise ValueError('nonfinite/zero gradient')
    if time.time()>=deadline:raise TimeoutError('no partial optimizer update')
    optimizer.step()
    return dict(weighted_ce=sum(x['weighted_ce'] for x in ledger),target_tokens=sum(x['target_tokens'] for x in ledger),forward_tokens=sum(x['forward_tokens'] for x in ledger),root_turns=len(ledger),gradient_norm=float(norm),turn_losses=ledger,terminal_weight=.05,mass_sum=sum(x['nominal_turn_mass'] for x in ledger))
