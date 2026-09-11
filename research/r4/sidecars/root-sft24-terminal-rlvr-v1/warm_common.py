"""Fresh RL cursor over exact SFT24 with unchanged qualified QSR numerics."""
import warm_study as study

SOURCE = study.QSR / "qsr_common.py"
PIN = "4f6a3cd85b95dfb6b005eb47f173b1bda2e84ba2f14e0f4010e327c055fe552d"
with study.aliases({"qsr_study": study}):
    qualified = study.load("warm_qualified_qsr_common", SOURCE, PIN)
c = qualified.c
_authenticate = c.authenticate_policy


def starting_decision():
    policy = study.fixed_start()
    value = study.read(study.ROOT / "START.json")
    if value["policy"] != policy or value["kind"] != "exact_operator_sft24" or not value["fresh_rl_adam"]:
        raise ValueError("starting decision is not exact SFT24 with fresh RL Adam")
    return study.ROOT / "START.json", value, policy


def authenticate_policy(policy):
    if policy["step"] == 0:
        if policy != study.fixed_start():
            raise ValueError("not exact SFT24/fresh Adam0")
    else:
        _authenticate(policy)


def check_generation(generation, policy, optimizer_step):
    if study.digest({key: value for key, value in generation.items() if key != "generation_id"}) != generation["generation_id"]:
        raise ValueError("generation identity")
    if generation["fixed_child_sha256"] != study.CHILD_SHA or generation["previous_policy"] != policy:
        raise ValueError("stale root/child generation")
    if not 1 <= generation["round"] <= 8 or generation["round"] != policy["step"] + 1:
        raise ValueError("fresh RL cursor outside fixed8")
    if optimizer_step != policy["step"] or not generation["round"] <= generation["candidate_window"] <= 8:
        raise ValueError("window/optimizer cursor mismatch")
    return generation["round"]


c.authenticate_policy = authenticate_policy
c.original_policy = study.fixed_start
c.check_generation = check_generation
c.ROOT = study.ROOT
c.SEED = 981731001
c.verify_campaign = study.verify_prepared


def generation(window, policy):
    if not 1 <= window <= 8:
        raise ValueError("fixed eight windows only")
    value = c.generation_identity(study.CAMPAIGN_ID, policy["step"] + 1, policy,
                                  study.digest(study.candidate_plan(window)))
    value["candidate_window"] = window
    value["generation_id"] = study.digest({key: item for key, item in value.items()
                                            if key != "generation_id"})
    check_generation(value, policy, policy["step"])
    return value


def transition(completed, policy, window, new_policy):
    if window != completed + 1 or not 1 <= window <= 8:
        raise ValueError("noncontiguous fixed8 window")
    if new_policy is not None and (new_policy["step"] != policy["step"] + 1
                                   or new_policy["adapter_sha256"] == policy["adapter_sha256"]):
        raise ValueError("real update must advance cursor and weights")
    chosen = policy if new_policy is None else new_policy
    return {"completed_windows": window, "optimizer_steps": chosen["step"],
            "next_window": window + 1, "policy": chosen,
            "decision": "noop" if new_policy is None else "update"}
