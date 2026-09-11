import importlib
import time
import pytest

def test_mechanism_masks_exclude_string_and_numeric_literals():
    import od_study as s
    p=importlib.import_module('od_protocol');n=s.qnative().stack().native;tok=n.renderer()._tokenizer
    code='result = sum(labels[key] == "human being" for key in keys) + 12345\nprint(result)'
    wire=n.tool_action(code);spans,ids=p.target_spans(tok,wire,code)
    assert ids==tok.encode(wire,add_special_tokens=False)+[151645]
    assert sorted(i for v in spans.values() for i in v)==list(range(len(ids)))
    mechanism=tok.decode([ids[i] for i in spans['mechanism']]);literal=tok.decode([ids[i] for i in spans['copied_literals']])
    assert 'sum' in mechanism and 'labels' in mechanism and '12345' not in mechanism and 'human being' not in mechanism
    assert '12345' in literal and 'human being' in literal and not spans['payload']

def test_role_mass_current_action_masks_and_gate():
    l=importlib.import_module('od_learning');p=importlib.import_module('od_protocol')
    def turn(kind):return p.row(kind,[7,8],[9,151645],kind)
    episode={'episode_id':'fixture','turns':{'first_producer':turn('first_producer'),'corrective':turn('corrective'),'terminal':turn('terminal')},'masked_history_turns':[turn('producer_history') for _ in range(3)]}
    weighted=l.weighted_turns(episode,'joint');assert [mass for _,mass in weighted]==[.1125]*4+[.5,.05]
    assert all(t['labels'][:2]==[-100,-100] for t,_ in weighted)
    assert not l.objective_gate([{'mechanism_nll':0.01,'target_nll':1.0} for _ in range(6)])['pass']
    assert l.objective_gate([{'mechanism_nll':0.5,'target_nll':0.5} for _ in range(6)])['pass']
    with pytest.raises(ValueError):l.objective_gate([{'mechanism_nll':.5,'target_nll':.5}]*5)
