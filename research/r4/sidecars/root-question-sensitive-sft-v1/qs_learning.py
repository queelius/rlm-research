"""Unchanged current-action CE; approved finite/cost-only gate, no fit threshold."""
import math
import qs_study as s
old=s.load('qs_qualified_joint_learning',s.JOINT/'joint_learning.py','b5d063afe883d1cbaa49a6b50bfa9d0ca561815fdc2d1617e905724dcb69b4db',{'joint_study':s.joint()})
weighted_turns,losses,validate_turn=old.weighted_turns,old.losses,old.validate_turn
def update(model,optimizer,episodes,arm,device,deadline):
    result=old.update(model,optimizer,episodes,arm,device,deadline)
    params=[p for p in model.parameters() if p.requires_grad]
    if set(optimizer.state)!=set(params):raise ValueError('all trainable parameter moments must be present')
    for p in params:
        state=optimizer.state[p]
        if state['exp_avg'].shape!=p.shape or state['exp_avg_sq'].shape!=p.shape:raise ValueError('Adam moment shape')
    return result
def objective_gate(rows):
    if len(rows)!=6 or any(not math.isfinite(r[k]) for r in rows for k in ('mechanism_nll','target_nll')):raise ValueError('six predetermined finite measurements')
    return {'pass':True,'objective':'validity only; no NLL magnitude/fit threshold','gradients_performed':0}
