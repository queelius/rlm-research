"""Plain native calls only; gold targets and interpreter are not used during collection."""
import concurrent.futures
import study
with study.aliases({"runner_study": study}, study.SOURCE):
    inherited = study.load("finqa_native_plain_collector", study.SOURCE / "runner_collect.py")
Collector = inherited.Collector


def execute(endpoint, output, deadline):
    runner = Collector(endpoint, output, deadline)
    public = study.read(study.INPUTS)
    plans = public["calls"]
    errors = []
    def question(index):
        selected = [call for call in plans if call["context_index"] == index]
        if index % 2: selected.reverse()
        for call in selected:
            runner.call(call, public["prompts"][study.call_id(call)])
    with concurrent.futures.ThreadPoolExecutor(max_workers=study.CONCURRENCY) as pool:
        futures = [pool.submit(question,index) for index in range(16)]
        for future in concurrent.futures.as_completed(futures):
            try: future.result()
            except Exception as error: errors.append({"type":type(error).__name__,"detail":str(error)})
    return {"physical_started":runner.physical,"unique_provider_ids":len(runner.provider_ids),"errors":errors,
            "gold_targets_loaded_in_collector":False,"programs_executed_in_collector":False}
