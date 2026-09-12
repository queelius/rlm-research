"""Run the paired one-wide versus three-narrow AnomalyXL budget-shape pilot."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import time
from urllib.request import Request, urlopen

import budget_study as m


def _source():
    previous=sys.modules.get("mini");sys.modules["mini"]=m.base
    if str(m.V1) not in sys.path: sys.path.insert(0,str(m.V1))
    try:
        spec=importlib.util.spec_from_file_location("anomalyxl_v1_owner_sealed",m.V1/"owner.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    finally:
        if previous is None: sys.modules.pop("mini",None)
        else: sys.modules["mini"]=previous
    if module.m is not m.base or module.m.ATTEMPT!=m.ATTEMPT: raise ValueError("V1 owner seam bound wrong study/attempt")
    return module


source=_source();native_service=source.native_service
RESEARCH_CALL_CAP=80


def research_admissible(calls):
    return sum(not c["engineering"] for c in calls)<RESEARCH_CALL_CAP


class NativeCalls(source.NativeCalls):
    """Same immutable wire recorder as V1, with the sealed 80-call V2 inventory cap."""
    def call(self,messages,maximum,destination,deadline,engineering=False):
        if time.time()>=deadline: raise TimeoutError("native call deadline")
        if not engineering and not research_admissible(self.calls): raise ValueError("80 research call cap")
        if sum(c["engineering"] for c in self.calls)>=2 and engineering: raise ValueError("two engineering call cap")
        request=m.body(messages,maximum)
        if destination.exists(): raise ValueError("call destination already used")
        destination.mkdir(parents=True);wire=json.dumps(request,separators=(",", ":")).encode();(destination/"REQUEST_WIRE.bin").write_bytes(wire);m.write(destination/"MESSAGES.json",messages)
        began=time.time();raw=None;result={"engineering":engineering,"status":"request_error","call_id":destination.name,"request_wire_sha256":m.sha(destination/"REQUEST_WIRE.bin"),"request_sha256":m.digest(request),"requested_max_tokens":maximum,"requested_prompt_tokens":len(request["token_ids"]),"started_epoch":began};error=None
        try:
            req=Request(self.endpoint,data=wire,headers={"Content-Type":"application/json"},method="POST")
            with urlopen(req,timeout=max(.001,min(180,deadline-time.time()))) as response: response_wire=response.read()
            (destination/"RESPONSE_WIRE.bin").write_bytes(response_wire);raw=json.loads(response_wire);decoded=m.decode(request,raw)
            if decoded["request_id"] in self.ids: raise ValueError("duplicate native provider request ID")
            self.ids.add(decoded["request_id"]);result.update(decoded,status="returned_valid")
        except Exception as exc:
            error=exc;result["error"]={"type":type(exc).__name__,"message":str(exc)}
            if isinstance(raw,dict):
                for field in ("prompt_tokens","completion_tokens"):
                    count=raw.get("usage",{}).get(field)
                    if type(count) is int and count>=0: result[field]=count
        result["elapsed_seconds"]=time.time()-began;result["response_wire_sha256"]=m.sha(destination/"RESPONSE_WIRE.bin") if (destination/"RESPONSE_WIRE.bin").exists() else None;m.write(destination/"CALL.json",result);self.calls.append(result);m.write(m.ATTEMPT/"CALL_PROGRESS.json",{"attempted_calls":len(self.calls),"last_call_id":destination.name,"last_call_sha256":m.sha(destination/"CALL.json")})
        if error is not None: raise error
        return result


def turns(arm):
    return {"direct":0,"python_wide1":1,"python_repair3":3}[arm]


def episode(row,client,global_deadline):
    began=time.time();deadline=min(global_deadline,began+m.EPISODE_CAP);directory=m.ATTEMPT/"episodes"/row["episode_id"];directory.mkdir(parents=True)
    outcome={**row,"status":"failed","answer":"","started_epoch":began,"generated_tokens":0,"episode_cap_seconds":m.EPISODE_CAP,"aggregate_output_cap":m.TOTAL_OUTPUT}
    before=len(client.calls)
    try:
        if row["arm"]=="direct":
            value=m.read(m.V1/"inputs/direct"/f"{row['row_id']}.json")
            call=client.call([{"role":"user","content":value["prompt"]}],2048,m.ATTEMPT/"calls"/(row["episode_id"]+"-final"),deadline)
            outcome.update(answer=call["text"],status="answered",direct_view=value["view"],generated_tokens=call["completion_tokens"],final_finish_reason=call["finish_reason"])
        else:
            public=m.read(m.V1/"inputs/public"/f"{row['row_id']}.json");workspace=directory/"workspace";m.write(workspace/"context.json",{"series":public["series"]})
            messages=[{"role":"user","content":m.inspection_prompt(public["question"],row["arm"])}]
            with m.executor(workspace) as worker:
                for turn in range(turns(row["arm"])):
                    call=client.call(messages,m.allowance(row["arm"],outcome["generated_tokens"],False),m.ATTEMPT/"calls"/f"{row['episode_id']}-inspect-{turn}",deadline)
                    outcome["generated_tokens"]+=call["completion_tokens"]
                    result=m.execute_cell(worker,call["text"],min(8,max(.001,deadline-time.time())))
                    m.write(directory/f"EXECUTION-{turn}.json",result);observation,inventory=m.observation(result);m.write(directory/f"OBSERVATION-{turn}.json",{"text":observation,**inventory})
                    messages.extend([{"role":"assistant","content":call["text"]},{"role":"user","content":observation+"\nNext inspection: one complete concise fenced python cell only."}])
            messages.append({"role":"user","content":"FINAL TURN. Python is disabled. Give only one JSON object matching the original question schema, without prose or fences."})
            call=client.call(messages,m.allowance(row["arm"],outcome["generated_tokens"],True),m.ATTEMPT/"calls"/(row["episode_id"]+"-final"),deadline)
            outcome.update(answer=call["text"],status="answered",generated_tokens=outcome["generated_tokens"]+call["completion_tokens"],final_finish_reason=call["finish_reason"])
    except Exception as exc: outcome["error"]={"type":type(exc).__name__,"message":str(exc)}
    outcome["call_ids"]=[c["call_id"] for c in client.calls[before:]];outcome["elapsed_seconds"]=time.time()-began;m.write(directory/"EPISODE.json",outcome);return outcome


def execute(cap):
    ready=m.verify()
    if cap!=m.CAP or m.ATTEMPT.exists() or not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]: raise ValueError("MAIN must assign one GPU and unused attempt under exact1800 cap")
    began=time.time();m.ATTEMPT.mkdir(parents=True);m.write(m.ATTEMPT/"OWNER_RUN.json",{"ready_sha256":m.sha(m.ROOT/"READY.json"),"identity":ready["identity"],"started_epoch":began,"cap_seconds":cap,"planned_episodes":30,"research_call_cap":80,"engineering_call_cap":2})
    process=client=None;qualified=released=False;errors=[];outcomes=[]
    def stop(sig,_frame): raise TimeoutError("owner interrupted by signal "+str(sig))
    previous={sig:signal.signal(sig,stop) for sig in (signal.SIGALRM,signal.SIGTERM,signal.SIGINT)};signal.setitimer(signal.ITIMER_REAL,cap-30);deadline=began+cap-120
    try:
        process,endpoint=native_service.start(m.ATTEMPT/"service",min(deadline,began+240));client=NativeCalls(endpoint);source.engineering(client,min(deadline,time.time()+60));qualified=True
        for row in m.schedule():
            if time.time()>=deadline: break
            outcome=episode(row,client,deadline);outcomes.append(outcome);m.write(m.ATTEMPT/"PROGRESS.json",{"episodes_terminal":len(outcomes),"last_episode":row["episode_id"],"last_status":outcome["status"],"elapsed_seconds":time.time()-began})
    except BaseException as exc: errors.append({"type":type(exc).__name__,"message":str(exc)})
    finally:
        signal.setitimer(signal.ITIMER_REAL,min(90,max(1,began+cap-time.time())))
        try:
            if process is not None: native_service.release(process,m.ATTEMPT/"service")
            released=True
        except BaseException as exc: errors.append({"stage":"release","type":type(exc).__name__,"message":str(exc)})
        gold=m.read(m.V1/"inputs/HOST_GOLD.json");by_id={r["episode_id"]:r for r in outcomes};scored=[]
        for row in m.schedule():
            value=by_id.get(row["episode_id"],{**row,"status":"unattempted","answer":""});scored.append({**value,"score":m.score(value["answer"],gold[row["row_id"]])})
        paired=[]
        for identifier in dict.fromkeys(r["row_id"] for r in m.schedule()):
            values={r["arm"]:r["score"]["primary"] for r in scored if r["row_id"]==identifier};paired.append({"row_id":identifier,**values,"wide1_minus_direct":values["python_wide1"]-values["direct"],"repair3_minus_direct":values["python_repair3"]-values["direct"],"wide1_minus_repair3":values["python_wide1"]-values["python_repair3"]})
        calls=client.calls if client else [];cost={}
        for arm in ("direct","python_wide1","python_repair3"):
            selected=[c for c in calls if f"-{arm}-" in c["call_id"]];cost[arm]={"attempted_calls":len(selected),"observed_prompt_tokens":sum(c.get("prompt_tokens",0) for c in selected),"observed_completion_tokens":sum(c.get("completion_tokens",0) for c in selected),"unknown_usage_calls":sum("prompt_tokens" not in c or "completion_tokens" not in c for c in selected)}
        report={"schema":"anomalyxl-native-budget-shape-result-v2","runtime_qualified":qualified,"primary_readout_eligible":qualified and len(outcomes)==30 and released,"episodes":scored,"paired":paired,"mean_primary":{arm:sum(r["score"]["primary"] for r in scored if r["arm"]==arm)/10 for arm in ("direct","python_wide1","python_repair3")},"cost":cost,"owner_elapsed_seconds":time.time()-began,"complete_episodes":len(outcomes)==30,"released":released,"claim":"Same exposed ten cases; tests turn allocation/interface feasibility, not a clean Python capability effect or generalization."};m.write(m.ATTEMPT/"RESULT.json",report)
        terminal={"runtime_qualified":qualified,"released":released,"episodes_terminal":len(outcomes),"errors":errors,"complete":qualified and released and len(outcomes)==30 and not errors,"elapsed_seconds":time.time()-began,"result_sha256":m.sha(m.ATTEMPT/"RESULT.json")};m.write(m.ATTEMPT/"OWNER_TERMINAL.json",terminal);signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items(): signal.signal(sig,handler)
    return terminal


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","run"));parser.add_argument("--outer-seconds",type=int,default=m.CAP);args=parser.parse_args()
    if args.command=="verify": print(m.verify()["identity"])
    else:
        result=execute(args.outer_seconds);print(json.dumps(result));raise SystemExit(0 if result["complete"] else 1)
