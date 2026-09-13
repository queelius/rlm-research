"""Pure public-record normalization; no eligibility, gold, filtering or file access."""
import copy
import json

MARKER="Local shard (authoritative JSON):\n"


def public_view(prompt):
    assert prompt.count(MARKER)==1
    body=prompt.split(MARKER,1)[1]
    view,end=json.JSONDecoder().raw_decode(body)
    suffix=body[end:]
    assert suffix.lstrip().startswith("Return exactly one JSON object with exactly one key, eligible_ids.")
    return view,suffix


def effective_candidates(stage):
    tables=stage["tables"];rows=[]
    for base in tables["implementations"]:
        identifier=base["implementation_id"]
        applied=[r for r in tables["changes"] if r["implementation_id"]==identifier and r["status"]=="applied"]
        features=set(base["base_features"])
        features.update(r["feature_add"] for r in applied if r["feature_add"]!="none")
        features.difference_update(r["feature_remove"] for r in applied if r["feature_remove"]!="none")
        checks={}
        for name in stage["policy"]["required_checks"]:
            matches=[r for r in tables["checks"] if r["implementation_id"]==identifier and r["check_name"]==name]
            latest=max(matches,key=lambda r:r["revision"]) if matches else None
            checks[name]={"revision":latest["revision"],"passed":latest["passed"]} if latest is not None else None
        row={k:base[k] for k in ("implementation_id","input_format","output_format")}
        row.update({k:base["base_"+k]+sum(r[k+"_delta"] for r in applied) for k in ("cost","latency","capacity","quality")})
        rows.append({**row,"features":sorted(features),"latest_required_checks":checks})
    assert len(rows)==len(tables["implementations"])
    return rows


def normalized_view(view):
    result={k:copy.deepcopy(view[k]) for k in ("child_id","child_index","role","public_domains")}
    stage=view["stage"]
    result["stage"]={k:copy.deepcopy(stage[k]) for k in ("child_id","stage_index","role","policy")}
    result["stage"]["effective_candidates"]=effective_candidates(stage)
    result["local_query"]="Retain exactly the implementations that pass every latest required check and all local numeric policy clauses."
    return result


def render(raw_prompt):
    view,suffix=public_view(raw_prompt)
    return (f"Evaluate only the local {view['role']} catalog. You do not need information from another stage.\n\n"
            "The public-source mechanical joins below are already resolved: draft changes were ignored, applied numeric deltas were summed, "
            "all applied feature additions were unioned before all applied removals, and the greatest revision of each required check was selected. "
            "A null check means no public row exists for that required check. ALL original candidates are retained; no eligibility decision has been made. "
            "Using these effective records, apply every original local policy clause and required check yourself.\n\n"
            "Mechanically normalized local shard (authoritative JSON):\n"+
            json.dumps(normalized_view(view),ensure_ascii=False,sort_keys=True,indent=2)+suffix)
