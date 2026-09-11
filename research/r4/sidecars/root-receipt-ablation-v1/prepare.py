"""Freeze72 CPU-prepared coordinates and authenticated source closure once."""
import json
import os
import subprocess
import time
from pathlib import Path
import experiment as e

c=e.c


def seeds_in(value):
    result=set()
    if isinstance(value,dict):
        for key,child in value.items():
            if key in ("seed","seed_master","seed_audit_master") and type(child) is int:
                result.add(child)
            result.update(seeds_in(child))
    elif isinstance(value,list):
        for child in value:
            result.update(seeds_in(child))
    return result


def prepare():
    tasks=e.make_tasks()
    plan=e.build_plan(tasks)
    prior=c.read(e.PRIOR/"SPEC.json")
    seed_files=sorted(set(e.ROOT.parent.glob("*/SPEC*.json")) | set(e.ROOT.parent.glob("*/inputs/PLANS.json")))
    seed_files=[p for p in seed_files if e.ROOT not in p.parents]
    old_seeds=set()
    for path in seed_files:
        old_seeds.update(seeds_in(c.read(path)))
    collision=old_seeds & {row["seed"] for row in plan}
    if collision:
        raise ValueError("declared seeds collide: "+str(sorted(collision)))
    audit={"seed_master":e.SEED_MASTER,"distinct_rollout_seeds":sorted({r["seed"] for r in plan}),
        "previous_seed_count":len(old_seeds),"collisions":[],
        "source_sha256":{str(p):c.file_hash(p) for p in seed_files},
        "scope":"Existing top-level sidecar SPEC*.json and inputs/PLANS.json only; no outcomes read and no global registry claim."}
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(Path(prior["base_model"])/"tokenizer.json"))
    identities=[]
    for name,task in tasks.items():
        arms={}
        for arm in e.ARMS:
            variant=e.with_prompt(task,arm)
            prompt=variant.data.prompt
            arms[arm]={"prompt":prompt,"prompt_sha256":e.hashlib.sha256(prompt.encode()).hexdigest(),
                "task_hash":variant.hash,"prompt_tokens":len(tokenizer.encode(prompt,add_special_tokens=False).ids)}
        identities.append({"name":name,"context_sha256":e.hashlib.sha256(task.data.context.encode()).hexdigest(),
            "context_window_id":task.data.context_window_id,"gold_sha256":c.digest(task.data.answer),"arms":arms,
            "catalog_sha256":c.digest(e.catalog_for(task))})
    policy=prior["policies"]["step8"]
    binding=e.binding_for(policy)
    c.write_once(e.ROOT/"inputs/PLAN.json",plan)
    c.write_once(e.ROOT/"inputs/TASKS.json",identities)
    c.write_once(e.ROOT/"inputs/BINDING.json",binding)
    c.write_once(e.ROOT/"inputs/SEED_AUDIT.json",audit)
    catalogs={t.data.context_window_id:e.catalog_for(t) for t in tasks.values()}
    c.write_once(e.ROOT/"inputs/PUBLIC_CATALOGS.json",catalogs)
    proof=c.read(e.ROOT/"qualification-map-attempt-001/RESULT.json")
    if proof["provider_calls"]!=9 or proof["actual_model_calls"]!=0 or proof["gpu_calls"]!=0:
        raise ValueError("three-arm actual CPU proof missing")
    sources=dict(prior["source_file_sha256"])
    paths=list(e.ROOT.glob("*.py"))+list(e.ROOT.glob("*.md"))+list((e.ROOT/"inputs").glob("*.json"))
    paths += [e.PRIOR/"SPEC.json",e.PRIOR/"study.py",e.PRIOR/"driver.py",e.PRIOR/"analysis.py",e.DECISION,e.DECISION.with_name("DESIGN_PROPOSAL.md"),e.DECISION.with_name("RECEIPT_FORMAT_AMENDMENT.md")]
    paths += list((e.ROOT/"qualification-map-attempt-001").rglob("*.json"))
    sources.update({str(p):c.file_hash(p) for p in paths})
    c.authenticate(sources)
    spec={"schema":e.ROOT.name,"source_file_sha256":sources,"plan":plan,"plan_sha256":c.digest(plan),
        "tasks":identities,"policy":policy,"binding":binding,"seed_master":e.SEED_MASTER,"seed_audit":audit,
        "environment":prior["environment"],"image_id":prior["image_id"],"sampling":prior["sampling"],
        "renderer":prior["renderer"],"base_model":prior["base_model"],"base_manifest_sha256":prior["base_manifest_sha256"],
        "max_concurrent_pairs":8,"max_concurrent_triples":8,"wall_time_cap_seconds":2400,
        "collection_cap_seconds":2100,"work_cap_seconds":2280,"cleanup_reserve_seconds":120,"outer_cap_seconds":2430,
        "exposure":prior["exposure"],"source_provenance":prior["source_provenance"],
        "inherited_retry_caveat":prior["inherited_retry_caveat"],"partial_trace_limitation":prior["partial_trace_limitation"],
        "objective":"inference-only optional receipt incremental effect; strict task success unchanged",
        "receipt_format":"strict JSON object mapping public selected source IDs to caller-allowed label strings; no grammar",
        "scored_episodes":72,"coordinate_triples":24,"live_smoke":None,
        "collector_adapter":{"original_sha256":e.COLLECTOR_SHA,"adapted_sha256":e.hashlib.sha256(e.collector_source().encode()).hexdigest(),
            "changes":"Exactly two queue chunk literals2->3; no other collector semantics changed"}}
    c.write_once(e.ROOT/"SPEC.json",spec)
    command=[str(c.NATIVE_PYTHON),"-m","unittest","test_receipt","test_experiment","test_results","test_driver","-v"]
    env={**os.environ,"CUDA_VISIBLE_DEVICES":"","PYTHONDONTWRITEBYTECODE":"1"}
    started=time.time()
    tests=subprocess.run(command,cwd=e.ROOT,env=env,capture_output=True,text=True,timeout=90)
    c.write_once(e.ROOT/"FOCUSED_TESTS.json",{"argv":command,"returncode":tests.returncode,"stdout":tests.stdout,
        "stderr":tests.stderr,"seconds":time.time()-started,"gpu_calls":0})
    if tests.returncode:
        raise ValueError("focused tests failed; no READY")
    argv=[str(c.NATIVE_PYTHON),str(e.ROOT/"driver.py"),"run","--output",str(e.ROOT/"outputs/attempt-001")]
    artifacts=[e.ROOT/"SPEC.json",e.ROOT/"FOCUSED_TESTS.json",*list((e.ROOT/"qualification-map-attempt-001").rglob("*.json"))]
    ready={"schema":e.ROOT.name,"planned":72,"prepared_epoch":time.time(),"spec_sha256":c.file_hash(e.ROOT/"SPEC.json"),
        "driver_sha256":c.file_hash(e.ROOT/"driver.py"),"launch_argv":argv,"launch_command":"PYTHONDONTWRITEBYTECODE=1 "+" ".join(argv),
        "outer_cap_seconds":2430,"owned_job_cap_seconds":2400,"work_cap_seconds":2280,"collection_cap_seconds":2100,
        "artifact_sha256":{str(p):c.file_hash(p) for p in artifacts},"actual_model_calls_during_preparation":0,"gpu_calls_during_preparation":0,
        "fake_provider_calls_during_qualification":9,"superseded_array_qualification":{"path":str(e.ROOT/"qualification-attempt-001"),"fake_provider_calls":9,"model_calls":0,"status":"superseded by pre-inference format amendment"},
        "acceptance":"CPU READY only; main must review and accept before launch",
        "environment":"Main supplies exclusive CUDA_VISIBLE_DEVICES and existing STRICT_RLM_CALIBRATION_API_KEY; never stored here."}
    c.write_once(e.ROOT/"READY.json",ready)
    print(json.dumps({"ready":str(e.ROOT/"READY.json"),"ready_sha256":c.file_hash(e.ROOT/"READY.json"),"planned":72,"gpu_calls":0}))


if __name__=="__main__":
    prepare()
