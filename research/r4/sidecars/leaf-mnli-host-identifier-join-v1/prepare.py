"""Freeze CPU-native requests and qualify both JSON field orders."""
import copy,hashlib,importlib.metadata,time
import protocol_v2 as p,study as s

def main():
    import xgrammar as xg
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    started=time.time();tok=s.tokenizer();rows=p.plan();contexts=p.contexts()
    requests={r['id']:p.request(contexts[r['context_index']],r) for r in rows}
    wires={k:s.serialize(body) for k,body in requests.items()}
    prompts={}
    for k,body in requests.items():
        typed=ChatCompletionRequest.model_validate(copy.deepcopy(body))
        assert not typed.tools
        prompts[k]=tok.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,
            tokenize=True,return_dict=False,**typed.chat_template_kwargs)
    oldrows=s.read(s.PRIOR/'PLAN_v2.json');oldwire=s.read(s.PRIOR/'ORDERED_REQUESTS_v2.json')
    for row in rows:
        if not row['arm'].endswith('tag_first'):continue
        arm=row['arm'].split('_',1)[0]+'_explicit_slot'
        previous=next(r for r in oldrows if r['context_index']==row['context_index'] and r['arm']==arm)
        baseline=s.read(s.PRIOR/'REQUESTS_v2.json')[previous['id']]
        actual=requests[row['id']]
        assert actual['messages']==baseline['messages']
        assert s.serialize(actual['structured_outputs'])==s.serialize(__import__('json').loads(oldwire[previous['id']])['structured_outputs'])
    config=s.read(__import__('pathlib').Path(s.MODEL['path'])/'config.json')
    vocabulary=config.get('text_config',config)['vocab_size']
    compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocabulary),max_threads=2,cache_enabled=True)
    checks=[]
    for row in rows:
        context=contexts[row['context_index']];body=requests[row['id']]
        grammar=compiler.compile_json_schema(s.serialize(body['structured_outputs']['json']),any_whitespace=True)
        def accepts(value):
            matcher=xg.GrammarMatcher(grammar)
            return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
        for label in p.LABELS:
            if row['arm'].endswith('labels_only'):
                good=[label]*48
                bad=[{'tag':t,'label':label} for t in p.requested_tags(context)]
                assert not accepts(good[:-1])
            else:
                good=[dict(tag=t,label=label) for t in p.requested_tags(context)]
                bad=[dict(reversed(list(v.items()))) for v in good]
            assert accepts(good)
            assert not accepts(bad)
        assert len(prompts[row['id']])+3072<=8192
        checks.append(dict(id=row['id'],arm=row['arm'],prompt_tokens=len(prompts[row['id']]),
                           declared_format_accepts_all_labels=True,wrong_format_rejected=True))
    native=dict(requests=48,schemas_compiled=48,schema_checks=checks,gpu_calls=0,service_calls=0,
                request_wire_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in wires.items()},
                max_prompt_tokens=max(map(len,prompts.values())),
                max_prompt_plus_output=max(map(len,prompts.values()))+3072,
                tag_first_matches_previous_explicit_messages_and_ordered_schema=True,
                versions={n:importlib.metadata.version(n) for n in ('vllm','transformers','xgrammar')},
                elapsed_seconds=time.time()-started)
    for name,value in {'PLAN_v2.json':rows,'REQUESTS_v2.json':requests,
                       'ORDERED_REQUESTS_v2.json':wires,'PROMPT_IDS_v2.json':prompts,
                       'CPU_NATIVE_v2.json':native,
                       'PLANNED_NULL_ENDPOINTS_v2.json':[p.null_row(r,'not attempted') for r in rows]}.items():
        s.write(s.ROOT/name,value)
    print({k:native[k] for k in ('requests','schemas_compiled','max_prompt_plus_output','elapsed_seconds')})
if __name__=='__main__':main()
