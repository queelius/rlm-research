import copy
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parent


def module():
    assert (ROOT/'analyze.py').exists(),'flexible-allocation analyzer absent'
    spec=importlib.util.spec_from_file_location('flexible_analysis_fixture',ROOT/'analyze.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


@pytest.mark.parametrize('fixture_index',[0,1,2])
def test_saved_native_entrypoint_fixture_retains_all12_and_invalid_branch_semantics(fixture_index):
    m=module()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(m.s.MODEL,local_files_only=True)
    fixture=m.SIDE/('cpu-fixture-001/test_current_owner_collector_e'+str(fixture_index))
    report=m.inspect_attempt(fixture,tok)
    assert report['authenticated_calls']==report['exact_prefixes']==5
    assert report['integrity_issues']==[] and len(report['questions'])==12
    assert report['arms']['fixed']['available']==report['arms']['flexible']['available']==1
    assert report['arms']['fixed']['unavailable']==11
    assert report['physical_cost']['physical_started']==5
    assert report['arms']['fixed']['natural_cost']['physical_started']==3
    assert report['arms']['flexible']['natural_cost']['physical_started']==4
    q=report['questions'][0]
    assert q['evidence_bindings_exact'] and q['paired_final_seed_equal']
    if fixture_index==0:
        assert q['half_allocation']=={'fixed':[2,2],'flexible':[4,0]}
        assert len(q['candidate_ids'])==8
    elif fixture_index==1:
        assert q['shared_selector_model_error'] and q['selected_ids']=={'fixed':[],'flexible':[]}
    else:
        assert q['planner_model_error'] and len(q['selected_ids']['fixed'])==4 and q['selected_ids']['flexible']==[]


def test_replacing_fixed_sources_with_planner_sources_is_detected():
    m=module()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(m.s.MODEL,local_files_only=True)
    fixture=m.SIDE/'cpu-fixture-001/test_current_owner_collector_e0'
    report=m.inspect_attempt(fixture,tok);item=m.s.selected()[0]
    local={v['role']:copy.deepcopy(v) for v in report['calls'] if v['record_id']==item['record_id']}
    local['fixed']['prompt']=copy.deepcopy(local['flexible']['prompt'])
    q=m.inspect_question(item,local,fixture)
    assert 'fixed_payload' in q['issues'] and not q['evidence_bindings_exact']


def test_four_ranked_ids_reject_bad_length_duplicates_and_other_half():
    m=module();half=[{'idx':i,'title':str(i),'paragraph_text':'text'} for i in range(4)]
    good=m.parse_selection({'authenticated':True,'decoded_text':'{"paragraph_ids":[3,2,1,0]}'},half)
    assert good['valid'] and good['ids']==[3,2,1,0]
    for text in ('{"paragraph_ids":[0,1]}','{"paragraph_ids":[0,1,2,99]}','{"paragraph_ids":[0,1,2,2]}'):
        bad=m.parse_selection({'authenticated':True,'decoded_text':text},half)
        assert bad['model_error'] and not bad['valid'] and bad['ids']==[]
