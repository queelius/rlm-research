import json
import pytest

def test_only_output_order_changes_within_pair():
    import protocol_v2 as p
    c=p.contexts()[0]
    rows={r['arm']:r for r in p.plan() if r['context_index']==0}
    for relation in ('wrong','alien','aligned'):
        left=p.request(c,rows[relation+'_tag_first'])
        right=p.request(c,rows[relation+'_label_first'])
        assert left['seed']==right['seed']
        assert p.visible_records(c,relation+'_tag_first')==p.visible_records(c,relation+'_label_first')
        assert left['messages'][1]['content'].replace('tag then label','label then tag')==right['messages'][1]['content']
        l=left['structured_outputs']['json']['prefixItems'][0]
        r=right['structured_outputs']['json']['prefixItems'][0]
        assert list(l['properties'])==['tag','label']
        assert list(r['properties'])==['label','tag']
        assert l['properties']==r['properties']

def test_scorer_honors_declared_order_and_never_repairs():
    import protocol_v2 as p,scoring_v2 as scorer
    c=p.contexts()[0]; tags=p.requested_tags(c)
    vals=[dict(label=r['gold_label'],tag=t) for t,r in zip(tags,c['records'])]
    good=scorer.score({'content':json.dumps(vals)},c,'wrong_label_first')
    assert good['strict_correct']==48 and good['contract_valid']
    wrong=scorer.score({'content':json.dumps(vals)},c,'wrong_tag_first')
    assert wrong['available'] and wrong['strict_correct']==0 and not wrong['contract_valid']
    vals[0]['tag']=tags[1]
    assert scorer.score({'content':json.dumps(vals)},c,'wrong_label_first')['strict_correct']==0
    assert scorer.missing(c)['strict_correct'] is None

def test_scorer_rejects_duplicate_keys_and_nonstring_label():
    import protocol_v2 as p,scoring_v2 as scorer
    c=p.contexts()[0]
    assert scorer.score({'content':'[{"label":"neutral","label":"entailment","tag":"m0"}]'},c,'wrong_label_first')['strict_correct']==0
    vals=[dict(label=r['gold_label'],tag=t) for t,r in zip(p.requested_tags(c),c['records'])]
    vals[0]['label']=[]
    assert scorer.score({'content':json.dumps(vals)},c,'wrong_label_first')['strict_correct']==0

def test_plan_complete_and_same_requested_tags():
    import protocol_v2 as p
    rows=p.plan()
    assert len(rows)==48 and len({r['id'] for r in rows})==48
    for ci,c in enumerate(p.contexts()):
        sub=[r for r in rows if r['context_index']==ci]
        assert {r['arm'] for r in sub}==set(p.ARMS)
        assert {r['seed'] for r in sub}=={982626101+ci}
        assert all(p.expected_tags(c,r['arm'])==p.requested_tags(c) for r in sub)


def test_owner_execution_uses_full_six_arm_plan(tmp_path,monkeypatch):
    import types
    import owner_v2 as owner
    s=owner.s
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES","fixture-assigned-mig")
    monkeypatch.setattr(s,"ATTEMPT",tmp_path/"attempt")
    monkeypatch.setattr(s,"verify",lambda:dict(identity="fixture"))
    original_read=s.read
    monkeypatch.setattr(s,"read",lambda path: owner.p.plan() if str(path).endswith("PLAN_v2.json") else original_read(path))
    monkeypatch.setattr(owner.module,"credential",lambda:{})
    monkeypatch.setattr(owner.module,"binding",lambda:{})
    calls=[]
    def command(stage,label,argv,cap,deadline):
        calls.append(argv)
        s.write(s.ATTEMPT/"rollout/STATUS.json",dict(planned=48,recorded=48))
    runner=types.SimpleNamespace(start_service=lambda *args:None,command=command,release_service=lambda *args:None)
    monkeypatch.setattr(owner.module,"suite",lambda:runner)
    result=owner.execute(s.ATTEMPT)
    assert result["complete"] and result["planned"]==48
    assert len(original_read(s.ATTEMPT/"PLANNED_NULL_ENDPOINTS.json"))==48
    assert len(calls)==1
