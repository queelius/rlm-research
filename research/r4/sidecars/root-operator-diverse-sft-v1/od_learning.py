"""Unchanged qualified numerical objective; fixed six-example practical gate."""
import math
import od_study as s
old=s.load('od_qualified_joint_learning',s.JOINT/'joint_learning.py','b5d063afe883d1cbaa49a6b50bfa9d0ca561815fdc2d1617e905724dcb69b4db',{'joint_study':s.joint()})
weighted_turns,losses,validate_turn,update=old.weighted_turns,old.losses,old.validate_turn,old.update

def objective_gate(rows):
    if len(rows)!=6 or any(not math.isfinite(r[k]) for r in rows for k in ('mechanism_nll','target_nll')):raise ValueError('six fixed finite rows required')
    active=sum(r['mechanism_nll']>.1 for r in rows)
    return {'pass':active>=4,'mechanism_rows_above_point1':active,'threshold':'practical spending gate; not inferential','gradients_performed':0}
