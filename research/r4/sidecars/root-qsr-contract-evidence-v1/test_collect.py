def test_cost_keeps_rejection_unknown_and_available_completion():
    import collect as c
    records=[dict(physical_request_attempt=True,status='error'),dict(physical_request_attempt=True,status='returned',native_wire_response=dict(body='{"usage":{"prompt_tokens":12,"completion_tokens":3}}'))]
    value=c.cost(records)
    assert value['physical_request_attempts']==2 and value['returned_native_completions']==1
    assert value['usage']['known']['input']==12 and value['usage']['unknown']['input']==1
    assert value['provider_billing'] is None

def test_authentic_terminal_not_tool_or_mismatched_trace():
    import collect as c
    capture=dict(status='returned',native_response=dict(finish_reason='stop',message=dict(content='Answer: 2',tool_calls=[])))
    assert c.terminal({'root_reply':'Answer: 2'},capture,2)['reward']==1
    assert c.terminal({'root_reply':'Answer: 3'},capture,3)['reward'] is None
    capture['native_response']['message']['tool_calls']=[{'name':'ipython'}]
    assert c.terminal({'root_reply':'Answer: 2'},capture,2)['reward'] is None
