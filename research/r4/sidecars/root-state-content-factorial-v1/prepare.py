"""CPU-only new visibility prompts; no inference or historical source mutation."""
import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from pathlib import Path
import protocol as p
import study as s

PRIOR=s.ROOT.parent/"root-artifact-restart-v1"
PRIOR_READY_SHA="9568ab66b89269da8670b855e66e9db0c1122b8ddc196f5759afa931613f5b42"
ANCESTRY={"study.py":"ebc4d5eb1abaaedfaaa54530889eb588d30b210c6b03a0ed60e48d635e42e76c",
          "collect.py":"a4b5bbb748bfad646f2568d2a345cff325cfbee535cc0f890302a05fed1b7531",
          "owner.py":"bc4d0a913cad133f8235ba1d0ba5698943b5635e7022d2f32bde06ba220d81f6"}

def prior():
    if s.sha(PRIOR/"READY.json")!=PRIOR_READY_SHA:raise ValueError("prior source READY changed")
    ready=s.read(PRIOR/"READY.json")
    for path,pin in {**ready["source_sha256"],**ready["input_sha256"]}.items():
        if s.sha(path)!=pin:raise ValueError("original source/input changed: "+path)
    for name,pin in ANCESTRY.items():
        if s.sha(PRIOR/name)!=pin:raise ValueError("runtime ancestry changed")
    return ready

def inputs():
    started=time.time();prior()
    for name in ("STATES.json","PACKAGES.json","SOURCE_CUTS.json","PUBLIC.json","HOST_GOLD.json","NATIVE_TEMPLATE.json","BINDING.json"):
        s.write(s.ROOT/"inputs"/name,s.read(PRIOR/"inputs"/name))
    states=s.read(s.ROOT/"inputs/STATES.json");packages=s.read(s.ROOT/"inputs/PACKAGES.json")
    template=s.read(s.ROOT/"inputs/NATIVE_TEMPLATE.json");public={c["id"]:c for c in s.read(s.ROOT/"inputs/PUBLIC.json")}
    source={v["source_id"]:v for v in states}
    simple=[{k:st[k] for k in ("source_id","context_id","native_context_id","family","users","width","source_seed","source_variable")} for st in states]
    rows=p.plan(simple);assert len(rows)==64
    renderer=s.stack().native.renderer();tools=json.loads(template["tools_ordered_json"]);prompts=[]
    for row in rows:
        st=source[row["source_id"]];text=p.prompt(st["goal"],packages[row["source_id"]],row["representation"])
        ids=renderer.render([template["system"],dict(role="user",content=text)],tools=tools,add_generation_prompt=True).token_ids
        if len(ids)+2048>8192:raise ValueError("native initial context overflow; no truncation")
        task=s.task(public[row["context_id"]],text,st["goal"],row,packages[row["source_id"]])
        prompts.append(dict(id=row["id"],prompt=text,token_ids=ids,task_hash=task.hash))
    # A narrow prospective namespace scan against prepared source/plan catalogs, not all history.
    candidates=[]
    for sidecar in s.ROOT.parent.iterdir():
        if sidecar.is_dir() and sidecar!=s.ROOT:
            for pattern in ("*.py","*SPEC*.json","*PLAN*.json","inputs/*PLAN*.json"):
                candidates.extend(str(path) for path in sidecar.glob(pattern) if path.is_file())
    scan=subprocess.run(["rg","-n",r"\b981370(?:001|10[1-9]|11[0-6])\b",*sorted(set(candidates))],capture_output=True,text=True,timeout=60)
    if scan.returncode!=1:raise ValueError("seed collision or scan error: "+scan.stdout[:1000]+scan.stderr[:1000])
    s.write(s.ROOT/"inputs/PLAN.json",rows);s.write(s.ROOT/"inputs/PROMPTS.json",prompts)
    s.write(s.ROOT/"inputs/PROVENANCE.json",dict(prior_ready_sha256=PRIOR_READY_SHA,
        prior_input_sha256={str(x):s.sha(x) for x in (PRIOR/"inputs").glob("*.json")},
        runtime_ancestry_sha256={str(PRIOR/k):v for k,v in ANCESTRY.items()},
        historical_unique_child_calls=40,hypothetical64_standalone_source_calls=160,new_source_acquisitions=0,
        paired_source_states=16,context_clusters=4,outcome_informed_followup=True,
        source_selection="all16 prior pre-correction states, no outcome filtering",prior_raw_outcomes_used_as_inputs=False,
        seed_scan_paths=sorted(set(candidates)),seed_scan_exit=scan.returncode,
        native_prompt_ranges={a:[min(len(v["token_ids"]) for v,r in zip(prompts,rows) if r["representation"]==a),
            max(len(v["token_ids"]) for v,r in zip(prompts,rows) if r["representation"]==a)] for a in p.ARMS},
        export_started_epoch=started,export_ended_epoch=time.time(),cpu_export_seconds=time.time()-started,gpu_calls=0))
    print(dict(prepared=64,states=16,new_acquisitions=0))

def seal():
    previous=prior();sources=dict(previous["source_sha256"]);pins=dict(previous["input_sha256"])
    if s.read(s.ROOT/"CPU_TESTS_FINAL.json")["returncode"]!=0:raise ValueError("final focused tests must pass")
    for path in [PRIOR/"READY.json",*s.ROOT.glob("*.py"),*s.ROOT.glob("*.md")]:sources[str(path)]=s.sha(path)
    for path in [*sorted((s.ROOT/"inputs").glob("*.json")),s.ROOT/"CPU_TESTS.json",s.ROOT/"CPU_TESTS_FINAL.json"]:pins[str(path)]=s.sha(path)
    for path,pin in {**sources,**pins}.items():
        if s.sha(path)!=pin:raise ValueError("readiness drift: "+path)
    value=dict(status="CPU_READY_FOR_MAIN_ACCEPTANCE",source_sha256=sources,input_sha256=pins,
        prepared_epoch=time.time(),representations=p.ARMS,states=16,endpoints=64,contexts=4,
        root_sha256=s.source().START_SHA,child_sha256=s.source().CHILD_SHA,
        outer_seconds=3000,work_seconds=2700,owned_seconds=2880,cleanup_seconds=180,
        collection_seconds=2400,startup_seconds=300,
        argv=[str(s.NATIVE),str(s.ROOT/"owner.py"),"run","--output",str(s.ATTEMPT)],
        interpretation="outcome-informed paired action/observation visibility factorial; not fresh-context confirmation",
        qualification="focused real native prompt/setup/CLI tests; proven unchanged service runtime",gpu_calls=0)
    value["identity"]=p.digest(value);s.write(s.ROOT/"READY.json",value);print(dict(ready_sha256=s.sha(s.ROOT/"READY.json"),identity=value["identity"]))

def qualify():
    argv=[str(s.NATIVE),"-m","pytest","-q","-p","no:cacheprovider","test_protocol.py","test_native.py"]
    started=time.time();result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=60,
        env={**os.environ,"CUDA_VISIBLE_DEVICES":"","PYTHONDONTWRITEBYTECODE":"1","OMP_NUM_THREADS":"2"})
    s.write(s.ROOT/"CPU_TESTS_FINAL.json",dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
        elapsed_seconds=time.time()-started,python=platform.python_version(),
        versions={k:importlib.metadata.version(k) for k in ("torch","transformers","tokenizers","vllm")},
        scope="5 focused tests, actual native tokenizer and fresh task filesystem double; no GPU/container/service",gpu_calls=0))
    if result.returncode:raise ValueError("focused qualification failed; result retained")
    print(dict(passed=True,sha256=s.sha(s.ROOT/"CPU_TESTS_FINAL.json")))

if __name__=="__main__":
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise ValueError("CPU preparation requires hidden GPU")
    ap=argparse.ArgumentParser();ap.add_argument("command",choices=("inputs","qualify","seal"));a=ap.parse_args()
    {"inputs":inputs,"qualify":qualify,"seal":seal}[a.command]()
