"""Conditional MAIN-only owner: skip absent update2, otherwise one fixed72 readout."""
import argparse, json, os, signal, time, traceback
from pathlib import Path
import readout_study as study
import readout_common as common
import readout_collect as collect
import readout_export as export
import readout_native as native

def budget(start): return {"started":start,"work":start+2400,"owned":start+2670,"outer":start+2700}
def collector_argv(stage,deadline): return [str(study.NATIVE),str(study.ROOT/"readout_collect.py"),"--spec",str(stage/"CAPTURE_SPEC.json"),"--output",str(stage/"rollout"),"--deadline",str(float(deadline))]
def planned_inventory(output):
    return [{"phase":"readout","arm":"checkpoint2","coordinate":row,
             "export":str(Path(output)/"readout/export/EPISODES.json"),"reward":None,
             "available":False,"reason":"planned before service"}
            for row in study.read(study.SOURCE/"inputs/PLANS.json")["readout"]]
def dependencies():
    with study.aliases({"terminal_study":study,"terminal_common":common,"terminal_collect":collect,
                        "terminal_export":export,"terminal_native":native}):
        module=study.load("checkpoint2_terminal_owner_dependencies",study.SOURCE/"terminal_owner.py")
    return module.dependencies()
def _usage(records):
    known={name:0 for name in ("input","output","cached")};unknown={name:0 for name in known}
    for record in records:
        usage=record.get("usage") or {}
        fields={"input":usage.get("prompt_tokens"),"output":usage.get("completion_tokens"),"cached":(usage.get("prompt_tokens_details") or {}).get("cached_tokens")}
        for name,value in fields.items():
            if type(value) is int and value>=0:known[name]+=value
            else:unknown[name]+=1
    return {"known":known,"unknown":unknown}
def cost_ledger(output):
    output=Path(output);requests=sorted(output.glob("**/role-audit/*-request.json"));results=sorted(output.glob("**/role-audit/*-result.json"))
    result_rows=[study.read(p) for p in results];result_ids={r.get("request_id") for r in result_rows};usage_rows=[];success=0;http_responses=0
    for row in result_rows:
        wire=row.get("native_wire_response") or {};status=wire.get("http_status");body=wire.get("body")
        if isinstance(status,int):http_responses+=1
        try: raw=json.loads(body) if isinstance(body,str) else {}
        except json.JSONDecodeError:raw={}
        if isinstance(status,int) and 200<=status<300 and bool(raw.get("choices")):success+=1
        usage_rows.append({"usage":raw.get("usage") if isinstance(raw,dict) else None})
    other=sorted(set(output.glob("**/REQUEST.json"))|set(output.glob("**/RESPONSE.json"))|set(output.glob("**/RESULT.json"))|set(output.glob("**/FAILURE.json")))
    return {"role_requests":len(requests),"response_proven_attempts":len(results),"raw_http_responses":http_responses,"http_2xx_choice_payloads":success,"prepared_attempt_unknown":sum(study.read(p).get("request_id") not in result_ids for p in requests),"usage":_usage(usage_rows),"record_sha256":{str(p):study.sha(p) for p in requests+results+other},"missing_usage_not_synthesized":True,"billing":"not measured"}
def execute(output):
    output=Path(output)
    if output.resolve()!=study.ATTEMPT.resolve(): raise ValueError("exact attempt-001 only")
    if output.exists(): raise FileExistsError("attempt retained")
    campaign=study.verify_prepared(); decision=study.checkpoint2_decision(); started=time.time(); limits=budget(started)
    output.mkdir(parents=True); inventory=planned_inventory(output)
    study.write(output/"PLANNED_NULL_ENDPOINTS.json",inventory)
    if not decision["run"]:
        terminal={"complete":False,"skipped":True,"reason":decision["reason"],"planned":72,
                  "physical_requests":0,"released":True,"elapsed_seconds":time.time()-started}
        study.write(output/"SKIP.json",terminal); study.write(output/"OWNER_TERMINAL.json",terminal); return terminal
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("MAIN must assign exactly one GPU")
    suite=dependencies(); service=output/"service"; service.mkdir(); active=True; errors=[]; result=None
    previous=signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError("owned deadline")))
    try:
        startup=min(limits["work"],time.time()+180)
        signal.setitimer(signal.ITIMER_REAL,max(.001,startup-time.time()))
        suite.start_service(service,collect.binding_for(decision["policy"]),startup)
        stage=output/"readout"; stage.mkdir(); deadline=limits["work"]
        signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
        collect.prepare_spec("readout-checkpoint2",service/"BINDING.json",service/"service/endpoint-original.json",stage/"CAPTURE_SPEC.json",max(.001,deadline-time.time()),None)
        suite.command(service,"collect-checkpoint2",collector_argv(stage,deadline),max(.001,deadline-time.time()),deadline)
        result=export.export_attempt(stage/"rollout",stage/"export")
    except BaseException as error:
        errors.append({"type":type(error).__name__,"message":str(error),"traceback":traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(.001,min(limits["owned"],time.time()+90)-time.time()))
        try: suite.release_service(service); active=False
        except BaseException as error: errors.append({"type":type(error).__name__,"message":str(error),"release_failed":True})
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
    terminal={"complete":not errors and bool(result and result["complete"]),"skipped":False,
              "errors":errors,"policy":decision["policy"],"result":result,"planned":72,
              "released":not active,"elapsed_seconds":time.time()-started}
    study.write(output/"COST_LEDGER.json",cost_ledger(output));study.write(output/"OWNER_TERMINAL.json",terminal); return terminal
def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument("command",choices=("verify","run"));p.add_argument("--output",type=Path,default=study.ATTEMPT);return p.parse_args(argv)
if __name__=="__main__":
    a=parse_args();v=study.verify_prepared() if a.command=="verify" else execute(a.output);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if a.command=="verify" or v.get("complete") or v.get("skipped") else 1)
