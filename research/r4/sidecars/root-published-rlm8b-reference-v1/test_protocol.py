"""Catch selected-data changes, hidden-label leaks and NULL zero-imputation."""
import copy
import rv_protocol as p

def test_full_fixed_panel_and_pairing():
    rows=p.plan();assert len(rows)==48
    assert {r['policy'] for r in rows}=={'base','rlm'}
    for i in range(24):
        a,b=rows[i],rows[i+24]
        assert (a['context_id'],a['family'],a['seed'])==(b['context_id'],b['family'],b['seed'])
        assert a['seed']==2026091101+i
    assert sum(p.gold(r)>0 for r in rows[:24])==23
    assert sum(p.gold(r)==0 for r in rows[:24])==1

def test_real_operator_truth_and_label_blind_task(monkeypatch):
    records=[dict(id='qa',user='u0',text='where',weight=3),dict(id='qb',user='u1',text='who',weight=7),dict(id='qc',user='u0',text='where else',weight=2)]
    q=dict(users=['u0','u1'],target='location')
    labels={'qa':'location','qb':'human being','qc':'location'}
    assert p.answer(records,labels,dict(q,operator='count'))==2
    assert p.answer(records,labels,dict(q,operator='distinct'))==1
    assert p.answer(records,labels,dict(q,operator='weight'))==5
    row=p.plan()[0];before=p.task(row)
    other=copy.deepcopy(p.host())
    for context in other.values():
        context['labels']={k:('location' if i%2 else 'entity') for i,k in enumerate(context['labels'])}
    monkeypatch.setattr(p,'host',lambda:other)
    assert p.task(row)==before
    assert set(before)=={'context','query'} and 'labels' not in before['context']

def test_strict_observed_invalid_separate_from_NULL():
    assert p.score('Answer: 3',True,3)==dict(available=True,format_ok=True,value=3,correct=True)
    assert p.score('Answer: 3 because yes',True,3)==dict(available=True,format_ok=False,value=None,correct=False)
    assert p.score(None,False,0)==dict(available=False,format_ok=None,value=None,correct=None)
