"""CPU construct real tasks/prefixes and authenticate both fixed endpoints once."""

import asyncio
import copy
import json
import os

import protocol
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only freeze")
    contexts, _gold = study.data()
    public = {row["id"]: row for row in contexts}
    es, terminal, _helper, _decoder, _causal = study.sources()
    renderer = terminal.qs.qnative().stack().native.renderer()
    template = study.read(es.SOURCE_INPUTS / "NATIVE_TEMPLATE.json")
    tools = json.loads(template["tools_ordered_json"])
    prefixes = {}
    for arm in study.ARMS:
        system = copy.deepcopy(template["system"])
        if arm == "no_child_python":
            system["content"] = es.no_child_system()
        for row in study.plan(arm):
            context = public[row["context_id"]]
            task = study.make_task(context, row, _gold[context["id"]]["answers"][row["operator"]])
            other = study.make_task(context, row, 999999)
            files = study.runtime_files(context, row)
            if "aggregate(" in files["batch_contract.py"].decode() or "question(" in files["batch_contract.py"].decode():
                raise ValueError("host reducer leaked into public module")
            if task.data.prompt != other.data.prompt:
                raise ValueError("host gold altered model prompt")
            ids = renderer.render([system, {"role": "user", "content": task.data.prompt}],
                                  tools=tools, add_generation_prompt=True).token_ids
            if len(ids) + 2048 > 8192:
                raise ValueError("initial root prefix plus output exceeds8192")
            prefixes[row["id"]] = {"token_ids": ids, "task_hash": task.hash,
                "prompt_sha256": __import__("hashlib").sha256(task.data.prompt.encode()).hexdigest(),
                "file_sha256": {name: __import__("hashlib").sha256(payload).hexdigest() for name, payload in files.items()},
                "gold_independent_prompt": True, "max_prefix_plus2048": len(ids) + 2048}
    for left, right in zip(study.plan("c32"), study.plan("rl_step8")):
        if prefixes[left["id"]]["token_ids"] != prefixes[right["id"]]["token_ids"] or left["seed"] != right["seed"]:
            raise ValueError("helper arms lack identical root prefix/paired seed")
    study.write_x(study.INPUTS / "PREFIXES.json", prefixes)
    for arm in ("c32", "rl_step8"):
        study.write_x(study.INPUTS / ("BINDING_" + arm + ".json"), study.binding(arm))
    # Backward-compatible completion of the initial data preparation, if it finished before
    # its canonical-exposure artifact was added. Content is derived only from frozen inputs.
    exposure = study.INPUTS / "PUBLIC_EXPOSURE.json"
    if not exposure.exists():
        by_id = {row["id"]: row for c in contexts for row in c["records"]}
        study.write_x(exposure, {"records": [{"dataset": "ag_news", "id": row["id"],
            "source_id": row["source_id"], "text": by_id[row["id"]]["text"]}
            for row in study.read(study.INPUTS / "PROVENANCE.json")]})
    print({"frozen_tasks": len(prefixes), "helper_prefix_pairs": 16,
           "max_root_prefix_plus2048": max(row["max_prefix_plus2048"] for row in prefixes.values()),
           "live_model_calls": 0})


if __name__ == "__main__":
    main()
