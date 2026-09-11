"""Recheck retained CPU captures with final diagnostic names; no providers or runtimes."""
import json
import experiment as e
import results

root=e.ROOT/'qualification-attempt-002'
prior=e.c.read(root/'RESULT.json')
policies=e.c.read(e.old.ROOT/'SPEC.json')['policies']
proofs=[]
for index,case in enumerate(prior['cases']):
    path=root/f"{index:02d}-{case['arm']}-{case['fixture']}"
    episode=e.c.read(path/'EPISODE.json')
    proof=results.corroborate(episode,path,e.binding_for(policies[case['weight']]))
    assert proof['root_calls']==2 and proof['child_calls']==1
    if case['arm']=='unchanged':
        assert proof['helper_uptake'] is False
    else:
        assert proof['helper_uptake'] is True
        assert proof['matching_child_model_requests']==proof['corroborated_helper_request_claims']==1
        assert len(proof['results'])==1
        item=proof['results'][0]
        assert item['map_valid']==(case['fixture']=='valid')
        assert item['map_report_matches'] and item['native_terminal_matches']==1
        assert item['receipt_access_claim']==(case['arm']=='restored_receipt')
    proofs.append({'arm':case['arm'],'fixture':case['fixture'],'proof':proof})
e.c.write_once(e.ROOT/'SAVED_CAPTURE_CHECK.json',{'cases':proofs,'additional_model_calls':0,'additional_provider_calls':0,
    'results_source_sha256':e.c.file_hash(e.ROOT/'results.py'),'source_result_sha256':e.c.file_hash(root/'RESULT.json'),
    'meaning':'Exact retained seven-case CPU wire captures checked under final metadata and source-binding logic.'})
print(json.dumps({'rechecked_cases':len(proofs),'additional_provider_calls':0,'model_calls':0}))
