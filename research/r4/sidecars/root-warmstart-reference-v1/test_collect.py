def test_complete_native_final_only_and_attempts_not_completions():
    import collect as c
    trace=dict(root_reply='Answer: 3');capture=dict(status='returned',native_response=dict(finish_reason='stop',message=dict(content='Answer: 3')))
    assert c.terminal(trace,capture,3)['reward']==1
    capture['native_response']['message']['content']='Answer: 4'
    assert c.terminal(trace,capture,3)['reward'] is None
    rows=[dict(physical_request_attempt=True,status='error',native_wire_response=dict(body='{"error":"context length"}')),dict(physical_request_attempt=False,status='error',pretransport_rejected=True)]
    result=c.cost(rows)
    assert result['physical_request_attempts']==1 and result['returned_native_completions']==0 and result['pretransport_rejected']==1
    rows.append(dict(physical_request_attempt=True,status='error',native_wire_response=dict(body='{"choices":[{"token_ids":[1],"finish_reason":"stop"}]}')))
    assert c.cost(rows)['returned_native_completions']==1
