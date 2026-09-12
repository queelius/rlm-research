"""Catches accidental cp32 alias or wrapper-export reuse in the cp16 analyzer."""
import importlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def test_actual_cp16_native_fixture_and_independent_paired_coordinates():
    assert (ROOT/'analyze.py').exists(), 'cp16 analyzer not implemented'
    a=importlib.import_module('analyze');core=a.core;c=core.bindings()
    assert c.study.ADAPTED_ALIAS=='Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step16'
    assert hasattr(c,'hooks') and hasattr(c,'original_inspect_trace')
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    fixture=core.SIDE/'cpu-001/test_actual_native_cp16_alias_0'
    raw=json.loads((fixture/'EPISODE.json').read_text())
    native=[json.loads(p.read_text()) for p in sorted((fixture/'native-calls').glob('*-result.json'))]
    item={'episode':raw,'episode_sha256':core.digest(raw),'derived':json.loads((fixture/'DERIVED.json').read_text()),'coordinate':{'id':'CPU_CP16'}}
    tok=AutoTokenizer.from_pretrained(str(c.study.BASE),local_files_only=True)
    value=core.episode(item,native,{'answer':'MARK native cp16 fixture  ','random_string_to_prepend':'MARK'},
                       native[0]['response']['tokens']['prompt_ids'],"print('CPU_CP16_OK')",c,tok,Qwen3Renderer(tok))
    assert value['binary_reward']==1 and value['actual_final_text'] and value['first_teacher_AST_exact']
    assert value['root_actions']==2 and value['child_actions']==0
    assert value['turns'][-1]['bare_semantic_final_span']
    coord={'record_id':'record','repeat':0,'seed':123,'temperature':.5}
    old={**value,'coordinate':coord,'binary_reward':0}
    new={**value,'coordinate':{**coord,'study':'cp16','id':'new-id'}}
    pair=a.pair_sample(old,new)
    assert pair['both_available'] and pair['cp16_win'] and not pair['cp16_loss']
    assert pair['initial_prompt_equal'] and pair['first_action_equal']
