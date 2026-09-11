import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
import pytest


def study():
    assert (Path(__file__).parent/'study.py').exists(), 'cue-order implementation absent'
    import study as s
    return s


def test_dispatch_keeps_order_pairs_adjacent_and_reverses_first_exposure():
    s=study();d=s.build_design(s.build_data())
    assert len(d['plan'])==len({r['id'] for r in d['plan']})==48
    assert [(c['dataset'],c['index']) for c in d['contexts']]==[('trec',0),('trec',1),('sst2',4),('sst2',5)]
    assert set(Counter((r['dataset'],r['arm'],r['field_order']) for r in d['plan']).values())=={4}
    first={}
    for a,b in zip(d['plan'][::2],d['plan'][1::2],strict=True):
        assert {a['field_order'],b['field_order']}=={'tag_first','label_first'}
        assert all(a[k]==b[k] for k in ('context_index','arm','seed','repeat'))
        first[a['context_index'],a['arm'],a['repeat']]=a['field_order']
    assert all(first[c,a,0]!=first[c,a,1] for c in [0,1,4,5] for a in s.ARMS)


def test_request_pair_changes_ordered_grammar_only_not_messages():
    s=study();d=s.build_design(s.build_data())
    for a,b in zip(d['plan'][::2],d['plan'][1::2],strict=True):
        x,y=s.make_request(d,a),s.make_request(d,b)
        assert {k:v for k,v in x.items() if k!='structured_outputs'}=={k:v for k,v in y.items() if k!='structured_outputs'}
        assert 'the keys tag and label' in x['messages'][1]['content']
        assert s.ordered_digest(x)!=s.ordered_digest(y)
        assert list(x['structured_outputs']['json']['prefixItems'][0]['properties'])==list(s.ORDERS[a['field_order']])


def test_raw_order_is_enforced_without_repair_and_displayed_gold_is_primary():
    s=study();d=s.build_design(s.build_data())
    for order in ['tag_first','label_first']:
        row=next(r for r in d['plan'] if r['field_order']==order and r['arm']=='ordinal_tag')
        gold=d['batches'][row['batch_id']]['gold'];values=[]
        for i,r in enumerate(gold['records'],1):
            v={'tag':f'p{i:04d}','label':r['gold_label']};values.append({k:v[k] for k in s.ORDERS[order]})
        scored=s.score_labels(json.dumps(values),gold)
        assert scored['schema_valid'] and scored['strict_correct']==64
        wrong=[dict(reversed(list(v.items()))) for v in values]
        bad=s.score_labels(json.dumps(wrong),gold)
        assert not bad['schema_valid'] and bad['strict_correct']==0 and bad['aligned_records']==0
        assert bad['parse_status']=='wrong_physical_key_order'
        bad=deepcopy(values);bad[0]['extra']=1
        assert not s.score_labels(json.dumps(bad),gold)['schema_valid']
        assert not s.score_labels(json.dumps(values[:-1]),gold)['schema_valid']
        raw=json.dumps(values).replace('"p0001"','"p0001", "tag": "p0001"',1)
        assert not s.score_labels(raw,gold)['schema_valid']


def test_previous_record_diagnostic_is_secondary_and_first_item_has_no_previous():
    s=study()
    gold={'records':[{'id':'q9876','gold_label':'A'},{'id':'q8888','gold_label':'B'},{'id':'q7777','gold_label':'A'}],
          'arm':'meaningful_tag','source_prefix':'q','labels':['A','B'],'field_order':'label_first'}
    raw='[{"label":"A","tag":"q9876"},{"label":"A","tag":"q8888"},{"label":"B","tag":"q7777"}]'
    score=s.score_labels(raw,gold);diag=score['previous_record_diagnostic']
    assert score['strict_correct']==1 and diag['previous_correct']==2 and diag['positions']==2
    assert diag['first_item_correct']==1 and diag['first_item_previous_correct'] is None
    assert diag['multiset_chance_expected_matches']==1 and diag['primary_replaced'] is False


def test_null_invalid_and_order_interactions_remain_separate():
    s=study();d=s.build_design(s.build_data());row=d['plan'][0];gold=d['batches'][0]['gold']
    assert s.score_coordinate(d,row,[])['strict_correct_assignments'] is None
    null={'coordinate':row,'score':None,'raw_response':None,'finish_reason':None,'started':0,'ended':1,'model_called':True,'status':'infrastructure_error'}
    assert s.score_coordinate(d,row,[null])['strict_correct_assignments'] is None
    invalid={**null,'score':s.score_labels('[]',gold),'raw_response':{'choices':[{'message':{'content':'[]'}}]},'status':'completed'}
    assert s.score_coordinate(d,row,[invalid])['strict_correct_assignments']==0
    out=s.summarize(d,[])
    assert len(out['cells'])==12 and len(out['order_interactions'])==8
    assert all(r['tag_first_minus_label_first_meaningful_minus_ordinal'] is None for r in out['order_interactions'])


def test_owned_preserves_cleanup_reserve_and_stops_after_work_deadline():
    assert (Path(__file__).parent/'owned.py').exists(), 'owned wrapper absent'
    import owned
    assert owned.work_deadline(100)==880
    assert owned.collection_command_cap(100,101)==630
    assert owned.collection_command_cap(100,879)==1
    with pytest.raises(TimeoutError): owned.collection_command_cap(100,880)
