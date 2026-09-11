"""Prepare data/protocol only; no policy choice, READY, service or GPU."""
from collections import Counter
import od_study as s
import od_protocol as p

def main():
    source=s.source_inputs();values=p.build(source);n=s.qnative();prompts={}
    public={c['id']:c for c in values['PUBLIC.json']}
    for row in values['TRAIN_PLAN.json']+values['FREE_PLAN.json']:
        task=n.make_task(public[row['context_id']],row['question'],0,row['id']);ids=n.first_prefix(task)
        if len(ids)+2048>8192:raise ValueError('actual initial prefix exceeds reserved context')
        prompts[row['id']]=dict(prompt=task.data.prompt,token_ids=ids,plain_query=row['question'])
    values['PROMPTS_ACCURATE.json']=prompts
    values['NATIVE_TEMPLATE.json']=s.read(s.SIDE/'root-corrective-reduction-sft-v1/inputs/NATIVE_TEMPLATE.json')
    values['HOST_GOLD.json']={k:v for k,v in source['HOST_GOLD.json'].items() if k in public}
    values['PROVENANCE.json']=dict(source_sha256={str(s.QSR/'inputs'/name):pin for name,pin in s.SOURCE_PINS.items()},
        training_groups=192,readout_contexts=[f'readout-{i:02}' for i in range(4,12)],reference_contexts_excluded=[f'readout-{i:02}' for i in range(4)],
        novelty='previous QSR research and child-training exposed; no pristine/root-new claim',starting_binding='pending MAIN; no READY',
        name_template_schedule='label-blind arithmetic on context index and width index only; no operator/scope/target/gold lookup')
    values['COST_PROJECTION.json']=dict(unique_trajectories=72,physical_child_acquisitions=180,authored_root_actions=324,
        fixed_updates=6,trajectory_exposures=432,root_turn_exposures=1944,old_capture_seconds=290.051,linear_capture_seconds=290.051*4.5,
        old_training_core_seconds=182.568,linear_training_core_seconds=182.568*6.75,target_token_exposure_proxy=5016*4.5*6,
        forward_token_exposure_proxy=113096*4.5*6,proxy_not_guarantee=True,capture_stage=1800,gate_train_stage=3600,
        final_stage_each=1200,finalize_stage=300,work=8100,owned=8280,outer=8400)
    table=Counter((r['operator'],r['scope'],r['width'],r['template'],r['layout']) for r in values['TRAIN_PLAN.json'])
    values['ROTATION_COUNTS.json']=[dict(operator=k[0],scope=k[1],width=k[2],template=k[3],layout=k[4],n=v) for k,v in sorted(table.items())]
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    s.write(s.ROOT/'INPUT_PREPARATION.json',dict(complete=True,policy_bound=False,ready_written=False,train=72,free_per_policy=24,gate=6,
        max_first_prefix=max(len(v['token_ids']) for v in prompts.values()),input_sha256={str(s.ROOT/'inputs'/name):s.sha(s.ROOT/'inputs'/name) for name in values}))
    print({'prepared':True,'train':72,'free_per_policy':24,'starting_binding':'pending MAIN','READY':False})

if __name__=='__main__':main()
