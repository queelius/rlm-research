import study
def test_fixed_eight_calls_and_native_bodies():
    calls=study.calls();assert len(calls)==8 and {x['kind'] for x in calls}=={'direct','oracle_exact_report_synthesis'}
    assert [x['seed'] for x in calls]==[202609271000,202609271015,202609271016,202609271031,202609271032,202609271047,202609271048,202609271063]
    root=study.roots()[0];call=next(x for x in calls if x['root_id']==root['root_id'] and x['kind']=='direct');prompt=study.contract().clarify(call,root['direct_prompt']);body=study.request_body(prompt,call['seed'],call['max_tokens'])
    assert body['model']==study.MODEL_ALIAS and body['sampling_params']=={'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'max_tokens':1024,'seed':call['seed'],'logprobs':1}
    decoded=study.tokenizer().decode(body['token_ids'],skip_special_tokens=False);assert '<think>' not in decoded and 'Output-contract clarification:' in prompt
def test_exact_cached_model_binding_and_source_grader():
    b=study.binding();assert b['adapter'] is None and b['checkpoint']['path']==str(study.MODEL) and b['checkpoint']['revision']=='b968826d9c46dd6066d109eabc6255188de91218'
    root=study.roots()[0];host=study.host_by_root()[root['root_id']];assert study.score_root(host['oracle_synthesis_prompt'],root['safe_root'],host['exact_child_reports'])['primary_metric']=='true_source_root_correctness'
