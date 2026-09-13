"""Plain native collector; representation prompts are frozen before runtime."""

import concurrent.futures
import study


with study.aliases({"runner_study": study}, study.SOURCE):
    inherited = study.load("b05_state_repr_plain_collector", study.SOURCE / "runner_collect.py")
Collector = inherited.Collector


def execute(endpoint, output, deadline):
    runner = Collector(endpoint, output, deadline)
    plan = study.read(study.INPUTS); errors = []

    def stage(task):
        for call in plan["calls"]:
            if call["root_id"] == task["root_id"]:
                runner.call(call, plan["prompts"][study.call_id(call)])

    with concurrent.futures.ThreadPoolExecutor(max_workers=study.CONCURRENCY) as pool:
        futures = [pool.submit(stage, task) for task in plan["tasks"]]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as error:
                errors.append({"type": type(error).__name__, "detail": str(error)})
    return {"physical_started": runner.physical, "unique_provider_ids": len(runner.provider_ids),
            "errors": errors, "gold_loaded": False, "eligibility_computed": False}

