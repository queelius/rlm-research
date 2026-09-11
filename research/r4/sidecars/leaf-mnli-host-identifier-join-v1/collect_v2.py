"""Qualified checkpointed collector bound to the additive six-arm inputs."""
import argparse,asyncio,sys,types
from pathlib import Path
import owner_v2 as owner,protocol_v2 as p,scoring_v2 as scoring,study as s

path=s.SOURCE/'collect.py';pin='53c9f05634aa0dc60731e96325c3f969fae8257ba63beafe57bd9c738c224b7d'
if s.sha(path)!=pin:raise ValueError('exact collector changed')
source=path.read_text();changes=(("s.ROOT/'PLAN.json'","s.ROOT/'PLAN_v2.json'"),("s.ROOT/'REQUESTS.json'","s.ROOT/'REQUESTS_v2.json'"),("s.ROOT/'ORDERED_REQUESTS.json'","s.ROOT/'ORDERED_REQUESTS_v2.json'"),("s.ROOT/'PROMPT_IDS.json'","s.ROOT/'PROMPT_IDS_v2.json'"),("s.ROOT/'CPU_NATIVE.json'","s.ROOT/'CPU_NATIVE_v2.json'"),("status=dict(planned=32,recorded=len(rows)","status=dict(planned=48,recorded=len(rows)"),("inventory_complete=len(rows)==32","inventory_complete=len(rows)==48"))
for old,new in changes:
    if source.count(old)!=1:raise ValueError('collector seam changed: '+old)
    source=source.replace(old,new)
module=types.ModuleType('visible_reference_collector_v2');module.__file__=str(path);sys.modules[module.__name__]=module
with s.aliases({'study':s,'protocol':p,'scoring':scoring}):exec(compile(source,str(path)+'::visible-reference48-v2','exec'),module.__dict__)
def summarize(rows):
    def group(values):
        available=[r for r in values if r['score']['available']];null=[r for r in values if not r['score']['available']];correct=sum(r['score']['strict_correct'] for r in available)
        return dict(planned=len(values),available=len(available),null=len(null),strict_correct=correct,strict_bounds=[correct,correct+48*len(null)],contract_valid=sum(bool(r['score']['contract_valid']) for r in available),shape_valid=sum(bool(r['score']['shape_valid']) for r in available),requested_tag_matches=sum(r['score']['tag_position_matches'] or 0 for r in available),named_correct_disagree=sum(r['score']['named_correct_disagree'] or 0 for r in available),named_disagree_items=sum(r['score']['named_disagree_items'] or 0 for r in available),third_correct_disagree=sum(r['score']['third_correct_disagree'] or 0 for r in available))
    costs=[r for r in rows if r.get('physical_attempt')];known=[r for r in costs if r.get('usage_observed')]
    return dict(arms={arm:group([r for r in rows if r['coordinate']['arm']==arm]) for arm in p.ARMS},costs=dict(physical_requests=len(costs),requests_with_usage=len(known),unknown_usage=len(costs)-len(known),prompt_tokens=sum(r['usage_observed']['prompt_tokens'] for r in known),completion_tokens=sum(r['usage_observed']['completion_tokens'] for r in known),provider_billing='unknown/not measured'),cluster_unit='8 exposed paired contexts; no label/seed independence')
module.summarize=summarize;run=module.run
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('run',));ap.add_argument('--endpoint',required=True);ap.add_argument('--output',required=True);ap.add_argument('--deadline',required=True,type=float);a=ap.parse_args()
    owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect_v2.py'),'run','--endpoint',a.endpoint,'--output',a.output,'--deadline',str(a.deadline)])
    print(asyncio.run(run(Path(a.endpoint),Path(a.output),a.deadline)))
