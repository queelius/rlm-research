"""Copy the exact supplied-plan40 science inputs and change only the served model alias."""

import copy
import time
from collections import Counter

import study as s


def main():
    prior = s.PRIOR_CEILING / "inputs"
    values = {name: s.read(prior / name) for name in
              ("PUBLIC.json", "HOST_GOLD.json")}
    old_plan = s.read(prior / "PLAN.json")
    old_requests = s.read(prior / "REQUESTS.json")
    old_prompt_ids = s.read(prior / "PROMPT_IDS.json")
    plan, requests, prompt_ids = [], {}, {}
    for old in old_plan:
        row = copy.deepcopy(old)
        old_id = row.pop("id")
        row["model_policy"] = "mixed_sft24"
        row["id"] = s.digest(["root-lambda-supplied-plan-mixed-child-20260910-v1", row])
        body = copy.deepcopy(old_requests[old_id])
        body["model"] = s.MIXED_ALIAS
        plan.append(row)
        requests[row["id"]] = body
        prompt_ids[row["id"]] = old_prompt_ids[old_id]
    values.update({"PLAN.json": plan, "REQUESTS.json": requests,
                   "PROMPT_IDS.json": prompt_ids})
    values["PROVENANCE.json"] = {
        "schema": "supplied-plan-mixed-child-bridge-provenance-v1",
        "created_epoch": time.time(),
        "prior_ready_sha256": s.sha(s.PRIOR_CEILING / "READY.json"),
        "prior_terminal_sha256": s.sha(s.PRIOR_CEILING / "outputs/attempt-001/OWNER_TERMINAL.json"),
        "prior_input_sha256": {name: s.sha(prior / name) for name in
                               ("PUBLIC.json", "HOST_GOLD.json", "PLAN.json", "REQUESTS.json", "PROMPT_IDS.json")},
        "science_identity": "plan coordinates differ only policy/call IDs; public/gold and prompt token values identical; request bodies differ only model alias",
        "mixed_checkpoint": str(s.MIXED), "mixed_adapter_sha256": s.MIXED_SHA,
        "host_gold_private_analysis_only": True, "child_optimizer_exposed": True,
        "both_results_research_exposed": True, "no_control_rerun": True,
    }
    physical = sorted((s.PRIOR_CEILING / "outputs/attempt-001/rollout/calls").glob("*/*.json"))
    physical = [path for path in physical if path.name in
                ("REQUEST.json", "RESPONSE.json", "RESULT.json")]
    values["OLD_CONTROL_PINS.json"] = {
        "schema": "supplied-plan-c32-control-receipts-v1",
        "owner_terminal_sha256": s.sha(
            s.PRIOR_CEILING / "outputs/attempt-001/OWNER_TERMINAL.json"
        ),
        "counts": dict(Counter(path.name for path in physical)),
        "physical_files_sha256": {str(path): s.sha(path) for path in physical},
    }
    for name, value in values.items(): s.write(s.ROOT / "inputs" / name, value)


if __name__ == "__main__": main()
