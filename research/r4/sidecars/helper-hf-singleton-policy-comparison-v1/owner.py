"""Run one fresh-service singleton helper arm."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import signal
import time
from urllib.request import Request, urlopen

import study


def send(endpoint, row, tokenizer, destination, timeout):
    started = time.time(); study.write(destination / "REQUEST.json", row); raw = None
    try:
        request = Request(endpoint, data=json.dumps(row["body"], separators=(",", ":")).encode(),
            headers=study.validator().headers(), method="POST")
        with urlopen(request, timeout=timeout) as response: raw = json.loads(response.read())
        study.write(destination / "RESPONSE.json", raw)
        if len(raw.get("choices", [])) != 1 or not raw.get("request_id") or raw.get("model") != study.CHILD_ALIAS:
            raise ValueError("native response identity differs")
        choice, usage = raw["choices"][0], raw["usage"]
        if (usage["prompt_tokens"] != len(row["body"]["token_ids"]) or
                usage["completion_tokens"] != len(choice["token_ids"]) or choice.get("finish_reason") != "stop"):
            raise ValueError("native token inventory/finish differs")
        result = study.validator().response_record(row, raw, tokenizer, started, time.time())
        result["raw_response_file_sha256"] = study.sha(destination / "RESPONSE.json")
    except Exception as error:
        result = {"call_id": row["call_id"], "dataset": row["dataset"], "start": row["start"],
            "ids": row["ids"], "status": "request_error" if raw is None else "integrity_error",
            "prediction": {}, "error": {"type": type(error).__name__, "message": str(error)}}
    result.update(batch_size=1, started_epoch=started, ended_epoch=time.time(),
        wall_seconds=time.time()-started, request_body_sha256=study.digest(row["body"]),
        requested_prompt_tokens=len(row["body"]["token_ids"]))
    study.write(destination / "CALL.json", result); return result


def summarize(arm, calls, rows, gold):
    planned = {row["call_id"]: row for row in rows}; observed = {row["call_id"]: row for row in calls}
    if len(planned) != 256 or len(observed) != len(calls) or not observed.keys() <= planned.keys():
        raise ValueError("call inventory differs")
    metrics = {dataset: {"planned": 128, "attempted": 0, "available": 0, "correct": 0,
        "wrong": 0, "unavailable": 0, "prompt_tokens": 0, "completion_tokens": 0,
        "cached_prompt_tokens": 0, "wall_seconds": 0.0, "label_changes": Counter()}
        for dataset in ("trec", "ag_news")}
    records = {}
    for row in rows:
        call = observed.get(row["call_id"]); identifier = row["ids"][0]; metric = metrics[row["dataset"]]
        metric["attempted"] += call is not None; available = call is not None and call.get("status") == "returned_valid"
        prediction = call["prediction"].get(identifier) if available else None; label = gold["labels"][identifier]
        correct = available and prediction == label
        records[identifier] = {"id": identifier, "dataset": row["dataset"], "source_call_id": row["call_id"],
            "gold": label, "prediction": prediction, "available": available, "correct": bool(correct)}
        metric["available"] += available; metric["correct"] += correct
        metric["wrong"] += available and not correct; metric["unavailable"] += not available
        if available: metric["label_changes"][label + " -> " + prediction] += 1
        if call:
            for field in ("prompt_tokens", "completion_tokens", "cached_prompt_tokens"):
                metric[field] += int(call.get(field) or 0)
            metric["wall_seconds"] += float(call.get("wall_seconds") or 0)
    for metric in metrics.values(): metric["label_changes"] = dict(metric["label_changes"])
    return {"schema": "helper-hf-singleton-policy-arm-result-v1", "arm": arm,
        "complete_inventory": len(calls) == 256, "planned_calls": 256, "attempted_calls": len(calls),
        "planned_predictions": 256, "datasets": metrics, "records": records, "calls": calls,
        "claim_boundary": "Adaptive research-exposed fixed256 singleton-shape readout; no confirmatory generalization."}


def execute(arm, cap):
    ready = study.verify(arm); attempt = study.ATTEMPTS[arm]
    if cap != study.CAP or attempt.exists(): raise ValueError("exact unused arm attempt and cap900 required")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"] or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("MAIN must assign one GPU and private credential")
    started=time.time();deadline=started+cap-90;calls=[];errors=[];suite=None;released=False
    attempt.mkdir(parents=True);service=attempt/"service";service.mkdir();rows=study.schedule();gold=study.size().source().panel()[3]
    study.write(attempt/"OWNER_RUN.json",{"ready_identity":ready["identity"],"arm":arm,"started_epoch":started,
        "planned_calls":256,"planned_predictions":256,"cap_seconds":cap,"root_calls":0,"training_updates":0})
    def stop(sig,_frame): raise TimeoutError("singleton policy comparison deadline")
    previous={sig:signal.signal(sig,stop) for sig in (signal.SIGALRM,signal.SIGTERM,signal.SIGINT)};signal.setitimer(signal.ITIMER_REAL,cap-30)
    try:
        from transformers import AutoTokenizer
        tokenizer=AutoTokenizer.from_pretrained(study.MODEL,local_files_only=True);suite=study.dependencies()
        bound=study.binding(arm);suite.start_service(service,bound,min(started+240,deadline))
        study.write(attempt/"RUNTIME_ATTESTATION.json",study.attest(service/"service"))
        descriptor=study.read(service/"service/endpoint-original.json");endpoint=f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate";request_ids=set()
        for row in rows:
            if time.time()>=deadline: raise TimeoutError("request deadline; remaining slots unattempted")
            result=send(endpoint,row,tokenizer,attempt/"calls"/row["call_id"],max(1,min(180,deadline-time.time())))
            provider=result.get("request_id")
            if provider and provider in request_ids: raise ValueError("duplicate provider request ID")
            if provider: request_ids.add(provider)
            calls.append(result);study.write(attempt/"PROGRESS.json",{"attempted_calls":len(calls),"elapsed_seconds":time.time()-started})
    except BaseException as error: errors.append({"type":type(error).__name__,"message":str(error)})
    finally:
        signal.setitimer(signal.ITIMER_REAL,60)
        if suite is not None:
            try:suite.release_service(service);released=True
            except BaseException as error:errors.append({"stage":"release","type":type(error).__name__,"message":str(error)})
        else:released=True
        result=summarize(arm,calls,rows,gold);study.write(attempt/"RESULT.json",result)
        terminal={"complete":not errors and released and len(calls)==256,"released":released,"errors":errors,
            "attempted_calls":len(calls),"elapsed_seconds":time.time()-started};study.write(attempt/"OWNER_TERMINAL.json",terminal)
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in previous.items():signal.signal(sig,handler)
    return terminal


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","run"));parser.add_argument("--arm",choices=study.ARMS,required=True);parser.add_argument("--outer-seconds",type=int,default=study.CAP);args=parser.parse_args()
    if args.command=="verify":print(study.verify(args.arm)["identity"])
    else:
        terminal=execute(args.arm,args.outer_seconds);print(json.dumps(terminal,sort_keys=True));raise SystemExit(0 if terminal["complete"] else 1)
