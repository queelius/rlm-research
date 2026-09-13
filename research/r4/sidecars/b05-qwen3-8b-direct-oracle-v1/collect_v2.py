"""Eight-call collector bound to the repaired study namespace."""

import concurrent.futures
import sys

import study_v2 as study

old = sys.modules.get("runner_study")
sys.modules["runner_study"] = study
try:
    source = study.load("b05_qwen8_collector_source_v2", study.SOURCE / "runner_collect.py")
finally:
    if old is None:
        sys.modules.pop("runner_study", None)
    else:
        sys.modules["runner_study"] = old


def execute(endpoint, output, deadline):
    collector = source.Collector(endpoint, output, deadline)
    errors = []

    def one(root):
        planned = [item for item in study.calls() if item["root_id"] == root["root_id"]]
        for call in planned:
            if call["kind"] == "direct":
                prompt, reports = root["direct_prompt"], None
            else:
                host = study.host_by_root()[root["root_id"]]
                reports, prompt = host["exact_child_reports"], host["oracle_synthesis_prompt"]
            prompt = study.contract().clarify(call, prompt)
            collector.call(call, prompt, root=root["safe_root"], reports=reports)
        study.write_x(
            output / "roots" / (root["root_id"] + ".json"),
            {
                "root_id": root["root_id"],
                "planned_call_ids": [study.call_id(item) for item in planned],
                "all_2_accounted": len(planned) == 2,
            },
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=study.CONCURRENCY) as pool:
        futures = {pool.submit(one, root): root["root_id"] for root in study.roots()}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as error:
                errors.append(
                    {
                        "root_id": futures[future],
                        "type": type(error).__name__,
                        "detail": str(error),
                    }
                )
    return {
        "physical_started": collector.physical,
        "unique_provider_ids": len(collector.provider_ids),
        "errors": errors,
    }

