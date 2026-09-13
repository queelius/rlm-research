"""Qualify one completed native rollout batch and freeze identical inputs for both credit arms."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
ROLLOUT = ROOT.parent / "b05-varied-vector-rollouts-v1"
OUT = ROOT / "TRAIN_INPUTS.json"
RECEIPT = ROOT / "DATA_QUALIFICATION.json"


def module(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def build():
    study = module("vector_credit_source_study", ROLLOUT / "study.py")
    credit = module("vector_credit_data_math", ROOT / "credit.py")
    ready = study.read(ROLLOUT / "CPU_READY.json")
    terminal_path = ROLLOUT / "outputs/attempt-001/OWNER_TERMINAL.json"
    result_path = ROLLOUT / "outputs/attempt-001/RESULT.json"
    terminal = study.read(terminal_path); result = study.read(result_path)
    assert all(terminal[key] for key in ("complete", "released", "runtime_qualified"))
    assert terminal["result_sha256"] == study.sha(result_path)
    assert result["complete"] and result["available"] == 64 and result["unknown"] == 0
    assert result["held_calls_executed"] == 0 and result["no_optimizer_or_adapter"]
    plan = study.read(study.INPUTS); tasks = {row["root_id"]: row for row in plan["tasks"]}
    gold = {row["root_id"]: set(row["gold_ids"]) for row in study.read(study.HOST)["rows"]
            if row["split"] == "train"}
    records = {path.stem: study.read(path) for path in
               (ROLLOUT / "outputs/attempt-001/calls").glob("*.json")}
    result_rows = {row["call_id"]: row for row in result["rows"]}
    assert set(records) == set(result_rows) == {study.call_id(call) for call in plan["calls"]}
    episodes = []; group_receipts = []
    for root_id, task in tasks.items():
        calls = sorted([call for call in plan["calls"] if call["root_id"] == root_id],
                       key=lambda call: call["repeat"])
        assert [call["repeat"] for call in calls] == [0, 1, 2, 3]
        order = task["public_order"]; correctness = []; valid = []
        for call in calls:
            row = result_rows[study.call_id(call)]; keep = bool(row["semantic_valid"])
            valid.append(keep)
            selected = set(row["ids"] or [])
            correctness.append([int((candidate in selected) == (candidate in gold[root_id]))
                                for candidate in order])
        reward = credit.advantages(correctness, valid)
        differing = any(reward["local"][i][j] != reward["joint"][i][j]
                        for i in range(4) for j in range(len(order)))
        group_receipts.append({"root_id": root_id, "candidate_count": len(order),
            "sample_valid": valid, "candidate_rewards": reward["candidate_rewards"],
            "response_rewards": reward["response_rewards"], "local_advantages": reward["local"],
            "joint_advantages": reward["joint"], "credit_modes_differ": differing})
        for index, call in enumerate(calls):
            key = study.call_id(call); record = records[key]; row = result_rows[key]
            assert record["transport_valid"] and record["completion_ids"]
            request = study.read(record["request_path"])
            assert request == plan["requests"][key] and request["token_ids"]
            coefficients = credit.token_credit(row["native_spans"],
                action_tokens=len(record["completion_ids"]), candidates=len(order),
                valid=bool(row["semantic_valid"]))
            root_turn = {"prompt_ids": request["token_ids"], "action_ids": record["completion_ids"],
                "input_ids": request["token_ids"] + record["completion_ids"],
                "labels": [-100] * len(request["token_ids"]) + record["completion_ids"],
                "loss_mask": [0] * len(request["token_ids"]) + [1] * len(record["completion_ids"]),
                "old_logprobs": record["completion_logprobs"]}
            union_mask = [int(any(value > 0 for value in coeff)) for coeff in coefficients["coefficients"]]
            episodes.append({"episode_id": key, "group_id": root_id, "repeat": call["repeat"],
                "root_id": root_id, "candidate_count": len(order), "public_order": order,
                "semantic_valid": bool(row["semantic_valid"]),
                "raw_candidate_correctness": correctness[index] if row["semantic_valid"] else None,
                "effective_candidate_rewards": reward["candidate_rewards"][index],
                "local_reward": reward["candidate_rewards"][index],
                "joint_reward": reward["response_rewards"][index],
                "local_advantages": reward["local"][index],
                "joint_advantages": reward["joint"][index],
                "credit_coefficients": coefficients["coefficients"], "credit_receipt": coefficients,
                "bool_union_mask": union_mask,
                "actual_loss_mask": [0] * len(request["token_ids"]) + union_mask,
                "root_turns": [root_turn], "source_record_path": str(
                    ROLLOUT / "outputs/attempt-001/calls" / f"{key}.json"),
                "source_record_sha256": study.sha(ROLLOUT / "outputs/attempt-001/calls" / f"{key}.json")})
    assert len(episodes) == 64 and len(group_receipts) == 16
    active_groups = sum(any(any(value != 0 for value in row) for row in group["local_advantages"])
                        for group in group_receipts)
    differing_groups = sum(group["credit_modes_differ"] for group in group_receipts)
    full_valid_variable = sum(group["sample_valid"] == [True] * 4 and
        any(len({group["candidate_rewards"][i][j] for i in range(4)}) > 1
            for j in range(group["candidate_count"])) for group in group_receipts)
    assert active_groups >= 2 and differing_groups >= 1 and full_valid_variable >= 2
    active_by_mode = {}
    for mode in ("local", "joint"):
        active_by_mode[mode] = any(
            any(coeff[j] * row[mode + "_advantages"][j] != 0
                for j in range(row["candidate_count"]))
            for row in episodes for coeff in row["credit_coefficients"])
    assert all(active_by_mode.values())
    source_pins = {str(path): study.sha(path) for path in
        [ROLLOUT / "CPU_READY.json", terminal_path, result_path, study.INPUTS, study.HOST,
         ROLLOUT / "diagnostics.py", ROOT / "credit.py"]}
    source_pins.update({row["source_record_path"]: row["source_record_sha256"] for row in episodes})
    payload = {"schema": "b05-vector-credit-shared64-input-v1", "episodes": episodes,
        "groups": group_receipts, "denominator": 64, "G": 4,
        "credit_modes": ["local", "joint"], "same_actions_for_both_modes": True,
        "per_candidate_weight": "1/candidate_count", "token_TIS_cap": 2.0,
        "invalid_policy": "zero candidate/response reward and zero token mask; retained /64 and peer RLOO",
        "source_pins": source_pins}
    with OUT.open("x") as stream:
        json.dump(payload, stream, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    receipt = {"schema": "b05-vector-credit-data-qualification-v1",
        "source_rollout_ready_sha256": study.sha(ROLLOUT / "CPU_READY.json"),
        "source_terminal_sha256": study.sha(terminal_path), "source_result_sha256": study.sha(result_path),
        "train_inputs_sha256": study.sha(OUT), "episodes": 64, "groups": 16,
        "active_local_groups": active_groups, "credit_modes_differ_groups": differing_groups,
        "full_valid_variable_groups": full_valid_variable,
        "sufficient_observed_contrast_gate": {"active_groups_min": 2,
            "differing_groups_min": 1, "full_valid_variable_groups_min": 2},
        "held_calls_executed": 0, "optimizer_steps": 0, "GPU_calls": 0, "model_calls": 0}
    with RECEIPT.open("x") as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2, allow_nan=False); stream.write("\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    build()
