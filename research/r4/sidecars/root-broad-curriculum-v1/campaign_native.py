"""Qualified native collector and exact exclusion-only exporter under fresh identity."""
import argparse
import asyncio
import json
import sys
import types

import campaign_common as c

sys.modules["campaign_native"] = sys.modules[__name__]
impl = c.adapted("broad16_native_original", c.OLD / "campaign_native.py", [
    ('c.ROOT / "READY.json"', 'c.ROOT / "PREPARED.json"', 1)])
installed = False


def make_tasks():
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTask
    from oolong_prime_v1.taskset import _QUESTION_INSTRUCTION, _RLM_FILE_INSTRUCTION, OolongData
    from tokenizers import Tokenizer

    public = c.read(c.ROOT / "inputs/PUBLIC.json")
    gold = c.read(c.ROOT / "inputs/HOST_GOLD.json")
    contexts = {row["id"]: row["text"] for row in public["contexts"]}
    tokenizer = Tokenizer.from_file(str(c.Path(c.pilot_recipe()["base_model"]) / "tokenizer.json"))
    tasks = {}
    for index, row in enumerate(public["tasks"]):
        context = contexts[row["context_id"]]
        data = OolongData(idx=index, name=row["name"],
            prompt=_QUESTION_INSTRUCTION + "\n\n" + _RLM_FILE_INSTRUCTION + "\n\nQuestion: " + row["question"],
            source_id=row["source_id"], source_split="candidate-root-broad-" + row["analysis_split"],
            source_revision=c.read(c.ROOT / "inputs/PROVENANCE.json")["source_split_sha256"],
            dataset=c.ROOT.name, context_len=len(tokenizer.encode(context, add_special_tokens=False).ids),
            context_window_id=row["context_window_id"], answer=gold[row["name"]]["answer"],
            answer_type="ANSWER_TYPE.NUMERIC", task_kind="local-count-by-coarse-category", context=context)
        tasks[row["name"]] = StrictOolongTask(data, StrictOolongConfig().task)
    return tasks


impl.make_tasks = make_tasks


def __getattr__(name):
    return getattr(impl, name)


def verify_amendment():
    c.verify_campaign()
    value = c.read(c.ROOT / "AMENDMENT.json")
    if c.digest({k: v for k, v in value.items() if k != "amendment_id"}) != value["amendment_id"] or value["inherited_optimizer_steps"] != 0:
        raise ValueError("broad16 amendment changed")
    c.authenticate(value["source_sha256"])
    c.authenticate(value["input_sha256"])
    return value


def install():
    global installed, binding_for, prepare_spec, export, authenticate_export
    if installed:
        return
    import campaign
    life = campaign.lifecycle()
    common = types.ModuleType("broad16_amendment_common")
    common.c, common.ROOT = c, c.ROOT
    common.OLD_ROUND04 = c.ROOT / "NO_INHERITED_ROUND04"
    common.verify_amendment = verify_amendment
    prior = sys.modules.get("common")
    sys.modules["common"] = common
    try:
        amended = c.private("broad16_exclusion_original", c.CONT / "native_amendment.py")
    finally:
        if prior is None:
            sys.modules.pop("common", None)
        else:
            sys.modules["common"] = prior
    binding_for, prepare_spec = amended.binding_for, amended.prepare_spec
    export, authenticate_export = amended.export, amended.authenticate_export
    installed = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["collect", "export", "verify-export", "verify"])
    parser.add_argument("--spec", type=c.Path)
    parser.add_argument("--attempt", type=c.Path)
    parser.add_argument("--output", type=c.Path)
    args = parser.parse_args()
    install()
    if args.command == "verify":
        result = {"initial_binding": binding_for(c.original_policy()), "gpu_calls": 0}
    elif args.command == "collect":
        spec = impl.verify_spec(args.spec)
        if spec.get("continuation_amendment_id") != verify_amendment()["amendment_id"]:
            raise ValueError("wrong fresh seed capture identity")
        result = asyncio.run(impl.collect(args.spec, args.output))
    elif args.command == "export":
        result = export(args.attempt, args.output)
    else:
        result = authenticate_export(args.output)
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
