import ast

import owner_v2
import study
import study_v2


class Tokenizer:
    def decode(self, token_ids, skip_special_tokens=True):
        assert token_ids == [42]
        assert skip_special_tokens is True
        return '{"fixture-id": "numeric value"}'


def test_complete_collector_study_surface_and_native_response_record():
    # Regression: V1 omitted this late-read collector field.
    assert not hasattr(study, "CHILD_ALIAS")
    tree = ast.parse((study_v2.C32 / "owner.py").read_text())
    required = {node.attr for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "study"}
    missing = sorted(name for name in required if not hasattr(study_v2, name))
    assert missing == []
    collector = owner_v2.build()
    row = {"call_id": "fixture", "dataset": "trec", "start": 0,
        "ids": ["fixture-id"], "body": {"sampling_params": {"seed": 7}}}
    response = {"request_id": "fixture-provider-id", "model": study_v2.CHILD_ALIAS,
        "choices": [{"token_ids": [42], "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4,
            "prompt_tokens_details": {"cached_tokens": 0}}}
    normalized = collector.response_record(row, response, Tokenizer(), 10.0, 11.0)
    assert normalized["status"] == "returned_valid"
    assert normalized["prediction"] == {"fixture-id": "numeric value"}
    assert normalized["model"] == study_v2.CHILD_ALIAS
