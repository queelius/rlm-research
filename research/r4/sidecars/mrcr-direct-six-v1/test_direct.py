from direct import request_body


def test_direct_receives_full_context_question_and_no_tools():
    body = request_body("FULL CONTEXT", "EXACT QUESTION", "frozen-model", 970260100)
    assert body["messages"] == [{"role": "user", "content": "FULL CONTEXT\n\nEXACT QUESTION"}]
    assert body["model"] == "frozen-model"
    assert body["max_tokens"] == 2048
    assert body["temperature"] == 0
    assert "tools" not in body
    assert "response_format" not in body
