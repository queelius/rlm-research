"""Seal the immutable CPU-prepared 48-call task-aware package."""
import json
import prepare
import study as s

def main():
    built=prepare.build(write=False)
    expected={"PLAN.json":built["plan"],"REQUESTS.json":built["requests"],"PUBLIC.json":built["public"],"HOST_GOLD.json":built["host"],"BASELINE.json":built["baseline"],"CONFIDENCE.json":built["confidence"],"SELECTIONS.json":built["selections"]}
    for name,value in expected.items():
        if s.read(s.ROOT/"inputs"/name)!=value:raise ValueError("input value drift: "+name)
    if len(built["plan"])!=48 or sum(x["n"] for x in built["plan"])!=1280:raise ValueError("plan shape")
    if built["overlap_fraction"]>.90:raise ValueError("overlap gate; do not spend")
    if s.ATTEMPT.exists():raise ValueError("attempt exists")
    seeds={str(x["seed"]) for x in built["plan"]};matches=[]
    for path in sorted(s.SIDE.glob("*/inputs/*.json")):
        if s.ROOT in path.parents:continue
        found=sorted(seed for seed in seeds if seed in path.read_text(errors="replace"))
        if found:matches.append({"path":str(path),"seeds":found})
    if matches:raise ValueError("seed collision; no reroll: "+json.dumps(matches))
    s.write(s.ROOT/"inputs/SEED_SCAN.json",{"scope":"named sidecar input JSON existing at seal time","matches":matches,"seeds":sorted(int(x) for x in seeds)})
    idea=s.SIDE.parent/"ideas";analysis=s.SIDE.parent/"analyses/root-task-aware-selective-recheck-live-2026-09-10"
    sources=[s.ROOT/n for n in ("DESIGN.md","PLAN.md","study.py","protocol.py","prepare.py","collect.py","owner.py","seal.py","test_contract.py")]
    sources += [idea/"2026-09-10-task-aware-selective-recheck.md",idea/"2026-09-10-task-aware-selective-recheck.yaml",idea/"2026-09-10-task-aware-selective-recheck-result-amendment.md",idea/"2026-09-10-task-aware-selective-recheck-result-amendment.yaml",analysis/"METHOD.md",s.BASE/"READY.json",s.BASE.parent.parent/"analyses/root-supplied-plan-selective-recheck-live-2026-09-10/REPORT.md",s.BASE.parent/"leaf-adapter-by-granularity-v1/bg_collect.py",s.BASE.parent/"runtime-an27-5780-v1/service_wrapper_v2.py",prepare.TOKENIZER]
    inputs=sorted((s.ROOT/"inputs").glob("*.json"))+[s.ROOT/"CPU_INPUT_NATIVE.json"]
    ready={"schema":"root-task-aware-selective-recheck-ready-v1","status":"READY_CPU_ONLY_MAIN_LAUNCH_REQUIRED","planned_physical_calls":48,"planned_episodes":8,"planned_derived_episodes":32,"selected_labels_per_selection_sample":320,"selection_overlap_fraction":built["overlap_fraction"],"overlap_gate":.90,"overlap_gate_passed":True,"one_a100":True,"outer_seconds":1200,"workers":4,"request_cap_seconds":90,"root_model_calls":0,"no_training":True,"no_retry":True,"runtime_fallback":False,"selection_uses_gold":False,"shared_derived_non_independent":True,"source_sha256":{str(p):s.sha(p) for p in sources},"input_sha256":{str(p):s.sha(p) for p in inputs}}
    ready["identity"]=s.digest(ready);s.write(s.ROOT/"READY.json",ready);print(ready["identity"])
if __name__=="__main__":main()
