import importlib
import json
from copy import deepcopy


def subject(name='study'):
    try: return importlib.import_module(name)
    except ModuleNotFoundError: assert False, 'approved implementation absent: '+name


def test_exact_source_crosswalk_and_alias_only_model_pairs():
    s=subject();d=s.build_design(s.build_data())
    assert len(d['plan'])==144
    assert len({r['id'] for r in d['plan']})==144
    for i in range(72):
        a,b=d['plan'][i],d['plan'][72+i]
        x,y=s.make_request(d,a),s.make_request(d,b)
        assert x['messages']==y['messages'] and x['tools']==y['tools']
        assert x['structured_outputs']==y['structured_outputs']
        assert x['model']!=y['model']
    for c in d['contexts']:
        rows=[r for r in d['plan'] if r['context_index']==c['index']]
        assert len(rows)==12
        inputs=[s.make_request(d,r)['messages'][1]['content'].split(s.INPUT_MARKER)[1] for r in rows]
        assert len(set(inputs))==1
        assert len({r['group_id'] for r in c['records']})==64


def test_invalid_is_zero_missing_is_null_and_no_tag_repair():
    s=subject();gold={'records':[{'id':'q7654','gold_label':'yes'},{'id':'q9876','gold_label':'no'}], 'labels':['yes','no'],'arm':'matching'}
    assert s.score_labels('[{"tag":"q7654","label":"yes"},{"tag":"q9876","label":"no"}]',gold)['strict_correct']==2
    wrong=s.score_labels('[{"tag":"q9876","label":"no"},{"tag":"q7654","label":"yes"}]',gold)
    assert wrong['strict_correct']==0 and wrong['aligned_records']==0
    assert not s.score_labels('[{"tag":"q7654","tag":"q7654","label":"yes"}]',gold)['schema_valid']
    reverse=s.score_labels('[{"label":"yes","tag":"q7654"},{"label":"no","tag":"q9876"}]',gold)
    assert reverse['strict_correct']==2 and reverse['key_order_valid'] is False
    d=s.build_design(s.build_data());r=d['plan'][0]
    assert s.score_coordinate(d,r,[])['strict_correct_assignments'] is None
    invalid=s.score_labels('[]',d['batches'][r['batch_id']]['gold'])
    assert s.score_coordinate(d,r,[{'coordinate':r,'score':invalid,'usage':{},'started':1,'ended':2}])['strict_correct_assignments']==0


def test_base_descriptor_rejects_adapter_and_wrong_model():
    v=subject('service');s=subject();m=s.MODELS['qwen35']
    endpoint=v.descriptor(m,'/tmp/qualified')
    v.validate_descriptor(endpoint,m)
    assert endpoint['adapter'] is None
    for bad in ({**endpoint,'adapter':{'path':'fake'}},{**endpoint,'model_alias':'wrong'}):
        try:v.validate_descriptor(bad,m)
        except ValueError:pass
        else:assert False,'false base identity accepted'
    v.validate_models({'data':[{'id':m['alias'],'root':m['path'],'parent':None}]},m)
    try:v.validate_models({'data':[{'id':m['alias'],'root':m['path'],'parent':'adapter-parent'}]},m)
    except ValueError:pass
    else:assert False,'LoRA-like model card accepted'


def test_common_config_no_lora_eager_and_explicit_sampling():
    s=subject();v=subject('service')
    from prime_rl.configs.inference import InferenceConfig
    for name,m in s.MODELS.items():
        cfg=v.config(m,'/tmp/qualified','fixture-key')
        InferenceConfig.model_validate(deepcopy(cfg))
        assert cfg['vllm']['enable_lora'] is False
        assert cfg['vllm']['enforce_eager'] is True
        assert cfg['vllm']['enable_prefix_caching'] is False
        assert cfg['vllm']['generation_config']=='vllm'
        assert cfg['enable_fp32_lm_head'] is False
        if name=='qwen35':assert cfg['vllm']['language_model_only'] and cfg['vllm']['mamba_cache_mode']=='align'
    d=s.build_design(s.build_data());body=s.make_request(d,d['plan'][0])
    assert body['chat_template_kwargs']=={'enable_thinking':False}
    assert body['top_k']==-1 and body['top_p']==1 and body['presence_penalty']==0


def test_native_template_kwargs_and_collector_preserve_invalid_and_null(tmp_path):
    import asyncio
    import httpx
    s=subject();driver=subject('driver')
    from transformers import AutoTokenizer
    d=s.build_design(s.build_data());d['plan']=d['plan'][72:75];d['coordinates']=deepcopy(d['plan']);d['max_concurrent_calls']=1
    tok=AutoTokenizer.from_pretrained(s.MODELS['qwen35']['path'],local_files_only=True,trust_remote_code=False)
    requests={r['id']:s.make_request(d,r) for r in d['plan']}
    ids={key:driver.typed_ids(tok,body) for key,body in requests.items()}
    assert all(tok.decode(tokens[-16:]).endswith('<think>\n\n</think>\n\n') for tokens in ids.values())
    d['rendered_prompts']={key:{'typed_token_ids_sha256':s.digest(value)} for key,value in ids.items()}
    spec={'design':d,'requests':requests,'request_sha256':{key:s.digest(body) for key,body in requests.items()}}
    pending=iter(d['plan'])
    def transport(request):
        r=next(pending);body=json.loads(request.content);assert body==requests[r['id']]
        if r==d['plan'][-1]:return httpx.Response(500,json={'error':'fixture unavailable'})
        content='[]' if r==d['plan'][1] else s.serialize(s.synthetic(d['batches'][r['batch_id']]['gold'],d['contexts'][0]['labels'][0]))
        return httpx.Response(200,json={'model':body['model'],'prompt_token_ids':ids[r['id']],
            'choices':[{'message':{'content':content},'finish_reason':'stop','token_ids':[1]}],
            'usage':{'prompt_tokens':len(ids[r['id']]),'completion_tokens':1}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(transport),event_hooks={'request':[driver.wire_hook(spec,tmp_path)]}) as client:
            return await s.collect_calls(client,'http://fixture/v1',spec,tmp_path)
    records,reason=asyncio.run(run());analysis=s.summarize(d,records)
    assert reason=='request_error' and len(records)==3
    assert analysis['coordinates'][0]['fully_valid']
    assert analysis['coordinates'][1]['strict_correct_assignments']==0
    assert analysis['coordinates'][2]['strict_correct_assignments'] is None
    assert len(list((tmp_path/'wire').glob('*.json')))==3
