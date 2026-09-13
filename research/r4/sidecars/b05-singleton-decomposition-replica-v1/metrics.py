"""Reuse exact singleton semantics; only fixed two-arm counts/seeds/cell metadata differ."""
import types
import interface
import study as s
path=s.PRIOR/'metrics.py';assert s.sha(path)=='23982f942d5e3a555e65077b30fd23a4cb8960c99cc369a7afe99f5cf772f7c3'
text=path.read_text()
changes=[("ARMS=('list','vector','singleton')","ARMS=('vector','singleton')",1),
    ("for left,right in [('list','vector'),('list','singleton'),('vector','singleton')]:","for left,right in [('vector','singleton')]:",1),
    ('176','328',5),('context_units=6,stage_seed_units=12,stage_arm_outputs=36','context_units=12,stage_seed_units=24,stage_arm_outputs=48',1),
    ('202609430000','202609500000',1),
    ("row=dict(root_id=root,width=task['width'],repeat=repeat,seed=","row=dict(root_id=root,width=task['width'],history_depth=task['history_depth'],check_revisions=task['check_revisions'],repeat=repeat,seed=",1)]
for before,after,count in changes:
    assert text.count(before)==count,(before,text.count(before));text=text.replace(before,after)
module=types.ModuleType('replica_existing_union_metrics');module.__file__=str(path)
# Initial imports resolve the original vector-metrics dependency; live plan binding is then explicit.
with s.aliases({'study':s.old,'interface':interface},s.PRIOR):exec(compile(text,str(path),'exec'),module.__dict__)
module.s=s
summarize=module.summarize;aggregate=module.aggregate;costs=module.costs
