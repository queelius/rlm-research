"""Freeze additive six-arm requests over the immutable eight-context draft selection."""
import copy,hashlib,importlib.metadata,json,time
from pathlib import Path
import protocol_v2 as p,study as s

DRAFT_DATA_SHA='e4ee78099d12d22b2e4e38fc2aa641a027712a34bf604124f753cf741ee829e8'
DRAFT_PUBLIC_SHA='8ed56fba25ca9e0a77b7fce36648eece3dd9a3fd9a4576a8c5f6480dd76ba47b'
DRAFT_SELECTION_SHA='202997ba0aa612e772fb0857209926fb56c568c3f42ae98661cf5b46938265e3'
def typed(tok,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value=ChatCompletionRequest.model_validate(copy.deepcopy(body));assert not value.tools
    return tok.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**value.chat_template_kwargs)
def main():
    import xgrammar as xg
    started=time.time()
    if s.sha(s.ROOT/'DATA.json')!=DRAFT_DATA_SHA or s.sha(s.ROOT/'PUBLIC.json')!=DRAFT_PUBLIC_SHA or s.sha(s.ROOT/'SELECTION_AUDIT.json')!=DRAFT_SELECTION_SHA:raise ValueError('draft selection changed')
    named=[]
    for directory in sorted(s.SIDE.glob('*mnli*')):
        for name in ('DATA.json','PUBLIC.json','PLAN.json','PLAN_v2.json','REQUESTS.json','REQUESTS_v2.json','READY.json','READY_v2.json'):
            path=directory/name
            if path.exists() and path.parent!=s.ROOT:named.append(path)
    manifest='\n'.join(path.read_text(errors='replace') for path in named);contexts=p.contexts();visible={r['id'] for c in contexts for r in c['records']};aliases={x for values in p.alien_dictionary().values() for x in values};seeds=sorted({row['seed'] for row in p.plan()})
    alias_visible=sorted(aliases&visible);alias_text=sorted(x for x in aliases if x in manifest);seed_collisions=sorted(seed for seed in seeds if str(seed) in manifest)
    if len(aliases)!=384 or alias_visible or alias_text or seed_collisions:raise ValueError('collision')
    rows=p.plan();tok=s.tokenizer();requests={r['id']:p.request(contexts[r['context_index']],r) for r in rows};ordered={k:s.serialize(v) for k,v in requests.items()};prompts={k:typed(tok,v) for k,v in requests.items()}
    compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=s.read(Path(s.MODEL['path'])/'config.json').get('text_config',s.read(Path(s.MODEL['path'])/'config.json'))['vocab_size']),max_threads=2,cache_enabled=True);checks=[]
    for row in rows:
        context=contexts[row['context_index']];schema=p.schema(context,row['arm']);grammar=compiler.compile_json_schema(s.serialize(schema['json']),any_whitespace=True)
        def accepts(value):matcher=xg.GrammarMatcher(grammar);return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
        tags=p.requested_tags(context)
        for label in p.LABELS:assert accepts([{'tag':tag,'label':label} for tag in tags])
        bad=[{'tag':tag,'label':p.LABELS[i%3]} for i,tag in enumerate(tags)];bad[0]['tag']=tags[1];assert not accepts(bad)
        checks.append(dict(id=row['id'],context_index=row['context_index'],arm=row['arm'],schema_sha256=s.digest(schema)))
    for ci in range(8):
        hashes={s.digest(requests[r['id']]['structured_outputs']) for r in rows if r['context_index']==ci}
        if len(hashes)!=1:raise ValueError('output schema differs within block')
    amendment=dict(approved_before_model_output=True,draft_data_sha256=DRAFT_DATA_SHA,draft_public_sha256=DRAFT_PUBLIC_SHA,draft_selection_audit_sha256=DRAFT_SELECTION_SHA,draft_contexts_reused_without_reranking=True,added_arm='aligned_legacy',planned_calls_before=40,planned_calls_after=48,factorial='visible relation3 x wording2',outer_seconds_before=1200,outer_seconds_after=1440,interpretation=['wording effect is instruction-sensitive component, not proof of ambiguity','closeness on eight contexts is not equivalence','thresholds are practical pilot rules, not absence evidence'],created_epoch=time.time())
    collision=dict(scan_started_epoch=started,scan_ended_epoch=time.time(),named_paths=[str(x) for x in named],named_sha256={str(x):s.sha(x) for x in named},alien_ids=len(aliases),alien_visible_collisions=alias_visible,alien_manifest_text_collisions=alias_text,seeds=seeds,seed_collisions=seed_collisions,scope='named inventory only')
    native=dict(requests=48,schemas_compiled=48,schema_checks=checks,all_output_schemas_equal_within_block=True,legacy_instruction=p.LEGACY,explicit_instruction=p.EXPLICIT,artificial_prompt_padding=False,prompt_tokens={k:len(v) for k,v in prompts.items()},max_prompt_tokens=max(map(len,prompts.values())),max_prompt_plus_output=max(map(len,prompts.values()))+3072,all_fit8192=all(len(v)+3072<=8192 for v in prompts.values()),request_wire_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in ordered.items()},versions={name:importlib.metadata.version(name) for name in ('vllm','transformers','xgrammar')},elapsed_seconds=time.time()-started,gpu_calls=0,service_calls=0)
    values={'ALLOCATION_AMENDMENT_V2.json':amendment,'PLAN_v2.json':rows,'REQUESTS_v2.json':requests,'ORDERED_REQUESTS_v2.json':ordered,'PROMPT_IDS_v2.json':prompts,'ALIEN_DICTIONARIES_v2.json':p.alien_dictionary(),'COLLISION_AUDIT_v2.json':collision,'CPU_NATIVE_v2.json':native,'PLANNED_NULL_ENDPOINTS_v2.json':[p.null_row(row,'not yet attempted') for row in rows]}
    for name,value in values.items():s.write(s.ROOT/name,value)
    print(json.dumps(dict(requests=len(rows),max_prompt_tokens=native['max_prompt_tokens'],all_fit8192=native['all_fit8192'],legacy_tokens=sorted({len(prompts[r['id']]) for r in rows if r['arm'].endswith('legacy')}),explicit_tokens=sorted({len(prompts[r['id']]) for r in rows if r['arm'].endswith('explicit_slot')}))))
if __name__=='__main__':main()
