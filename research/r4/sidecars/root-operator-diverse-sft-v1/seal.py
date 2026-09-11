"""CPU-only immutable closure. Does not create an attempt, service or lock."""
import od_study as s
import od_collect as c

def main():
    s.starting_policy();source={};inherited=[]
    for root in (s.QSR,s.JOINT):
        ready=s.read(root/'READY.json');inherited.append(dict(path=str(root/'READY.json'),sha256=s.sha(root/'READY.json')))
        for path,pin in ready['source_sha256'].items():
            if path in source and source[path]!=pin:raise ValueError('incompatible inherited closure')
            source[path]=pin
        source[str(root/'READY.json')]=s.sha(root/'READY.json')
    for path in s.ROOT.glob('*.py'):source[str(path)]=s.sha(path)
    for name in ('DESIGN.md','PLAN.md','CPU_REPORT.json','ENVIRONMENT_AMENDMENT.json','READY.json'):source[str(s.ROOT/name)]=s.sha(s.ROOT/name)
    for path in (s.ROOT/'pre-acceptance-v1').iterdir():source[str(path)]=s.sha(path)
    inputs={str(path):s.sha(path) for path in (s.ROOT/'inputs').glob('*.json')}
    for name,pin in s.SOURCE_PINS.items():inputs[str(s.QSR/'inputs'/name)]=pin
    start=s.read(s.ROOT/'inputs/START_BINDING.json');selected=s.starting_policy()
    for key in ('lineage_receipt_path','conversion_path','base_manifest_path'):inputs[start[key]]=s.sha(start[key])
    model=s.read(start['lineage_receipt_path'])
    for value in model['models'].values():
        for filename,key in [('adapter_model.safetensors','adapter_sha256'),('adapter_config.json','config_sha256')]:inputs[str(s.ROOT.__class__(value['path'])/filename)]=value[key]
    for path,pin in {**source,**inputs}.items():
        if s.sha(path)!=pin:raise ValueError('closure changed: '+path)
    c.implementation()
    value=dict(schema='operator-diverse-sft-v1-ready',source_sha256=source,input_sha256=inputs,inherited_readies=inherited,
        starting=selected,train_trajectories=72,physical_child_acquisitions=180,authored_root_actions=324,full_corpus_updates=6,planned_endpoints=48,
        fixed_gate_examples=6,outer_seconds=8400,work_seconds=8100,owned_seconds=8280,collector_counted_edits=c.EDIT_COUNTS,
        command=[str(s.NATIVE),str(s.ROOT/'od_owner.py'),'run','--output',str(s.ATTEMPT)],cpu_only_preparation=True,main_acceptance_and_launch_required=True)
    value['identity']=s.digest(value);s.write(s.ROOT/'READY_v2.json',value);s.verify();print(dict(identity=value['identity'],ready_sha256=s.sha(s.ROOT/'READY_v2.json'),source_pins=len(source),input_pins=len(inputs)))
if __name__=='__main__':main()
