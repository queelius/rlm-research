import json
from pathlib import Path
import tempfile
import asyncio
import os
import time


def test_overlay_preserves_raw_and_clips_only_visible_view():
    import bv_overlay as o

    source = o.composed_engine_source()
    patched = o.patch_engine(source)
    assert patched != source
    assert patched.count(".observation_view.jsonl") == 1
    assert patched.count("content = truncate_tool_output(result)") == 1
    assert "if _observation_view_cap == 20000" in patched
    assert "_observation_keep = _observation_view_cap // 2" in patched
    assert "self.session.log_tool_result(turn, tool_name, result, duration)" in patched
    compile(patched, "<bounded-view-test>", "exec")
    raw = "A" * 12000
    visible, record = o.render_for_test(raw, 4096, turn=3)
    assert raw not in visible and "bytes truncated" in visible
    assert record["raw_content"] == raw and record["visible_content"] == visible
    assert record["raw_bytes"] == 12000 and record["view_cap_bytes"] == 4096
    assert record["clipped"] is True and record["omitted_bytes"] == 12000 - 4096
    control, control_record = o.render_for_test(raw, 20000, turn=3)
    assert control == raw and control_record["clipped"] is False


def test_overlay_program_replaces_only_exact_composed_engine():
    import bv_overlay as o

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "rlm" / "engine.py"
        path.parent.mkdir()
        path.write_text(o.composed_engine_source())
        receipt = o.apply_to_roots([Path(directory)])
        assert receipt["patched"] == [str(path)]
        assert Path(path).read_text() == o.patch_engine(o.composed_engine_source())


def test_actual_native_root_child_root_sees_clipped_view_and_harvests_raw(tmp_path, monkeypatch):
    import bv_collect as c
    import bv_study as s
    from aiohttp import web

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU_FIXTURE_NOT_CREDENTIAL")
    monkeypatch.setenv("BOUNDED_VIEW_CPU_KEY", "CPU_FIXTURE_NOT_CREDENTIAL")
    async def fixture():
        row=next(r for r in s.read(s.ROOT/'inputs/FREE_PLAN.json') if r['return_arm']=='B' and r['view_bytes']==4096 and r['records']==128)
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id']);binding=s.binding();native=s.stack().native;tokenizer=native.renderer()._tokenizer;roots=[]
        code='from rlm.api import run as rlm\nchild=await rlm("Return the word ok")\nprint("A"*12000)'
        async def provider(request):
            body=await request.json()
            if body['model']==binding['role_map']['root']:
                roots.append(body)
                if len(roots)==1:reply=native.tool_action(code)
                else:
                    decoded=tokenizer.decode(body['token_ids'],skip_special_tokens=False)
                    assert 'Warning: truncated output' in decoded and 'A'*6000 not in decoded
                    reply='Answer: 0'
            else:
                assert body['model']==binding['fixed_child'];reply='ok'
            ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            return web.json_response({'request_id':'BV_CPU','usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids)},'choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{v}','logprob':-.5} for v in ids]}}]})
        async def models(request):return web.json_response({'data':[{'id':alias,'root':model['path'],'max_model_len':8192} for alias,model in binding['models'].items()]})
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor={'host':'127.0.0.1','port':site._server.sockets[0].getsockname()[1],'api_key_env':'BOUNDED_VIEW_CPU_KEY'}
        try:
            await c.implementation().episode(row,context,binding,descriptor,tmp_path/'native',time.time()+120,'free')
            episode=s.read(tmp_path/'native/EPISODE.json');raw=episode['traces'][0]['info']['bounded_observation_view']['raw']
            records=[json.loads(line) for line in raw.splitlines()]
            root_records=[x for x in records if x['view_cap_bytes']==4096 and x['clipped']]
            assert len(roots)==2 and root_records and root_records[0]['raw_content'].startswith('A'*4096)
            assert root_records[0]['raw_bytes']>4096
            assert root_records[0]['clipped'] and root_records[0]['view_cap_bytes']==4096
        finally:await runner.cleanup()
    asyncio.run(fixture())
