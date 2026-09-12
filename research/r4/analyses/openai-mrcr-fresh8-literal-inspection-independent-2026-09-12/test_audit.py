"""Catch inference of inspection from a correct constant or a later observation."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def test_only_earlier_observed_request_can_be_an_inspection_candidate():
    assert (ROOT/'analyze.py').exists(),'literal inspection analyzer not implemented'
    spec=importlib.util.spec_from_file_location('inspection_audit_test',ROOT/'analyze.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    request='write a email about candy'
    source=[{'role':'user','content':request},{'role':'assistant','content':'TARGET  '}]
    def program(code):return {'message':{'role':'assistant','tool_calls':[{'name':'ipython','arguments':json.dumps({'code':code})}]}}
    def observation(text):return {'message':{'role':'tool','content':text}}
    select=program("request_text = 'write a email about candy'\nprint(request_text)")
    guessed=m.mechanism({'nodes':[select,observation(request)],'root_reply':'TARGET  '},source,'TARGET  ')
    assert guessed['programs'][0]['earlier_request_observation_nodes']==[]
    assert not guessed['observed_before_literal_program_candidate']
    assert guessed['inspection_adjudication']=='UNREVIEWED'
    inspected=m.mechanism({'nodes':[program("print([x['content'] for x in messages if x['role']=='user'])"),
        observation("['write a email about candy']"),select,observation('TARGET  \n')],'root_reply':'TARGET'},source,'TARGET  ')
    assert inspected['programs'][1]['earlier_request_observation_nodes']==[1]
    assert inspected['observed_before_literal_program_candidate']
    assert inspected['inspection_adjudication']=='UNREVIEWED'  # substring/order is not semantic use
    assert inspected['full_gold_stdout'] and not inspected['final_exact']
    assert inspected['final_diff']==[{'op':'delete','gold_interval':[6,8],'final_interval':[6,6],'gold_text':'  ','final_text':''}]
    bad=m.mechanism({'nodes':[program('this is invalid Python !!!')],'root_reply':None},source,'TARGET  ')
    assert not bad['programs'][0]['ast_parseable'] and bad['final_exact'] is None


def test_actual_saved_control_decode_and_new_study_prefix_binding():
    spec=importlib.util.spec_from_file_location('inspection_saved_test',ROOT/'analyze.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    c=m.bindings(m.CONTROL);new=m.bindings(m.SIDE)
    assert c.study.ROOT==m.CONTROL and new.study.ROOT==m.SIDE
    assert c.study.schedule('train')[0]['seed']==new.study.schedule('train')[0]['seed']==202609250000
    assert c.study.input_dir('train')!=new.study.input_dir('train')
    saved=m.CONTROL/'outputs/attempt-001/science'
    item=m.core.read(saved/'episodes/1885ce38d3567426fcd0a1c1386fa699bacba9341125c6a3279aae132223494c.json')
    row=item['coordinate'];gold=m.core.read(c.study.input_dir('train')/'HOST_GOLD.json')[row['record_id']]
    prefix=m.core.read(c.study.input_dir('train')/'PREFIXES.json')[row['id']]['token_ids']
    native=[m.core.read(p) for p in sorted((saved/'native-calls').glob('*-result.json'))]
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    tok=AutoTokenizer.from_pretrained(str(c.study.BASE),local_files_only=True)
    value=m.core.episode(item,native,gold,prefix,None,c,tok,Qwen3Renderer(tok))
    assert value['available'] and value['binary_reward']==1 and value['clean_target_stdout']
    assert value['root_actions']==2 and value['child_actions']==0
