"""Focused frozen-input and unchanged-native-interface checks."""
from collections import Counter
import ct_study as s
import ct_protocol as p

def test_exact_paired_inventory_source_baselines():
    contexts={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};rows=s.read(s.ROOT/'inputs/FREE_PLAN.json');plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');host=s.read(s.ROOT/'inputs/HOST_GOLD.json');groups=s.read(s.ROOT/'inputs/GROUPS.json');receipt=s.read(s.ROOT/'inputs/PROVENANCE.json')
    selected=[g for c in groups for g in c['group_ids']]
    assert len(contexts)==8 and len(rows)==48 and len(plan['full'])==96 and plan['first_action']==[]
    assert len(set(selected))==len(selected)==128 and set(selected)<=set(receipt['eligible_group_ids'])
    assert not set(selected)&set(receipt['excluded_positive_groups'])
    assert len({r['seed'] for r in rows})==48 and not receipt['observed_seed_collision']
    for policy in plan['policy_order']:assert [r['coordinate'] for r in plan['full'] if r['policy']==policy]==rows
    for context in contexts.values():
        assert len(context['records'])==16 and Counter(r['user'] for r in context['records'])==dict.fromkeys(p.USERS,4)
        assert all(set(r)=={'id','user','weight','text'} and 1<=r['weight']<=7 for r in context['records'])
    for row in rows:
        records=contexts[row['context_id']]['records'];labels=host[row['context_id']]['labels']
        assert p.answer(records,labels,row)==p.enumerated_answer(records,labels,row)==host[row['context_id']]['answers'][row['family']]
    for panel in ('primitive','composition'):
        hist=Counter(s.answer(contexts[r['context_id']]['records'],host[r['context_id']]['labels'],r) for r in rows if r['panel']==panel)
        baseline=s.read(s.ROOT/'inputs/BASELINES.json')[panel]
        assert baseline['answer_histogram']=={str(k):v for k,v in hist.items()} and baseline['zero_correct']==hist[0]

def test_same_qualified_interface_only_task_text_changes():
    assert s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json')==s.read(s.OLD/'inputs/NATIVE_TEMPLATE.json')
    for policy in ('sft6','sft24'):
        baseline=s.dr.binding(policy);actual=s.binding(policy)
        assert actual['models']==baseline['models'] and actual['role_map']==baseline['role_map']
        assert actual['campaign_policy']==baseline['campaign_policy'] and actual['fixed_child']==baseline['fixed_child']
    native=s.read(s.ROOT/'CPU_INPUT_NATIVE.json')
    assert len(native['rows'])==48 and native['max_prefix']+2048<=8192
    assert all(r['gold_independent'] and r['policy_independent'] for r in native['rows'])
