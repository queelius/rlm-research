import copy
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parent


def module():
    assert (ROOT/'analyze.py').exists(),'quoted-relation analyzer absent'
    spec=importlib.util.spec_from_file_location('quoted_relation_audit_fixture',ROOT/'analyze.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def test_wrong_person_valid_quote_is_not_verified_as_true():
    m=module();paragraphs=[{'idx':2,'title':'Mayor','paragraph_text':'Jerome died in Lexington.'}]
    raw={'relations':[{'subject':'Anne Marie','relation':'died in','object':'Lexington','paragraph_id':2,'quote':'Jerome died in Lexington.'}],'missing_links':[]}
    parsed=m.parse_report({'authenticated':True,'decoded_text':m.json.dumps(raw)},paragraphs)
    assert parsed['valid'] and parsed['quote_substrings_verified']
    assert parsed['relation_truth_verified'] is False
    raw['relations'][0]['quote']='Anne Marie died in Lexington.'
    assert not m.parse_report({'authenticated':True,'decoded_text':m.json.dumps(raw)},paragraphs)['valid']


@pytest.mark.parametrize('index',[0,1,2])
def test_real_native_fixture_preserves12_cached_controls_and_raw4_on_invalid_report(index):
    m=module()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(m.s.MODEL,local_files_only=True)
    fixture=m.SIDE/('cpu-fixture-001/test_actual_owner_entrypoint_k'+str(index))
    report=m.inspect_attempt(fixture,tok)
    assert report['new_authenticated_calls']==report['new_exact_prefixes']==2
    assert report['baseline_authenticated_calls']==report['baseline_exact_prefixes']==12
    assert report['integrity_issues']==[] and len(report['questions'])==12
    assert report['arms']['direct']['available']==12 and report['arms']['relations']['available']==1
    assert report['arms']['relations']['unavailable']==11
    assert report['new_physical_cost']['physical_started']==2
    q=report['questions'][0]
    assert q['final_source_payload_exact'] and q['baseline_source_payload_exact'] and q['final_seed_matches_baseline']
    assert q['parsed_report']['model_error'] is (index!=0)


def test_changed_final_source_is_detected_independently():
    m=module()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(m.s.MODEL,local_files_only=True)
    fixture=m.SIDE/'cpu-fixture-001/test_actual_owner_entrypoint_k0'
    report=m.inspect_attempt(fixture,tok);item=m.s.selected()[0]
    local={v['role']:copy.deepcopy(v) for v in report['new_calls'] if v['record_id']==item['record_id']}
    payload,instruction=m.payload(local['relations']['prompt']);payload['evidence']=payload['evidence'][:-1]
    local['relations']['prompt'][1]['content']=m.json.dumps(payload)+'\n\n'+instruction
    baseline=next(v for v in report['baseline_calls'] if v['record_id']==item['record_id'])
    q=m.inspect_question(item,local,baseline,fixture)
    assert 'final_source_payload' in q['issues'] and not q['final_source_payload_exact']
