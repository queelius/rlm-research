"""Seal the fixed 36-call ID-renaming mechanism probe."""

import json
import subprocess
import time

import study


def main():
    if study.READY.exists():
        raise FileExistsError(study.READY)
    source_ready = study.base.verify()
    data = study.read(study.ROOT / "DATA_READY.json")
    assert data["planned_calls"] == 36 and data["only_implementation_id_strings_changed"]
    study.write_x(study.ROOT / "INPUTS.json", {"schema": "b05-id-renaming-eval-inputs-v1",
        "calls": [dict(call=call, request=study.request_for(call), prompt=study.prompt(call))
                  for call in study.calls()]})
    study.write_x(study.ROOT / "BINDING.json", study.binding())
    command = [str(study.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider",
               str(study.ROOT / "test_eval.py")]
    started = time.time(); process = subprocess.run(command, capture_output=True, text=True, timeout=120)
    receipt = study.ROOT / "CPU_TESTS.json"
    study.write_x(receipt, {"command": command, "returncode": process.returncode,
        "stdout": process.stdout, "stderr": process.stderr, "elapsed_seconds": time.time()-started,
        "actual_inherited_collector_native_http_fixture": True, "GPU_calls": 0, "model_calls": 0})
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    closure = dict(source_ready["closure_sha256"])
    closure[str(study.base.READY)] = study.sha(study.base.READY)
    for name in ("prepare_data.py", "ID_MAPPING_PUBLIC.json", "RENAMED_TASKS.json", "HOST_GOLD.json",
                 "DATA_READY.json", "study.py", "collect.py", "metrics.py", "owner.py", "QUESTION.md",
                 "test_eval.py", "prepare.py", "INPUTS.json", "BINDING.json", "CPU_TESTS.json"):
        path = study.ROOT / name
        closure[str(path)] = study.sha(path)
    mapping = study.read(study.ROOT / "ID_MAPPING_PUBLIC.json")
    token_counts = [len(study.request_for(call)["token_ids"]) for call in study.calls()]
    value = {"schema": "b05-selection-id-renaming-native-readout-ready-v1",
        "created_epoch": time.time(),
        "question": "Does the fixed selection update's local advantage survive a bijective renaming of every implementation ID?",
        "claim_boundary": "in-sample mechanism probe; tokenization changes; not pure causal or generalization proof",
        "source_eval_ready_sha256": study.sha(study.base.READY),
        "data_ready_sha256": study.sha(study.ROOT / "DATA_READY.json"),
        "mapping_sha256": study.sha(study.ROOT / "ID_MAPPING_PUBLIC.json"),
        "mapping_namespace": mapping["namespace"], "mapping_used_outcomes_or_gold": False,
        "planned": {"stage_contexts": 9, "repeats": 2, "base": 18, "cp1": 18, "total": 36},
        "sampling": {"temperature": .5, "top_p": 1., "top_k": -1, "min_p": 0.,
                     "max_tokens": 384, "same_source_seeds": True},
        "prefix_token_bounds": {"minimum": min(token_counts), "maximum": max(token_counts),
                                "all_prefix_plus_output_le8192": True},
        "binding": study.binding(), "metrics": {"primary": "strict renamed eligible-ID set exact",
            "secondary": "unordered-known-unique ID exact and balanced accuracy", "unknown_separate": True},
        "caps_seconds": {"science": 600, "owner": 700, "external": 800},
        "attempt": str(study.ATTEMPT), "GPU_calls_during_preparation": 0,
        "model_calls_during_preparation": 0,
        "argv": [str(study.NATIVE), str(study.ROOT / "owner.py"), "run", "--outer-seconds", "700"],
        "closure_sha256": dict(sorted(closure.items()))}
    value["identity"] = study.digest(value)
    study.write_x(study.READY, value)
    print(json.dumps({"sha256": study.sha(study.READY), "identity": value["identity"]}, sort_keys=True))


if __name__ == "__main__":
    main()
