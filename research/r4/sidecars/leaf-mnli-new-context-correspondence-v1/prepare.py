"""CPU-only fixed input copy, actual typed native prefixes/grammars, tests and READY."""
import argparse
import copy
import hashlib
import importlib.metadata
import os
from pathlib import Path
import subprocess
import time
import mn_protocol as p
import mn_study as s

def typed_ids(tokenizer,body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    parsed=ChatCompletionRequest.model_validate(copy.deepcopy(body))
    if parsed.tools or parsed.tool_choice not in (None,'none'):raise ValueError('tools advertised')
    return tokenizer.apply_chat_template(body['messages'],tools=None,add_generation_prompt=True,tokenize=True,return_dict=False,**parsed.chat_template_kwargs)

def selection_check():
    import pyarrow.parquet as pq
    receipt=s.read(s.FEASIBILITY/'FEASIBILITY_V2.json')
    if s.sha(s.FEASIBILITY/'FEASIBILITY_V2.json')!=s.FEASIBILITY_SHA:raise ValueError('feasibility changed')
    selector=s.load('mn_new_context_frozen_selector',s.FEASIBILITY/'check_v2.py',receipt['feasibility_script_sha256'])
    if s.sha(selector.PARQUET)!=receipt['parquet_sha256']:raise ValueError('original parquet changed')
    rows=pq.read_table(selector.PARQUET).to_pylist();excluded=set(s.read(s.BASE/'EXPOSURE.json')['exact_text_hits'])
    for path,value in receipt['inventories'].items():
        if s.sha(path)!=value['sha256']:raise ValueError('exposure inventory changed')
        data=s.read(path);contexts=data['contexts'] if isinstance(data,dict) else data
        excluded.update(selector.group(row[key]) for c in contexts for row in c['records'] for key in ('premise','hypothesis'))
    contexts,counts,_=selector.select(rows,excluded)
    mutated=[{**row,'label':int(selector.digest([p.MASTER,'arbitrary-label-mutation',index]),16)%3} for index,row in enumerate(rows)]
    changed,_,_=selector.select(mutated,excluded)
    if contexts!=s.read(s.FEASIBILITY/'SELECTED_INPUTS.json')['contexts'] or selector.public(contexts)!=selector.public(changed):raise ValueError('fixed selection/public label independence')
    return dict(label_mutation_rechecked=True,eligible_by_genre=counts,excluded_texts=len(excluded),source_parquet_sha256=receipt['parquet_sha256'])

def inputs():
    import xgrammar as xg
    started=time.time()
    if s.sha(s.FEASIBILITY/'SELECTED_INPUTS.json')!=s.SELECTED_SHA:raise ValueError('selected bytes changed')
    selection=selection_check()
    # Byte-for-byte immutable data artifact copy, not a source transformation.
    with (s.ROOT/'DATA.json').open('xb') as handle:handle.write((s.FEASIBILITY/'SELECTED_INPUTS.json').read_bytes())
    contexts=p.contexts();plan=p.plan();tok=s.tokenizer();bodies={row['id']:p.request(contexts[row['context_index']],row) for row in plan}
    prefixes={key:typed_ids(tok,body) for key,body in bodies.items()};maximum=max(map(len,prefixes.values()))
    if maximum!=4088 or maximum+3072>8192:raise ValueError('frozen prefix budget differs; no reselection')
    with s.aliases({'study':s}):ancestor=s.load('mn_new_context_request_boundary',s.SOURCE/'protocol.py',s.PINS['protocol.py'])
    ancestor.expected_tags=p.expected_tags
    for row in plan:
        context=contexts[row['context_index']];body=bodies[row['id']]
        if body!=ancestor.request(context,row):raise ValueError('exact prior preamble/sampling/schema boundary changed')
        changed=copy.deepcopy(context)
        for index,record in enumerate(changed['records']):record['gold_label']=p.LABELS[(index*7+1)%3];record['original_pairID']='PRIVATE-MUTATION'
        if body!=p.request(changed,row) or prefixes[row['id']]!=typed_ids(tok,p.request(changed,row)):raise ValueError('host gold/source suffix in actual prompt')
    for ci in range(16):
        rows=[r for r in plan if r['context_index']==ci];a,b=[bodies[r['id']] for r in rows]
        if {k:v for k,v in a.items() if k not in ('messages','structured_outputs')}!={k:v for k,v in b.items() if k not in ('messages','structured_outputs')} or a['messages'][0]!=b['messages'][0]:raise ValueError('paired common envelope changed')
        schemas=[copy.deepcopy(v['structured_outputs']) for v in (a,b)]
        for schema in schemas:
            for item in schema['json']['prefixItems']:item['properties']['tag'].pop('const')
        if schemas[0]!=schemas[1]:raise ValueError('paired schema differs beyond const tags')
    config=s.read(Path(s.MODEL['path'])/'config.json');vocab=config.get('text_config',config)['vocab_size']
    compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocab),max_threads=2,cache_enabled=True);checks=[]
    for context in contexts:
        for arm in p.ARMS:
            compiled=compiler.compile_json_schema(s.serialize(p.schema(context,arm)['json']),any_whitespace=True)
            def accepts(value):
                matcher=xg.GrammarMatcher(compiled);return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()
            tags=p.expected_tags(context,arm)
            for label in p.LABELS:
                if not accepts([dict(tag=tag,label=label) for tag in tags]):raise ValueError('a canonical label was constrained')
            legal=[dict(tag=tag,label=p.LABELS[index%3]) for index,tag in enumerate(tags)]
            if not accepts(legal):raise ValueError('valid tag vector rejected')
            invalid=[]
            bad=copy.deepcopy(legal);bad[0]['tag']='m000000000000';invalid.append(bad)
            bad=copy.deepcopy(legal);bad[0]['label']='unknown';invalid.append(bad)
            bad=copy.deepcopy(legal);bad[0]['extra']='x';invalid.append(bad)
            bad=copy.deepcopy(legal);bad[0]={'label':bad[0]['label'],'tag':bad[0]['tag']};invalid.append(bad)
            invalid.extend([legal[:-1],legal+[legal[-1]]])
            if any(accepts(value) for value in invalid):raise ValueError('invalid exact contract accepted')
            swapped=copy.deepcopy(legal);swapped[0],swapped[1]=swapped[1],swapped[0]
            if accepts(swapped)!=(arm=='constant'):raise ValueError('constant labels must remain unconstrained; matching tag order fixed')
            checks.append(dict(context=context['index'],arm=arm,positions=48,all_three_labels_at_every_position=True,valid_vectors=4,invalid_vectors=6,swap_allowed_only_for_constant=True,schema_sha256=s.digest(p.schema(context,arm))))
    source=dict(original_exact_ready_sha256=s.sha(s.SOURCE/'READY.json'),original_exact_source_pins=s.PINS,selected_origin=str(s.FEASIBILITY/'SELECTED_INPUTS.json'),selected_sha256=s.SELECTED_SHA,feasibility_v2_sha256=s.FEASIBILITY_SHA,invalid_v1_retained_sha256=s.sha(s.FEASIBILITY/'FEASIBILITY.json'),selection=selection,context_cap_unchanged=8192,constant=s.read(s.ROOT/'DATA.json')['constant'],no_resampling=True,no_gold_balancing=True)
    values={'PLAN.json':plan,'REQUESTS.json':bodies,'ORDERED_REQUESTS.json':{key:s.serialize(body) for key,body in bodies.items()},'PROMPT_IDS.json':prefixes,'PUBLIC.json':[dict(index=c['index'],records=[{key:r[key] for key in ('id','premise','hypothesis')} for r in c['records']]) for c in contexts],'SOURCE_BINDING.json':source,'PLANNED_NULL_ENDPOINTS.json':[p.null_row(row,'before any service') for row in plan],
        'CPU_NATIVE.json':dict(passed=True,requests=32,max_input_tokens=maximum,max_input_plus_output=maximum+3072,output_allowance=3072,context_cap=8192,exact_grammar_checks=checks,all32_request_boundary_equal_to_exact_source=True,all32_host_mutation_native_prefix_invariant=True,selection_label_mutation_rechecked=True,tools_advertised=0,gpu_calls=0,model_service_calls=0,versions={name:importlib.metadata.version(name) for name in ('vllm','transformers','xgrammar','httpx','pyarrow')},request_wire_sha256={key:hashlib.sha256(s.serialize(body).encode()).hexdigest() for key,body in bodies.items()},elapsed_seconds=time.time()-started)}
    for name,value in values.items():s.write(s.ROOT/name,value)
    print(dict(requests=32,max_input_plus_output=maximum+3072,grammar_checks=len(checks)))

def qualify():
    argv=[str(s.NATIVE),'-m','unittest','-v','test_science','test_owner','test_collect'];started=time.time()
    result=subprocess.run(argv,cwd=s.ROOT,capture_output=True,text=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    value=dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,passed=result.returncode==0,elapsed_seconds=time.time()-started,gpu_calls=0,model_service_calls=0,source_sha256={str(path):s.sha(path) for path in s.ROOT.glob('*.py')})
    s.write(s.ROOT/('CPU_REPORT_V2.json' if (s.ROOT/'CPU_REPORT.json').exists() else 'CPU_REPORT.json'),value)
    if result.returncode:raise ValueError(result.stderr)
    print(result.stderr)

def seal():
    tests=s.read(s.ROOT/'CPU_REPORT_V2.json');native=s.read(s.ROOT/'CPU_NATIVE.json')
    if not tests['passed'] or not native['passed']:raise ValueError('CPU proofs required')
    for path,pin in tests['source_sha256'].items():
        if s.sha(path)!=pin:raise ValueError('test source changed')
    ancestor=s.read(s.SOURCE/'READY.json');source=dict(ancestor['source_sha256']);source[str(s.SOURCE/'READY.json')]=s.sha(s.SOURCE/'READY.json')
    for name in ('SELECTED_INPUTS.json','FEASIBILITY.json','FEASIBILITY_V2.json','check.py','check_v2.py'):source[str(s.FEASIBILITY/name)]=s.sha(s.FEASIBILITY/name)
    for path in s.ROOT.iterdir():
        if path.is_file() and path!=s.READY_PATH:source[str(path)]=s.sha(path)
    for path,pin in source.items():
        if s.sha(path)!=pin:raise ValueError('source closure changed: '+path)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,model=s.MODEL,adapter=None,planned_endpoints=32,contexts=16,premise_groups=256,pairs_per_context=48,pairs_per_arm=768,arms=list(p.ARMS),research_exposure='new selected premise groups relative to explicit MNLI inputs; not pretraining-unseen',decoder='exact_public_requested_tag_both_arms',labels_unconstrained_by_gold=True,work_seconds=1080,owned_seconds=1170,outer_seconds=1200,cleanup_seconds=90,outer_margin_seconds=30,startup_seconds=180,workers=4,request_seconds=90,seed_master=p.MASTER,provider_billing='unknown/not measured',actual_service_wrapper=str(s.ROOT/'service_wrapper.py'),argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],gpu_calls=0,model_service_calls=0,prepared_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify();print(dict(sha256=s.sha(s.READY_PATH),identity=ready['identity'],pins=len(source)))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('inputs','qualify','seal'));args=parser.parse_args()
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU preparation requires hidden GPUs')
    globals()[args.command]()
