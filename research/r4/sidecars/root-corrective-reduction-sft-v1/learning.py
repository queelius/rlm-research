"""Current-action mean CE; copied-literal and mechanism NLL are diagnostics, not gradients."""
import math
import statistics
import time

def validate_turn(turn):
    ids=turn['input_ids'];k=turn['prompt_length'];count=len(ids)-k
    if not 0<k<len(ids)<=8192 or ids[-1]!=151645 or turn['labels']!=[-100]*k+ids[k:] or turn['loss_mask']!=[0]*k+[1]*count:raise ValueError('exact native current-action suffix required')
    if any(key in turn for key in ('old_logprobs','reward','advantage','behavior_logprobs')):raise ValueError('authored CE cannot carry RL fields')
    return count

def selected_turn(episode,arm):
    if arm not in ('corrective','first_producer'):raise ValueError('only selected authored action is trained')
    turn=episode['turns'][arm];validate_turn(turn);return turn

def objective_gate(rows):
    if len(rows)!=8 or any(not math.isfinite(r[k]) for r in rows for k in ('mechanism_nll','target_nll')):raise ValueError('eight fixed finite objective measurements required')
    active=sum(r['mechanism_nll']>=.1 for r in rows);median=statistics.median(r['target_nll'] for r in rows)
    return {'pass':active>=4 and median>=.05,'mechanism_rows_at_least_point1':active,'median_target_nll':median,'floors':'practical spending gate, not inferential threshold'}

def losses(model,turn,device):
    import torch
    import torch.nn.functional as F
    count=validate_turn(turn);x=torch.tensor([turn['input_ids']],device=device)
    logits=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False).logits
    # Keep only target prediction positions, avoiding a full-context FP32 vocabulary copy.
    start=turn['prompt_length']-1
    ce=F.cross_entropy(logits[:,start:-1].float().reshape(-1,logits.size(-1)),x[:,start+1:].reshape(-1),reduction='none')
    if len(ce)!=count or not torch.isfinite(ce).all():raise ValueError('finite shifted current-action loss required')
    return ce

def update(model,optimizer,episodes,arm,device,deadline):
    import torch
    optimizer.zero_grad(set_to_none=True);ledger=[]
    for episode in episodes:
        if time.time()>=deadline:raise TimeoutError('no partial optimizer update')
        turn=selected_turn(episode,arm);ce=losses(model,turn,device);weighted=ce.mean()/len(episodes)
        weighted.backward()
        ledger.append(dict(episode_id=episode['episode_id'],kind=arm,target_tokens=len(ce),ce_sum=float(ce.detach().sum()),weighted_ce=float(weighted.detach()),nominal_turn_mass=1/len(episodes)))
        del ce,weighted
    norm=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.)
    if not torch.isfinite(norm) or norm<=0:raise ValueError('nonfinite/zero gradient')
    if time.time()>=deadline:raise TimeoutError('no partial optimizer update')
    optimizer.step()
    return dict(weighted_ce=sum(x['weighted_ce'] for x in ledger),target_tokens=sum(x['target_tokens'] for x in ledger),root_turns=len(ledger),gradient_norm=float(norm),turn_losses=ledger,terminal_weight=0.,mass_sum=1.)
