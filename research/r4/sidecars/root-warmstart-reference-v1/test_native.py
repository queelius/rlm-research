def test_native_task_has_no_extra_role_or_evidence_and_explicit_action_cap(monkeypatch):
    import study as s,protocol as p,native as n
    data=p.build();row=data['PLAN.json'][0];context=next(c for c in data['PUBLIC.json'] if c['id']==row['context_id']);query=data['QUERIES.json'][row['task_name']]['question']
    task=n.task(context,query,row)
    assert task.data.prompt==s.qnative().prompt(context,query)
    expected=n.expected(task,row);template=s.read(s.SIDE/'root-corrective-reduction-sft-v1/inputs/NATIVE_TEMPLATE.json')
    assert expected['messages'][0]==template['system']
    assert expected['tools_ordered_json']==template['tools_ordered_json']
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','cpu-fixture-not-credential')
    interface=n.interface(s.ROOT/'CPU-native-config-only')
    endpoint=dict(url='http://127.0.0.1:1/v1',model='CPU',renderer_model=str(s.qnative().stack().prior.BASE),api_key_env='CPU_KEY')
    assert n.make_context(interface,endpoint,row).sampling.max_tokens==2048
