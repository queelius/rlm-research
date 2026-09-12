"""Outcome-blind ID-order selection and exact model-native first-prefix inventory."""
import hashlib
from pathlib import Path
import study as s


def main():
    assert not s.INPUTS.exists()
    s.short().verify_data()
    rows=sorted(s.read(s.DATA/'MODEL_INPUTS_V2.json')['train'],key=lambda x:x['id'])[:8]
    assert len(rows)==8 and len({x['id'] for x in rows})==8
    old=s.short().v7_study().old_module()
    teacher=s.load('controller_screen_teacher_schema_only',s.SIDE/'openai-mrcr-procedural-sft-warmstart-v1/teacher.py')
    system,tools=teacher._system_and_ordered_tools()
    assert len(tools)==1 and tools[0]['function']['name']=='ipython'
    schedule=[];prefixes={};gold_source=s.read(s.DATA/'host/HOST_GOLD.json')['train']
    for arm in s.ARMS:
        tasks=[]
        for index,row in enumerate(rows):
            payload=Path(row['prompt_json_path']).read_bytes()
            assert hashlib.sha256(payload).hexdigest()==row['prompt_json_sha256']
            question=Path(row['final_question_path']).read_text()
            assert hashlib.sha256(question.encode()).hexdigest()==row['final_question_sha256']
            prompt=s.short().root_prompt(question,row['prompt_json_bytes'])
            coordinate={'arm':arm,'record_id':row['id'],'row_index':index,'seed':202609190000+index,
                        'context_sha256':row['prompt_json_sha256'],'source_row_sha256':row['source_row_sha256']}
            coordinate['id']=s.digest(coordinate);schedule.append(coordinate)
            tasks.append(old.MRCRData(idx=index,name=coordinate['id'],prompt=prompt,row_id=row['id'],
                document_sha256=row['prompt_json_sha256'],arm='released_controller_'+arm).model_dump(mode='json',exclude_none=True))
            messages=[system,{'role':'user','content':prompt}]
            ids=s.renderer(arm).render(messages,tools=tools,add_generation_prompt=True).token_ids
            official=s.tokenizer(arm).apply_chat_template(messages,tools=tools,enable_thinking=False,
                tokenize=True,return_dict=False,add_generation_prompt=True)
            assert ids==official and len(ids)+1024<=8192
            prefixes[coordinate['id']]={'token_ids':ids,'token_ids_sha256':s.digest(ids),
                'messages':messages,'tools':tools,'renderer_config':s.renderer_config(arm).model_dump(mode='json'),
                'prefix_plus_output_cap':len(ids)+1024,'official_initial_template_equal':True,
                'stop_token_ids':s.renderer(arm).get_stop_token_ids()}
        s.write_x(s.INPUTS/f'tasks_{arm}.json',tasks)
    s.write_x(s.INPUTS/'SCHEDULE.json',schedule)
    s.write_x(s.INPUTS/'PREFIXES.json',prefixes)
    s.write_x(s.INPUTS/'MANIFEST.json',{'selected':rows,'selection':'first8 lexicographic id among frozen32train',
        'source_manifest':str(s.DATA/'MANIFEST_V2.json'),'source_manifest_sha256':s.sha(s.DATA/'MANIFEST_V2.json'),
        'source_model_inputs_sha256':s.sha(s.DATA/'MODEL_INPUTS_V2.json'),
        'same_research_exposed_train_pool':True,'heldout_read':False,'model_pretraining_exposure':'unknown',
        'examples_selected_by_outcomes':False,'original_task_prompt_unchanged':True,
        'task_prompt_mentions_child_but_depth_zero_disables_it':True})
    s.write_x(s.INPUTS/'HOST_GOLD.json',{row['id']:gold_source[row['id']] for row in rows})
    (s.INPUTS/'HOST_GOLD.json').chmod(0o600)
    print({'examples':8,'episodes':16,'prefixes':16,'max_first_prefix_plus_output':max(x['prefix_plus_output_cap'] for x in prefixes.values())})


def depth_zero_prefixes():
    """Retain first draft; remove only actual runtime's depth-positive paragraph."""
    import copy
    assert not (s.ROOT/'READY.json').exists() and not s.PREFIX_FILE.exists()
    prior=s.read(s.INPUTS/'PREFIXES.json');updated={}
    teacher=s.load('controller_screen_exact_tool_order',s.SIDE/'openai-mrcr-procedural-sft-warmstart-v1/teacher.py')
    _,ordered_tools=teacher._system_and_ordered_tools()
    paragraph=("A callable `rlm` is already in your global namespace — call it directly with `await rlm('sub-task')` "
        "to spawn a recursive sub-agent. Returns an `RLMResult` with `.answer` (string), `.usage`, `.turns`, and `.session_dir`.\n"
        "For parallel sub-agents, use normal Python async patterns such as `await asyncio.gather(rlm('task1'), rlm('task2'))`.\n\n")
    actual=s.read(s.ROOT/'cpu-fixture-001/test_actual_two_turn_native_te0/qwen3/native-calls/0000-start.json')['body']
    for coordinate in s.plan():
        arm=coordinate['arm'];value=copy.deepcopy(prior[coordinate['id']]);system=value['messages'][0]
        # JSON checkpoint key sorting must not alter the original native tool serialization.
        value['tools']=copy.deepcopy(ordered_tools)
        assert system['content'].count(paragraph)==1
        system['content']=system['content'].replace(paragraph,'')
        assert system==actual['messages'][0]
        ids=s.renderer(arm).render(value['messages'],tools=value['tools'],add_generation_prompt=True).token_ids
        official=s.tokenizer(arm).apply_chat_template(value['messages'],tools=value['tools'],enable_thinking=False,
            tokenize=True,return_dict=False,add_generation_prompt=True)
        assert ids==official and len(ids)+1024<=8192
        value.update(token_ids=ids,token_ids_sha256=s.digest(ids),prefix_plus_output_cap=len(ids)+1024,
                     original_draft_depth1_inventory_retained=True,actual_depth0_system_verified=True)
        updated[coordinate['id']]=value
    s.write_x(s.PREFIX_FILE,updated)
    print({'depth_zero_prefixes':len(updated),'actual_CPU_system_matched':True,
           'prior_unsealed_prefix_inventory_preserved':True})


if __name__=='__main__':
    import sys
    if sys.argv[1:]==['depth-zero-prefixes']:depth_zero_prefixes()
    elif not sys.argv[1:]:main()
    else:raise ValueError('unexpected preparation mode')
