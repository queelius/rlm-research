"""Qualified checkpointed collector bound to 96 frozen inputs."""
import argparse,asyncio,sys,types
from pathlib import Path
import owner,protocol as p,scoring,study as s
path=s.SOURCE/'collect.py';pin='53c9f05634aa0dc60731e96325c3f969fae8257ba63beafe57bd9c738c224b7d'
if s.sha(path)!=pin:raise ValueError('exact collector changed')
source=path.read_text();changes=(("status=dict(planned=32,recorded=len(rows)","status=dict(planned=96,recorded=len(rows)"),("inventory_complete=len(rows)==32","inventory_complete=len(rows)==96"))
for old,new in changes:
    if source.count(old)!=1:raise ValueError('collector seam changed: '+old)
    source=source.replace(old,new)
module=types.ModuleType('field_order_replication_collector');module.__file__=str(path);sys.modules[module.__name__]=module
with s.aliases({'study':s,'protocol':p,'scoring':scoring}):exec(compile(source,str(path)+'::field-order-replication','exec'),module.__dict__)
def summarize(rows):
    def group(values):
        available=[r for r in values if r['score']['available']];null=[r for r in values if not r['score']['available']];correct=sum(r['score']['strict_correct'] for r in available)
        return dict(planned=len(values),available=len(available),null=len(null),strict_correct=correct,strict_bounds=[correct,correct+48*len(null)],contract_valid=sum(bool(r['score']['contract_valid']) for r in available),shape_valid=sum(bool(r['score']['shape_valid']) for r in available),requested_tag_matches=sum(r['score']['tag_position_matches'] or 0 for r in available))
    costs=[r for r in rows if r.get('physical_attempt')];known=[r for r in costs if r.get('usage_observed')]
    return dict(arms={arm:group([r for r in rows if r['coordinate']['arm']==arm]) for arm in p.ARMS},costs=dict(physical_requests=len(costs),requests_with_usage=len(known),unknown_usage=len(costs)-len(known),prompt_tokens=sum(r['usage_observed']['prompt_tokens'] for r in known),completion_tokens=sum(r['usage_observed']['completion_tokens'] for r in known),provider_billing='unknown/not measured'),cluster_unit='16 fresh paired contexts; no label/seed independence')
module.summarize=summarize;run=module.run
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('run',));ap.add_argument('--endpoint',required=True);ap.add_argument('--output',required=True);ap.add_argument('--deadline',required=True,type=float);args=ap.parse_args()
    owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',args.endpoint,'--output',args.output,'--deadline',str(args.deadline)])
    print(asyncio.run(run(Path(args.endpoint),Path(args.output),args.deadline)))
