"""Prospective V2 outcome taxonomy with explicit model-stop allowlists."""

import study


MODEL_BUDGET_STOPS = frozenset(
    {"max_turns", "max_input_tokens", "max_output_tokens", "max_total_tokens"}
)


def classify_outcome(
    *, root_reply, answer, marker, stop_condition, trace_ok, trace_errors,
    returned_root_actions, returned_child_actions, native_mapping_complete
):
    del returned_child_actions
    authenticated = returned_root_actions > 0 and native_mapping_complete
    if trace_errors or not authenticated:
        return {
            "scientifically_available": False,
            "reward": None,
            "failure_class": "infrastructure_unavailable",
        }
    if stop_condition in MODEL_BUDGET_STOPS:
        return {
            "scientifically_available": True,
            "reward": 0.0,
            "failure_class": "model_finite_horizon",
        }
    if stop_condition == "agent_completed":
        if not (trace_ok and isinstance(root_reply, str) and root_reply.strip()):
            return {
                "scientifically_available": True,
                "reward": 0.0,
                "failure_class": "model_invalid_terminal",
            }
        return {
            "scientifically_available": True,
            "reward": study.official_grade()(root_reply, answer, marker),
            "failure_class": None,
        }
    return {
        "scientifically_available": False,
        "reward": None,
        "failure_class": "ambiguous_nonmodel_stop_unavailable",
    }
