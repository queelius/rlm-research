"""Same sealed raw decoder/scorer, exact-runtime c32 reuse and all fixed seed contrasts."""
import json
import bundle as b


def execute():
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(b.study.MODEL,local_files_only=True)
    new,runtime,provenance=b.compare.audited_arm(b.ARM,tokenizer)
    old=b.original_audit()
    arms={b.ARM:new}
    origins={b.ARM:provenance}
    comparisons={}
    for arm in ("c32","rl_step8"):
        value,old_runtime,origin=old.audited_arm(arm,tokenizer)
        keys=("configuration_sha256","service_wrapper_sha256","native_python",
              "max_prompt_plus_1024","actual_max_model_len","concurrency","batch")
        matched=bool(runtime and old_runtime) and all(runtime[k]==old_runtime[k] for k in keys)
        arms[arm],origins[arm]=value,origin
        comparisons[arm+"_vs_"+b.ARM] = (
            {"available":True,**b.metrics.paired(value,new,b.study.gold(),b.study.schedule())}
            if matched else {"available":False,"reason":"runtime mismatch forbids baseline reuse"})
    return dict(schema="same512-training-seed-replica-source-to-raw-v1",arms=arms,
        comparisons=comparisons,provenance=origins,baseline_physical_calls_reused=128,
        replica_new_physical_calls=128,baseline_new_model_calls=0,
        primary="c32 versus fixed replica step8",secondary="seed1 versus seed2 descriptive paired contrast",
        boundary="same research-exposed512; training-seed replication, not new data or independent trainer implementation")


if __name__ == "__main__":
    print(json.dumps(execute(),sort_keys=True))
