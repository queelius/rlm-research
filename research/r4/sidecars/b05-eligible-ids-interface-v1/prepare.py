"""Focused CPU preparation and qualified V3 comparator seal; never starts a model."""
import argparse
import json
from pathlib import Path
import subprocess
import interface
import owner
import study


def cpu():
    assert not (study.ROOT / "CPU_PREPARED.json").exists()
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_interface.py", "--basetemp=cpu-fixture-seal-001"]
    completed = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True)
    study.write_x(study.ROOT / "CPU_TESTS.json", {"command": command, "returncode": completed.returncode,
                  "stdout": completed.stdout, "stderr": completed.stderr, "GPU_calls": 0})
    assert completed.returncode == 0
    inventory = []
    roots = {root["root_id"]: root for root in study.active_roots()}
    for call in study.calls():
        original = roots[call["root_id"]]["child_prompts"][call["child_index"]]
        prompt = interface.render(original)
        request = study.request_body(prompt, call["seed"], call["max_tokens"])
        inventory.append({"call": call, "call_id": study.call_id(call), "prompt": prompt, "request": request,
                          "original_child_prompt_sha256": study.digest(original),
                          "public_prefix_sha256": study.digest(original.split(interface.MARKER, 1)[0]),
                          "prefix_token_ids_sha256": study.digest(request["token_ids"])})
    study.write_x(study.ROOT / "INPUTS.json", {"schema": "b05-ids-only-frozen-native-inputs-v1", "calls": inventory})
    assert study.sha(study.BASELINE_READY) == study.BASELINE_READY_SHA
    closure = dict(study.read(study.BASELINE_READY)["closure_sha256"])
    closure[str(study.BASELINE_READY)] = study.BASELINE_READY_SHA
    for path in sorted(study.ROOT.glob("*.py")) + [study.ROOT / "RUNBOOK.md", study.ROOT / "CPU_TESTS.json", study.ROOT / "INPUTS.json"]:
        closure[str(path)] = study.sha(path)
    ready = {"schema": "b05-ids-only-cpu-prepared-v1", "status": "NOT_GPU_ADMITTED_COMPARATOR_QUALIFICATION_REQUIRED",
             "planned_child_calls": 24, "root_model_calls": 0, "closure_sha256": dict(sorted(closure.items()))}
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "CPU_PREPARED.json", ready)
    owner.implementation()
    return ready


def seal():
    cpu_path = study.ROOT / "CPU_PREPARED.json"
    prepared = study.read(cpu_path)
    assert prepared["identity"] == study.digest({key: value for key, value in prepared.items() if key != "identity"})
    for path, expected in prepared["closure_sha256"].items():
        assert study.sha(Path(path)) == expected, path
    if not (study.BASELINE / "OWNER_TERMINAL.json").exists():
        pending = study.ROOT / "PENDING_BASELINE.json"
        if not pending.exists():
            study.write_x(pending, {"status": "PENDING", "baseline": str(study.BASELINE), "one_completion_check": True})
        return {"status": "PENDING", "no_polling": True}
    study.qualify_baseline()
    closure = dict(prepared["closure_sha256"])
    closure[str(cpu_path)] = study.sha(cpu_path)
    contract = study.load("ids_only_baseline_contract", study.SOURCE / "contract_v3.py")
    roots = {root["root_id"]: root for root in study.active_roots()}
    for name in ("OWNER_TERMINAL.json", "OWNER_RUN.json", "RESULT.json", "BINDING.json", "ENGINE_ATTESTATION.json"):
        path = study.BASELINE / name
        closure[str(path)] = study.sha(path)
    for call in study.calls():
        path = study.BASELINE / "calls" / (study.call_id(call)+".json")
        record = study.read(path)
        closure[str(path)] = study.sha(path)
        original = roots[call["root_id"]]["child_prompts"][call["child_index"]]
        expected_prompt = contract.clarify(call, original)
        prompt = study.read(record["prompt_path"])
        request = study.read(record["request_path"])
        response = study.read(record["response_path"])
        assert prompt == {"messages": [{"role": "user", "content": expected_prompt}]}
        assert request == study.request_body(expected_prompt, call["seed"], 384)
        decoded = study.decode_response(request, response)
        assert decoded["transport_valid"] and decoded["text"] == record["text"]
        assert decoded["completion_ids"] == record["completion_ids"]
        for key in ("prompt_path", "request_path", "response_path"):
            closure[record[key]] = study.sha(Path(record[key]))
    ready = {"schema": "b05-eligible-ids-interface-ready-v1", "status": "CPU_READY_MAIN_REVIEW_NO_GPU_ADMISSION",
             "baseline": str(study.BASELINE), "baseline_ready_sha256": study.BASELINE_READY_SHA,
             "baseline_terminal_sha256": study.sha(study.BASELINE / "OWNER_TERMINAL.json"),
             "attempt": str(study.ATTEMPT), "planned_calls": 24, "root_model_calls": 0,
             "owner_seconds": 700, "science_seconds": 600, "external_seconds": 800,
             "argv": [str(study.NATIVE), str(study.ROOT / "owner.py"), "run", "--outer-seconds", "700"],
             "primary": "eligible-ID-set exactness over24; precision/recall with strict-valid denominator and invalid/unknown separate",
             "lookup_both_arms": "public effective fields of exactly claimed known IDs, without eligibility filtering",
             "model_seed_temperature_max_tokens_unchanged": True, "native_public_shard_prefix_unchanged": True,
             "output_contract_intentionally_changed": True, "gold_or_eligible_catalog_in_prompts": False,
             "physical24_natural3children_per_host_plan": True, "host_arithmetic_not_model_skill": True,
             "four_exposed_context_units": True, "CPU32_recombined_tuples_not_independent": True,
             "launch_authority": "MAIN only", "closure_sha256": dict(sorted(closure.items()))}
    ready["identity"] = study.digest(ready)
    study.write_x(study.READY_RUN, ready)
    study.verify()
    return {"ready": str(study.READY_RUN), "sha256": study.sha(study.READY_RUN), "identity": ready["identity"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("cpu", "seal"))
    args = parser.parse_args()
    print(json.dumps(cpu() if args.command == "cpu" else seal()))
