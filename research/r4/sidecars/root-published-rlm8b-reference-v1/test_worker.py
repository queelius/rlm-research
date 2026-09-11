"""The real isolated worker must acquire, compute, retrieve and stop."""
import json
import container_runner as cr

def test_actual_isolated_FINAL_VAR(tmp_path):
    calls=[]
    outputs=["```repl\nimport json, os\nprint('host_visible', os.path.exists('/project/alex_phd/repos/rlm/AGENTS.md'))\nrows=[json.loads(x) for x in context.splitlines()]\nlabels=llm_query(context)\nprint(labels)\n```",
             "```repl\npred=json.loads(labels)\nfinal='Answer: '+str(sum(r['weight'] for r in rows if pred[r['id']]=='location'))\nprint(final)\n```","FINAL_VAR(final)"]
    def provider(request):
        calls.append(request)
        content=outputs.pop(0) if request['role']=='root' else '{"qa":"location","qb":"entity"}'
        return dict(content=content,usage=dict(prompt_tokens=11,completion_tokens=7,total_tokens=18))
    task=dict(context='{"id":"qa","text":"Where?","weight":3}\n{"id":"qb","text":"What?","weight":2}\n',query='Sum location weights; return Answer: N',system='Use context and llm_query, then FINAL or FINAL_VAR.')
    result=cr.run(task,tmp_path/'episode',provider,30)
    assert result['terminal']['final']=='Answer: 3'
    assert [x['role'] for x in calls]==['root','child','root','root']
    events=result['events'];assert any(x['kind']=='observation' and 'host_visible False' in x['value']['stdout'] for x in events)
    assert any(x['kind']=='observation' and x['value']['code']=="print(FINAL_VAR('final'))" and x['value']['stdout']=='Answer: 3\n' for x in events)
    assert result['container_released']

def test_actual_isolated_FINAL_and_no_fallback(tmp_path):
    task=dict(context='actual source',query='Return Answer: 2',system='Use FINAL.',max_iterations=1)
    first=cr.run(task,tmp_path/'final',lambda r:dict(content='FINAL(Answer: 2)',usage=dict(prompt_tokens=1,completion_tokens=1,total_tokens=2)),20)
    assert first['terminal']['final']=='Answer: 2'
    seen=[]
    def nofinal(r):seen.append(r);return dict(content='Still thinking.',usage=dict(prompt_tokens=1,completion_tokens=1,total_tokens=2))
    second=cr.run(task,tmp_path/'capped',nofinal,20)
    assert second['terminal']['final'] is None and len(seen)==1
    assert second['terminal']['error']['type']=='NoFinal'
