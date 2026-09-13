"""Public-only grouping and normalization views; no eligibility computation."""

import copy
import json


MARKER = "Local shard (authoritative JSON):\n"


def public_view(prompt):
    assert prompt.count(MARKER) == 1
    body = prompt.split(MARKER, 1)[1]
    view, end = json.JSONDecoder().raw_decode(body)
    suffix = body[end:]
    assert suffix.lstrip().startswith(
        "Return exactly one JSON object with exactly one key, eligible_ids."
    )
    return view, suffix


def unresolved_view(view):
    result = {key: copy.deepcopy(view[key])
              for key in ("child_id", "child_index", "role", "public_domains")}
    stage = view["stage"]
    result["stage"] = {key: copy.deepcopy(stage[key])
                       for key in ("child_id", "stage_index", "role", "policy")}
    tables = stage["tables"]
    records = []
    for base in tables["implementations"]:
        identifier = base["implementation_id"]
        records.append({"implementation": copy.deepcopy(base),
            "all_change_rows": [copy.deepcopy(row) for row in tables["changes"]
                                if row["implementation_id"] == identifier],
            "all_check_rows": [copy.deepcopy(row) for row in tables["checks"]
                               if row["implementation_id"] == identifier]})
    assert [row["implementation"] for row in records] == tables["implementations"]
    canonical = lambda rows: sorted(json.dumps(row, sort_keys=True, separators=(",", ":"))
                                    for row in rows)
    assert canonical([row for record in records for row in record["all_change_rows"]]) == canonical(tables["changes"])
    assert canonical([row for record in records for row in record["all_check_rows"]]) == canonical(tables["checks"])
    result["stage"]["candidate_records"] = records
    result["local_query"] = copy.deepcopy(view["local_query"])
    return result


def render_unresolved(raw_prompt):
    view, suffix = public_view(raw_prompt)
    grouped = unresolved_view(view)
    return (
        f"Evaluate only the local {view['role']} catalog. You do not need information from "
        "another stage.\n\nThe original public rows below have only been grouped by candidate. "
        "Each record retains its unchanged base implementation row, ALL applicable change rows "
        "including drafts, and ALL applicable check rows including older revisions. No deltas, "
        "features, or checks have been resolved; no candidate was filtered and no eligibility "
        "decision was made. Apply the original query and every policy clause yourself.\n\n"
        "Candidate-grouped unresolved local shard (authoritative JSON):\n"
        + json.dumps(grouped, ensure_ascii=False, sort_keys=True, indent=2)
        + suffix
    )
