"""Two focused fixtures: actual two-turn CPU runtime and host-only metric branches."""
import asyncio
import json
import os
from pathlib import Path
import time

from aiohttp import web
import study as s
import collect
import metrics
from native_capture import capture


def test_actual_two_turn_native_templates_and_original_python_runtime(tmp_path, monkeypatch):
    async def run():
        from verifiers.v1.env import RunSlot
        s.configure_runtime()
        for arm in s.ARMS:
            s.bind_arm(arm)
            coordinate = s.plan(arm)[0]
            env = s.environment(arm)
            task = next(t for t in env.taskset if t.data.name == coordinate['id'])
            tokenizer = s.tokenizer(arm); requests = []
            code = "import json; m=json.load(open('/context.json')); print('CPU_ROLE='+m[1]['role'])"
            tool = ('<tool_call>\n' + json.dumps({'name':'ipython','arguments':{'code':code}}) + '\n</tool_call>'
                    if arm == 'qwen3' else '<tool_call>\n<function=ipython>\n<parameter=code>\n' + code + '\n</parameter>\n</function>\n</tool_call>')
            replies = [tool, 'CPU_SCREEN_FINAL  ']
            async def provider(request):
                body = await request.json(); requests.append(body)
                assert len(requests) <= 2
                ids = tokenizer.encode(replies[len(requests)-1], add_special_tokens=False) + [tokenizer.eos_token_id]
                return web.json_response({'request_id':'CPU_'+arm+str(len(requests)),
                    'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),
                             'total_tokens':len(body['token_ids'])+len(ids)},
                    'choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[
                        {'token':'token_id:'+str(token),'logprob':-.5} for token in ids]}}]})
            app=web.Application();app.router.add_post('/inference/v1/generate',provider)
            runner=web.AppRunner(app);await runner.setup()
            site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
            endpoint={'model_alias':s.MODEL_ALIAS,'base_model':s.MODELS[arm],'adapter':None,
                      'host':'127.0.0.1','port':site._server.sockets[0].getsockname()[1],
                      'api_key_env':'SCREEN_CPU_KEY'}
            monkeypatch.setenv('SCREEN_CPU_KEY','not-a-real-secret')
            directory=tmp_path/arm
            try:
                with capture(directory/'native-calls',[coordinate]) as native:
                    async with env.serving():
                        episode=await asyncio.wait_for(env.run_slot(RunSlot(task),collect.model_context(endpoint,coordinate)),180)
                raw=episode.to_record();derived=metrics.inspect(raw,coordinate,native)
            finally:await runner.cleanup()
            s.write_x(directory/'EPISODE.json',raw);s.write_x(directory/'DERIVED.json',derived)
            s.write_x(directory/'PROVIDER_REQUESTS.json',requests)
            assert len(requests)==2 and derived['root_actions_returned']==2
            assert derived['child_actions_returned']==0 and derived['initial_prefix_verified']
            assert derived['first_action']['schema_correct'] is True
            assert derived['terminal_class']=='valid_final' and derived['raw_exact'] is False
            fidelity=derived['final_text_fidelity']
            assert fidelity['raw_model_final_stop_tokens_removed']=='CPU_SCREEN_FINAL  '
            assert fidelity['raw_equals_native_parsed'] is (arm=='qwen3')
            assert fidelity['raw_to_native_difference_is_exactly_strip'] is (arm=='qwen35')
            assert fidelity['original_harness_final']=='CPU_SCREEN_FINAL'
            assert fidelity['native_to_harness_difference_is_exactly_strip'] is (arm=='qwen3')
            assert any('CPU_ROLE=user' in ((n.get('message') or {}).get('content') or '')
                       for n in raw['traces'][0]['nodes'] if (n.get('message') or {}).get('role')=='tool')
            assert len(list((directory/'native-calls').glob('*-wire-request.json')))==2
            assert len(list((directory/'native-calls').glob('*-wire-response.json')))==2
    asyncio.run(run())


def test_host_observation_selection_and_terminal_unknown_are_distinct():
    messages=[{'role':'user','content':'shared demonstration'},
              {'role':'user','content':'write a poem about clouds'},
              {'role':'assistant','content':'FIRST_UNIQUE_RESPONSE'},
              {'role':'user','content':'write a poem about clouds'},
              {'role':'assistant','content':'SECOND_UNIQUE_RESPONSE'},
              {'role':'user','content':'final request'}]
    gold={'desired_msg_index':3,'answer':'MARKSECOND_UNIQUE_RESPONSE','random_string_to_prepend':'MARK'}
    one=metrics.observation_inventory(['SECOND_UNIQUE_RESPONSE'],messages,gold)
    broad=metrics.observation_inventory([json.dumps(messages)],messages,gold)
    assert one['target_assistant_observed'] and one['target_ordinal']==2
    assert one['matching_message_indices']==[4] and one['unique_target_only']
    assert broad['target_assistant_observed'] and not broad['unique_target_only']
    assert metrics.terminal_status('unknown_stop',True,[],True,'answer')=='unavailable_unknown_stop'
    assert metrics.terminal_status('max_turns',True,[],True,None)=='model_no_final_within_two_turns'
    assert metrics.terminal_status('agent_completed',True,[],True,'')=='model_invalid_final'
