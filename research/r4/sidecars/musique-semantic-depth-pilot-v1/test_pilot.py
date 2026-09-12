"""Two bounded CPU contract fixtures; no weights or GPU service are loaded."""
import asyncio
import json
from pathlib import Path

import pytest


def test_frozen_public_schema_and_official_alias_support_scoring():
    import musique_study as s
    import scoring
    manifest = s.read(s.INPUTS / 'MANIFEST.json')
    assert len(manifest['selected']) == 12
    assert sorted(r['hop_count'] for r in manifest['selected']) == [2]*4+[3]*4+[4]*4
    seen_steps, seen_supports = set(), set()
    for row in manifest['selected']:
        public = s.read(row['public_path'])
        assert set(public) == {'question', 'paragraphs'}
        assert all(set(p) == {'idx', 'title', 'paragraph_text'} for p in public['paragraphs'])
        assert not (set(row['singlehop_ids']) & seen_steps)
        assert not (set(row['support_paragraph_sha256']) & seen_supports)
        seen_steps.update(row['singlehop_ids']); seen_supports.update(row['support_paragraph_sha256'])
        assert row['public_qwen_tokens'] <= 5500
    gold = {'answer':'Nile', 'answer_aliases':['The Nile'], 'support_idxs':[1,2]}
    result = scoring.score_final('{"answer":"The Nile","support_idxs":[1,3]}', gold, 20)
    assert result['answer_em'] == result['answer_f1'] == 1
    assert result['support_em'] == 0 and result['support_f1'] == .5
    assert scoring.score_final('```json\n{}\n```', gold, 20)['valid_json'] is False
    assert scoring.score_final('{"answer":"Nile","answer":"Nile","support_idxs":[]}', gold, 20)['valid_json'] is False
    assert len(s.plan()) == 48 and len({r['record_id'] for r in s.plan()}) == 12


def test_actual_depth2_callback_and_shared_physical_budget(tmp_path, monkeypatch):
    asyncio.run(_actual_depth2(tmp_path, monkeypatch))


async def _actual_depth2(tmp_path, monkeypatch):
    import musique_study as s
    import collect
    from aiohttp import web
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from native_audit import capture
    from verifiers.v1.clients.train import TrainClient
    from verifiers.v1.dialects import ChatDialect
    from verifiers.v1.env import RunSlot
    from verifiers.v1.errors import ProviderError
    import scoring

    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', '')
    monkeypatch.setenv('MUSIQUE_CPU_KEY', 'cpu-fixture-no-science')
    s.configure_runtime()
    coordinate = next(row for row in s.plan() if row['arm'] == 'depth2')
    env = s.environment('depth2')
    task = next(task for task in env.taskset if task.data.name == coordinate['id'])
    tok = create_renderer(load_tokenizer(s.MODEL), Qwen3RendererConfig(enable_thinking=True))._tokenizer
    def tool(code):
        return '<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':code}})+'\n</tool_call>'
    replies = [tool('c = await rlm("CPU_CHILD"); print(c.answer)'),
               tool('g = await rlm("CPU_GRANDCHILD"); print(g.answer)'),
               tool('print("rlm" in globals())'), 'GRANDCHILD_OK', 'CHILD_OK',
               '{"answer":"CPU_ONLY","support_idxs":[]}']
    requests = []
    async def provider(request):
        body = await request.json(); requests.append(body)
        assert len(requests) <= 7
        assert len(body['token_ids'])+1024 <= 8192
        assert body['sampling_params']['max_tokens'] == 1024
        text = replies[len(requests)-1] if len(requests)<=6 else '{"answer":"CPU_ONLY","support_idxs":[]}'
        ids = tok.encode(text, add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'MUSIQUE_CPU_{len(requests)}','model':s.MODEL_ALIAS,
            'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),
                     'total_tokens':len(body['token_ids'])+len(ids)},
            'choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[
                {'token':f'token_id:{token}','logprob':-.5} for token in ids]}}]})
    app = web.Application(); app.router.add_post('/inference/v1/generate', provider)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner,'127.0.0.1',0); await site.start()
    endpoint = {'model_alias':s.MODEL_ALIAS,'base_model':{'path':str(s.MODEL)},'adapter':None,
                'host':'127.0.0.1','port':site._server.sockets[0].getsockname()[1], 'api_key_env':'MUSIQUE_CPU_KEY'}
    context = collect.model_context(endpoint,coordinate)
    try:
        with capture(tmp_path/'native-calls', s.plan()) as audit:
            async with env.serving():
                episode = await asyncio.wait_for(env.run_slot(RunSlot(task),context),100)
            raw = episode.to_record()
            # Exercise the actual wrapped native call again with the identical episode
            # coordinate: admission must refuse before sending the seventh physical request.
            client = TrainClient(context.client)
            try:
                with pytest.raises(ProviderError, match='musique_physical_call_cap'):
                    await client.get_response(ChatDialect(), {'model':s.MODEL_ALIAS,'messages':[
                        {'role':'user','content':'CPU refusal check'}]},context.sampling,
                        session_id=raw['traces'][0]['id'])
            finally:
                await client.close()
            assert len(requests)==6
            qonly = next(row for row in s.plan() if row['arm']=='question_only')
            direct_raw = await collect.direct(endpoint,qonly)
            assert scoring.inspect(direct_raw,qonly,audit)['available']
            # The actual renderer/HTTP-hook path must refuse an overlong request;
            # selection-time external-file token lengths are not this invariant.
            over = next(row for row in s.plan() if row['arm']=='question_only' and row['id']!=qonly['id'])
            over_context = collect.model_context(endpoint,over)
            over_client = TrainClient(over_context.client)
            try:
                with pytest.raises(ProviderError,match='musique_context_cap'):
                    await over_client.get_response(ChatDialect(),{'model':s.MODEL_ALIAS,'messages':[
                        {'role':'user','content':' token'*9000}]},over_context.sampling,
                        session_id='CPU_OVERLONG')
            finally:
                await over_client.close()
        returned = [r for r in audit if r['status']=='returned']
        assert len(requests) == len(returned) == 7
        derived = scoring.inspect(raw, coordinate, returned)
        assert derived['native_mapping']['complete'], derived
        assert derived['available'] and derived['max_observed_depth'] == 2, derived
        assert derived['actions_by_depth'] == {'0':2,'1':2,'2':2}
        assert all(r.get('wire_response_text') and r.get('wire_request_text') for r in returned)
        tools = [n['message'].get('content') for n in raw['traces'][0]['nodes']
                 if n.get('message',{}).get('role')=='tool']
        assert any('False' in str(text) for text in tools), tools
        s.write_x(tmp_path/'EPISODE.json',raw)
        s.write_x(tmp_path/'QUESTION_ONLY_EPISODE.json',direct_raw)
        s.write_x(tmp_path/'PROVIDER_REQUESTS.json',requests)
    finally:
        await runner.cleanup()
