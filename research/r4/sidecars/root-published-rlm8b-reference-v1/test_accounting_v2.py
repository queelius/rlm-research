"""Additive regressions: late physical ledgers and genuine current block finals."""
import importlib,copy,json
import rv_study as s,rv_protocol as p

def existing_with_late_calls(tmp_path):
    row=p.plan()[0];directory=tmp_path/'base/rollout/episodes'/row['id']
    embedded=dict(role='root',index=0,physical_attempt=True,native_verified=True,usage=dict(prompt_tokens=2,completion_tokens=3,total_tokens=5))
    episode=dict(coordinate=row,score=p.score(None,False,p.gold(row)),terminal=dict(final=None,error=dict(type='Unreturned')),outstanding_requests=2,calls=[embedded,copy.deepcopy(embedded),dict(role='child',index=4,physical_attempt=True,native_verified=False,usage=None)])
    s.write(directory/'RESULT.json',episode)
    s.write(directory/'calls/root-000/RESULT.json',embedded)
    s.write(directory/'calls/child-000/REQUEST.json',dict(body='{}'))
    s.write(directory/'calls/child-000/RESPONSE.json',dict(status=200,body=json.dumps(dict(usage=dict(prompt_tokens=11,completion_tokens=7,total_tokens=18)))))
    s.write(directory/'calls/child-001/REQUEST.json',dict(body='{}'))
    return row,episode

def test_existing_episode_late_calls_and_duplicate_identity(tmp_path):
    row,episode=existing_with_late_calls(tmp_path)
    owner=importlib.import_module('owner_v2');result=owner.harvest(tmp_path,'base')[0]
    assert len(result['calls'])==4
    assert {(c['role'],c['index']) for c in result['calls']}=={('root',0),('child',0),('child',1),('child',4)}
    assert sum(c['physical_attempt'] for c in result['calls'])==4
    assert sum((c.get('usage') or {}).get('completion_tokens',0) for c in result['calls'])==10
    assert result['score']==episode['score'] and result['terminal']==episode['terminal'] and result['outstanding_requests']==2
    assert result['call_reconciliation']['duplicate_embedded_identities']==1

def test_v1_reproduces_omission(tmp_path):
    import owner
    existing_with_late_calls(tmp_path);calls=owner.harvest(tmp_path,'base')[0]['calls']
    assert len(calls)==3 and not any(c['role']=='child' and c['index']==0 for c in calls)

def block_result(prior=False):
    text="```repl\nanswer='Answer: 3'\nFINAL_VAR('answer')\n```";code="answer='Answer: 3'\nFINAL_VAR('answer')"
    observation=dict(kind='observation',value=dict(code=code,stdout='',stderr='',final_answer='Answer: 3'))
    events=[observation]
    if prior:events.append(dict(kind='iteration',value=dict(response='earlier',final=None,code=[code])))
    events.append(dict(kind='iteration',value=dict(response=text,final='Answer: 3',code=[code])))
    return dict(terminal=dict(final='Answer: 3',error=None),events=events),[dict(role='root',index=0,native_verified=True,content=text)]

def test_in_block_FINAL_VAR_current_only():
    import collect
    patched=importlib.import_module('collect_v2');result,calls=block_result()
    assert not collect.final_capture(result,calls,0)
    assert patched.final_capture(result,calls,0)
    stale,root=block_result(True);assert not patched.final_capture(stale,root,0)
    assert not patched.final_capture(result,calls,1)

def test_v2_entry_wires_exact_collector_without_changing_science():
    owner=importlib.import_module('owner_v2')
    argv=owner.collector_argv('base',123.)
    assert argv[1]==str(s.ROOT/'collect_v2.py')
    assert owner.validate_argv(argv)==dict(policy='base',deadline=123.)
    assert owner.original.collector_argv is owner.collector_argv
    assert owner.original.harvest is owner.harvest
