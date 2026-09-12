import analyze as a
import importlib
import sys

def sample(reward,answer,available=True):
    return {'available':available,'binary_reward':reward if available else None,
            'returned_final_sha256':answer,'first_program_sha256':'same-program',
            'first_native_path_sha256':'same-prefix-action','clean_target_stdout':True,
            'failure_category':'returned_exact' if reward else 'copy_difference',
            'actual_final_text':True,'official_score':float(reward)}

def test_fixed_g4_reward_signal_does_not_impute_unknown_or_confuse_last_tool():
    mixed=a.group_summary([sample(1,'a'),sample(1,'a'),sample(0,'b'),sample(0,'c')])
    assert mixed['complete_group'] and mixed['mixed_reward']
    assert mixed['binary_population_variance']==.25
    assert mixed['rloo_advantages']==[2/3,2/3,-2/3,-2/3]
    assert mixed['same_first_native_path'] and mixed['all_clean_target_stdout']
    incomplete=a.group_summary([sample(1,'a'),sample(1,'a'),sample(0,'b'),sample(0,'x',False)])
    assert not incomplete['complete_group'] and incomplete['rloo_advantages'] is None
    assert a.group_summary([sample(1,'a')]*4)['binary_population_variance']==0
    assert not a.actual_final_text({'stop_condition':'max_turns','root_reply':''},{'tool_calls':[{'name':'ipython'}],'content':''},True)

def test_actual_preserved_native_fixture_and_original_scoring_seam():
    # Existing operator-authored fixture, not a new training or heldout model query.
    sys.path.insert(0,str(a.SIDE));c=importlib.import_module('collect')
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    fixture=a.STORE/'sidecars/openai-mrcr-procedural-sft-terminal-strip-disabled-v1/cpu-green-002'
    path=next(p for p in sorted(fixture.rglob('DERIVED.json')) if a.read(p)['raw_exact'])
    raw=a.read(path.with_name('EPISODE.json'));native=[a.read(p) for p in sorted((path.parent/'native-calls').glob('*-result.json'))]
    item={'episode':raw,'episode_sha256':a.digest(raw),'derived':a.read(path),'coordinate':{'id':'CPU_ONLY'}}
    tokenizer=AutoTokenizer.from_pretrained(str(c.study.BASE),local_files_only=True)
    value=a.episode(item,native,{'answer':'  MARK\ncurly ’ target  ','random_string_to_prepend':'  MARK'},
        native[0]['response']['tokens']['prompt_ids'],"print('CPU_TOOL_OK')",c,tokenizer,Qwen3Renderer(tokenizer))
    assert value['binary_reward']==1 and value['actual_final_text'] and value['first_teacher_AST_exact']
    assert len(value['turns'])==2 and not value['turns'][0]['actual_final_text_turn']
    assert value['turns'][1]['actual_final_text_turn'] and value['turns'][1]['bare_exact']
    assert not value['clean_target_stdout']
