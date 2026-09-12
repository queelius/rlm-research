import copy
import json
from pathlib import Path

import analyze


def test_archived_native_path_identity_and_actual_collector_seam():
    files=sorted((analyze.OLD/'science/episodes').glob('*.json'))
    item=json.loads(files[0].read_text());trace=item['episode']['traces'][0]
    native=[json.loads(p.read_text()) for p in sorted((analyze.OLD/'science/native-calls').glob('*-result.json'))]
    path=analyze.path_projection([r for r in native if r['session_id']==trace['id']])
    same=analyze.compare_paths(path,copy.deepcopy(path))
    assert same['all_action_ids_equal'] and same['all_prompt_ids_equal'] and same['strict_native_path_equal']
    action=copy.deepcopy(path);action[0]['completion_ids'][-1]+=1
    assert not analyze.compare_paths(path,action)['all_action_ids_equal']
    prompt=copy.deepcopy(path);prompt[0]['prompt_ids'][0]+=1
    result=analyze.compare_paths(path,prompt)
    assert result['all_action_ids_equal'] and not result['strict_native_path_equal']
    assert not analyze.compare_paths(path,path[:-1])['same_call_count']
    module=analyze.bindings();coord=item['coordinate']
    gold=module.study.read(module.study.input_dir('held')/'HOST_GOLD.json')[coord['record_id']]
    prefix=module.study.read(module.study.input_dir('held')/'PREFIXES.json')[coord['id']]['token_ids']
    actual=module.source.inspect_trace(item['episode'],gold,native,prefix)
    assert actual['native_mapping_complete'] and actual['initial_root_prefix_verified']
    assert actual['raw_exact']==item['derived']['raw_exact']
