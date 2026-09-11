"""Material comparison seams; no model calls."""
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
import pytest


def study():
    assert (Path(__file__).parent/'study.py').exists(), 'approved AG96 study not implemented'
    import study as s
    return s


def test_exact_groups_display_numerals_and_96_counterbalanced_weight_pairs():
    s=study();data=s.build_data();d=s.build_design(data)
    assert len(data['contexts'])==4 and len({r['group_id'] for c in data['contexts'] for r in c['records']})==256
    proof=s.read(s.FEASIBILITY)
    for c,p in zip(data['contexts'],proof['contexts'],strict=True):
        assert [c['records'][i]['group_id'] for i in c['presentations'][0]]==p['source_group_ids_in_display_order']
        assert [c['disjoint_values_by_rank'][i] for i in c['presentations'][0]]==p['source_numbers_in_display_order']
        assert all(v>999 and not 1<=v%1000<=64 for v in c['disjoint_values_by_rank'])
        assert not s.factorial.affine_sequence(c['disjoint_values_by_rank'])
    assert len(d['plan'])==96 and len({r['id'] for r in d['plan']})==96
    assert set(Counter((r['weight'],r['source_prefix'],r['arm']) for r in d['plan']).values())=={8}
    for a,b in zip(d['plan'][::2],d['plan'][1::2],strict=True):
        assert {a['weight'],b['weight']}=={'original','old_sft'}
        assert all(a[k]==b[k] for k in ('context_index','repeat','source_prefix','arm','seed'))


def test_matched_bodies_change_only_weight_and_preserve_complete_news():
    s=study();d=s.build_design(s.build_data())
    for a,b in zip(d['plan'][::2],d['plan'][1::2],strict=True):
        x,y=s.make_request(d,a),s.make_request(d,b)
        assert x['model']!=y['model']
        assert {k:v for k,v in x.items() if k!='model'}=={k:v for k,v in y.items() if k!='model'}
        user=x['messages'][1]['content']
        assert user.startswith('Classify the main topic of each news text.\n')
        records=d['batches'][a['batch_id']]['gold']['records']
        assert json.loads(user.split(s.INPUT_MARKER)[1])=={r['id']:r['question'] for r in records}
        assert 'human being:' not in user and 'movie-review' not in user
        assert 'source_row_index' not in user and 'gold_label' not in user


def test_displayed_alignment_never_source_numeric_rescue_and_invalid_schema():
    s=study();d=s.build_design(s.build_data())
    row=next(r for r in d['plan'] if r['arm']=='ordinal_tag')
    gold=d['batches'][row['batch_id']]['gold']
    values=[{'tag':tag,'label':r['gold_label']} for tag,r in zip(s.expected_tags(gold['records'],row['arm'],row['source_prefix']),gold['records'],strict=True)]
    assert s.score_labels(json.dumps(values),gold)['strict_correct']==64
    wrong=deepcopy(values);wrong[0]['label']='TREC'
    assert not s.score_labels(json.dumps(wrong),gold)['schema_valid']
    wrong=deepcopy(values);wrong[0]['tag']=gold['records'][0]['id']
    assert not s.score_labels(json.dumps(wrong),gold)['schema_valid']
    assert not s.score_labels(json.dumps(values[:-1]),gold)['schema_valid']
    assert not s.score_labels('[{"tag":"p0001","tag":"p0001","label":"World"}]',gold)['schema_valid']


def test_unrun_infra_and_complete_invalid_are_distinct():
    s=study();d=s.build_design(s.build_data());row=d['plan'][0];gold=d['batches'][row['batch_id']]['gold']
    assert s.score_coordinate(d,row,[])['strict_correct_assignments'] is None
    null={'coordinate':row,'score':None,'raw_response':None,'finish_reason':None,'started':0,'ended':1,'model_called':True,'status':'infrastructure_error'}
    assert s.score_coordinate(d,row,[null])['strict_correct_assignments'] is None
    invalid={**null,'score':s.score_labels('[]',gold),'raw_response':{'choices':[{'message':{'content':'[]'}}]},'status':'completed'}
    score=s.score_coordinate(d,row,[invalid])
    assert score['strict_correct_assignments']==0 and score['aligned_records']==0


def test_weight_interaction_is_per_context_seed_prefix_not_pooled_labels():
    s=study();d=s.build_design(s.build_data());out=s.summarize(d,[])
    assert len(out['cells'])==12 and len(out['weight_interactions'])==16
    assert all(x['old_minus_original_meaningful_minus_ordinal'] is None for x in out['weight_interactions'])
    assert out['inference_context_clusters']==4
