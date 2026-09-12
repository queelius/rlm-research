import json

import owner
import study


class Tokenizer:
    def __init__(self, text): self.text = text
    def decode(self, ids, skip_special_tokens=True):
        assert ids == [42] and skip_special_tokens is True
        return self.text


def test_exact_singleton_schedule_decoder_and_authenticated_bindings():
    rows = study.schedule(); assert len(rows) == 256
    assert all(row["batch_size"] == len(row["ids"]) == 1 for row in rows)
    row = rows[0]; identifier = row["ids"][0]
    label = study.size().source().panel()[3]["labels"][identifier]
    raw = {"request_id": "fixture-provider-id", "model": study.CHILD_ALIAS,
        "choices": [{"token_ids": [42], "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(row["body"]["token_ids"]), "completion_tokens": 1,
            "total_tokens": len(row["body"]["token_ids"])+1, "prompt_tokens_details": {"cached_tokens": 0}}}
    normalized = study.validator().response_record(row, raw,
        Tokenizer(json.dumps({identifier: label})), 10.0, 11.0)
    assert normalized["status"] == "returned_valid" and normalized["prediction"] == {identifier: label}
    c32, reference = study.binding("c32"), study.binding("reference_step4")
    assert c32["role_map"] == reference["role_map"]
    alias = study.CHILD_ALIAS
    assert c32["models"][alias]["adapter_sha256"] == "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
    assert reference["models"][alias]["path"].endswith("checkpoint-0004")
    assert reference["models"][alias]["adapter_sha256"] != c32["models"][alias]["adapter_sha256"]


def test_owner_summary_keeps_wrong_and_unavailable_separate():
    rows=study.schedule();gold=study.size().source().panel()[3]
    identifier=rows[0]["ids"][0]
    calls=[{"call_id":rows[0]["call_id"],"dataset":rows[0]["dataset"],"ids":[identifier],
        "status":"returned_valid","prediction":{identifier:"not-the-gold"},"prompt_tokens":2,
        "completion_tokens":1,"cached_prompt_tokens":0,"wall_seconds":.1}]
    result=owner.summarize("c32",calls,rows,gold);metric=result["datasets"][rows[0]["dataset"]]
    assert metric["wrong"] == 1 and metric["unavailable"] == 127 and metric["correct"] == 0
