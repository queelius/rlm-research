"""Seal CPU-prepared inputs only after exact adopted-ceiling qualification."""
from pathlib import Path
import json

import prepare
import study as s


def main():
    rebuilt=prepare.build(write=False)
    expected={"PLAN.json":rebuilt["plan"],"REQUESTS.json":rebuilt["requests"],"PUBLIC.json":rebuilt["public"],"HOST_GOLD.json":rebuilt["host"],"BASELINE.json":rebuilt["baselines"],"CONFIDENCE.json":rebuilt["confidences"],"SELECTIONS.json":rebuilt["selections"],"CEILING_CALL_PINS.json":rebuilt["call_pins"]}
    for name,value in expected.items():
        if s.read(s.ROOT/"inputs"/name)!=value:raise ValueError("input not byte-value reproducible: "+name)
    plan=rebuilt["plan"]
    if len(plan)!=24 or sum(r["n"] for r in plan)!=640:raise ValueError("plan shape")
    if any(r["n"] not in (16,32) for r in plan):raise ValueError("repack shape")
    if (s.ROOT/"outputs/attempt-001").exists():raise ValueError("attempt already exists")
    seeds={str(r["seed"]) for r in plan};matches=[]
    for path in sorted(s.SIDE.glob("*/inputs/*.json")):
        if s.ROOT in path.parents:continue
        text=path.read_text(errors="replace");found=sorted(seed for seed in seeds if seed in text)
        if found:matches.append({"path":str(path),"seeds":found})
    if matches:raise ValueError("seed collision; no reroll: "+json.dumps(matches))
    s.write(s.ROOT/"inputs/SEED_SCAN.json",{"scope":"named sidecar input JSON existing at seal time","matches":matches,"seeds":sorted(int(x) for x in seeds)})
    analysis=s.SIDE.parent/"analyses/root-supplied-plan-selective-recheck-live-2026-09-10"
    design=s.SIDE.parent/"analyses/root-supplied-plan-selective-recheck-design-2026-09-10"
    source_paths=[s.ROOT/name for name in ("DESIGN.md","PLAN.md","study.py","protocol.py","prepare.py","collect.py","owner.py","seal.py","test_contract.py")]
    source_paths += [analysis/"METHOD.md",design/"DESIGN_AMENDMENT_NO_FALLBACK.md",design/"AMENDMENT_SEAL.json",
        s.CEILING/"READY.json",s.CEILING/"study.py",s.CEILING/"prepare.py",s.CEILING/"protocol.py",
        s.CEILING/"outputs/attempt-001/OWNER_TERMINAL.json",prepare.EXIT_PATH,
        s.CEILING_ANALYSIS/"REPORT.md",s.CEILING_ANALYSIS/"FINAL_SEAL.json",
        s.CEILING_ANALYSIS/"MAIN_ADOPTION.json",
        prepare.TOKENIZER,
        s.SIDE/"leaf-trec-test-adapter-granularity-v1/READY.json",
        s.SIDE.parent/"analyses/leaf-trec-confidence-ranking-live-2026-09-10/MAIN_ADOPTION.json",
        s.SIDE/"leaf-adapter-by-granularity-v1/bg_collect.py",
        s.SIDE/"runtime-an27-5780-v1/service_wrapper_v2.py"]
    input_paths=sorted((s.ROOT/"inputs").glob("*.json"))+[s.ROOT/"CPU_INPUT_NATIVE.json"]
    ready={"schema":"root-supplied-plan-selective-recheck-ready-v1","status":"READY_CPU_ONLY_MAIN_LAUNCH_REQUIRED","planned_calls":24,"planned_episodes_per_arm":8,"selected_labels_per_arm":320,"one_a100":True,"outer_seconds":1800,"workers":4,"root_model_calls":0,"no_training":True,"no_retry":True,"runtime_fallback":False,"ceiling_alignment":rebuilt["alignment"],"source_sha256":{str(p):s.sha(p) for p in source_paths},"input_sha256":{str(p):s.sha(p) for p in input_paths}}
    ready["identity"]=s.digest(ready);s.write(s.ROOT/"READY.json",ready);print(ready["identity"])


if __name__=="__main__":main()
