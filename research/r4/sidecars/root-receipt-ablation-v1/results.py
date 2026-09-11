"""Descriptive triple contrasts; original exact score, separate unknown outcomes."""
import json
import sys
from pathlib import Path
import experiment as e

saved = sys.modules.get("study")
sys.modules["study"] = e.old
old = e.private("receipt_original_analysis", e.PRIOR/"analysis.py")
if saved is None:
    sys.modules.pop("study",None)
else:
    sys.modules["study"] = saved


def episode_metrics(episode, seconds):
    value = old.episode_metrics(episode,seconds)
    events, failures = [], []
    for trace in episode.get("traces") or []:
        audit = trace.get("info",{}).get("receipt_audit")
        if not audit:
            continue
        if audit.get("raw") is None:
            failures.append(audit)
            continue
        try:
            events.extend(json.loads(line) for line in audit["raw"].splitlines() if line)
        except (ValueError,TypeError) as error:
            failures.append({"type":type(error).__name__,"message":str(error)})
    replies = [row["receipt"] for row in events if row.get("event")=="helper_result"]
    value["receipt_diagnostics"] = {"helper_requests":sum(row.get("event")=="helper_request" for row in events),
        "helper_errors":sum(row.get("event")=="helper_error" for row in events),
        "receipt_accesses":sum(row.get("event")=="receipt_access" for row in events),
        "helper_results":len(replies),"valid_receipts":sum(row["valid"] for row in replies),
        "receipts":replies,"audit_read_failures":failures,
        "interpretation":"Requested-subset syntactic correspondence only; access is not proof of use in final aggregate."}
    return value


def summarize(records,plan):
    planned = {row["id"]:row for row in plan}
    observed = {row["coordinate"]["id"]:row for row in records}
    if len(observed)!=len(records) or any(row["coordinate"]!=planned.get(key) for key,row in observed.items()):
        raise ValueError("duplicate/unplanned/drifting coordinate")
    cells=[]
    for arm in e.ARMS:
        rows=[r["derived"] for r in records if r["coordinate"]["arm"]==arm]
        cells.append({"arm":arm,"planned":sum(r["arm"]==arm for r in plan),"recorded":len(rows),
            "observable":sum(r.get("strict_reward") is not None for r in rows),
            "strict_successes":sum(r.get("strict_reward")==1 for r in rows),
            "execution_failures":sum(not r.get("execution_completed",False) for r in rows),
            "usage":{key:sum(r.get(key,0) or 0 for r in rows) for key in
                ("model_calls","completion_tokens","logical_input_tokens","wall_seconds","recursive_subcalls","truncated_calls","calls_without_cache_measurement")},
            "receipt":{key:sum(r.get("receipt_diagnostics",{}).get(key,0) for r in rows) for key in
                ("helper_requests","helper_errors","receipt_accesses","helper_results","valid_receipts")}})
    matches={}
    for row in plan:
        match=matches.setdefault(row["matched_id"],{"matched_id":row["matched_id"],"context_sha256":row["context_sha256"],
            "task_name":row["task_name"],"seed":row["seed"],"outcomes":{arm:None for arm in e.ARMS}})
        match["outcomes"][row["arm"]]=observed.get(row["id"],{}).get("derived",{}).get("strict_reward")
    pairs=[("receipt","indexed_raw"),("indexed_raw","unchanged"),("receipt","unchanged")]
    def contrasts(rows):
        result={}
        for left,right in pairs:
            values=[row["outcomes"][left]-row["outcomes"][right] for row in rows
                if row["outcomes"][left] is not None and row["outcomes"][right] is not None]
            result[left+"_minus_"+right]={"observable_matches":len(values),"gains":sum(v>0 for v in values),
                "losses":sum(v<0 for v in values),"ties":sum(v==0 for v in values),"sum":sum(values)}
        return result
    return {"planned":len(plan),"recorded":len(records),"cells":cells,"matched":list(matches.values()),
        "contrasts":contrasts(matches.values()),"contexts":[{"context_sha256":sha,
            "contrasts":contrasts([row for row in matches.values() if row["context_sha256"]==sha])}
            for sha in sorted({r["context_sha256"] for r in plan})],
        "unrun_coordinates":[r["id"] for r in plan if r["id"] not in observed],
        "caution":"72 episodes/24 triples/six exposed contexts. Missing/infra outcomes remain unknown. Child choices can diverge."}


def analyze(output):
    spec=e.verify()
    files=sorted(Path(output).glob("phase-*/rollout/episodes/*.json"))
    records=[e.c.read(p) for p in files]
    report=summarize(records,spec["plan"])
    evidence=[]
    for path,row in zip(files,records,strict=True):
        if e.c.digest(row["episode"])!=row["episode_sha256"]:
            raise ValueError("raw episode hash changed")
        proof={"path":str(path),"sha256":e.c.file_hash(path),"native_capture_verified":False}
        try:
            roots,calls=e.native.exporter.episode_turns(row["episode"],path.parent.parent.with_name("rollout-routing"),spec["binding"])
            if any(call["sampling"]["seed"]!=row["coordinate"]["seed"] for call in calls):
                raise ValueError("physical call seed mismatch")
            proof.update(native_capture_verified=True,root_calls=len(roots),child_calls=len(calls)-len(roots))
        except (ValueError,KeyError,TypeError,AttributeError) as error:
            proof["error"]={"type":type(error).__name__,"message":str(error)}
        evidence.append(proof)
    report["episode_evidence"]=evidence
    costs=[]
    for path in sorted(Path(output).glob("phase-*/rollout-routing/role-audit/*-result.json")):
        audit=e.c.read(path)
        wire=audit.get("native_wire_request",{}).get("body",{})
        response=audit.get("native_wire_response",{})
        try:
            payload=json.loads(response.get("body","null"))
            choices=payload.get("choices",[]) if isinstance(payload,dict) else []
        except json.JSONDecodeError:
            choices=[]
        costs.append({"path":str(path),"sha256":e.c.file_hash(path),"request_id":audit.get("request_id"),
            "alias":audit.get("actual_alias"),"depth":audit.get("depth"),"status":audit.get("status"),
            "http_status":response.get("http_status"),"physical_prompt_tokens":len(wire["token_ids"]) if "token_ids" in wire else None,
            "physical_action_tokens":sum(len(choice.get("token_ids") or []) for choice in choices) if choices else None,
            "cached_tokens":None,"wall_seconds":audit["ended"]-audit["started"]})
    report["all_native_attempt_audits"]=costs
    report["physical_cost_totals"]={"retained_attempts":len(costs),
        "physical_prompt_tokens":sum(row["physical_prompt_tokens"] or 0 for row in costs),
        "physical_action_tokens":sum(row["physical_action_tokens"] or 0 for row in costs),
        "missing_prompt_counts":sum(row["physical_prompt_tokens"] is None for row in costs),
        "missing_action_counts":sum(row["physical_action_tokens"] is None for row in costs),"cached_tokens":None}
    e.c.write_once(Path(output)/"ANALYSIS.json",report)
    return report
