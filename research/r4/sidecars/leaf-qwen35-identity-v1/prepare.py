"""One CPU freeze; each full weight shard already hashed once in observed audit."""
import hashlib
import importlib.metadata
import inspect
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
import study as s
import driver


def qualify(d,requests):
    import xgrammar as xg
    from transformers import AutoTokenizer
    ids={};rendered={};checks=[];negative=0
    for model,m in s.MODELS.items():
        tok=AutoTokenizer.from_pretrained(m['path'],local_files_only=True,trust_remote_code=False)
        config=s.read(Path(m['path'])/'config.json');vocab=config.get('text_config',config)['vocab_size']
        compiler=xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tok,vocab_size=vocab),max_threads=2,cache_enabled=True)
        seen=set()
        for r in [r for r in d['plan'] if r['model']==model]:
            body=requests[r['id']];schema=body['structured_outputs']['json'];h=hashlib.sha256(s.serialize(schema).encode()).hexdigest()
            gold=d['batches'][r['batch_id']]['gold'];sample=s.synthetic(gold,gold['labels'][0])
            if h not in seen:
                compiled=compiler.compile_json_schema(s.serialize(schema),any_whitespace=True)
                matcher=xg.GrammarMatcher(compiled)
                if not matcher.accept_string(s.serialize(sample).encode()) or not matcher.is_completed():raise ValueError('legal schema fixture rejected')
                bads=[sample[:-1],sample+[sample[-1]]]
                if r['arm']!='plain':
                    wrong=deepcopy(sample);wrong[0]['tag']='not-source';bads.append(wrong)
                    wrong=deepcopy(sample);wrong[0]={'label':wrong[0]['label'],'tag':wrong[0]['tag']};bads.append(wrong)
                    wrong=deepcopy(sample);wrong[0]['extra']='bad';bads.append(wrong)
                for bad in bads:
                    matcher=xg.GrammarMatcher(compiled)
                    if matcher.accept_string(s.serialize(bad).encode()) and matcher.is_completed():raise ValueError('invalid grammar fixture accepted')
                    negative+=1
                seen.add(h)
            tokens=driver.typed_ids(tok,body)
            if len(tokens)+3072>8192:raise ValueError('complete source does not fit; no truncation')
            tail=tok.decode(tokens[-16:]);is35=model=='qwen35'
            if is35 and not tail.endswith('<|im_start|>assistant\n<think>\n\n</think>\n\n'):raise ValueError('thinking not disabled physically')
            if not is35 and not tail.endswith('<|im_start|>assistant\n'):raise ValueError('Qwen3 native prefix')
            ids[r['id']]=tokens;rendered[r['id']]=dict(tokens=len(tokens),typed_token_ids_sha256=s.digest(tokens),model=model,tail=tail)
            checks.append(dict(id=r['id'],ordered_schema_sha256=h,prompt_tokens=len(tokens),source_context_index=r['context_index']))
        print(s.serialize(dict(model=model,requests=len([r for r in d['plan'] if r['model']==model]),schemas=len(seen))),flush=True)
    for i in range(72):
        a,b=d['plan'][i],d['plan'][i+72];x,y=deepcopy(requests[a['id']]),deepcopy(requests[b['id']]);x.pop('model');y.pop('model')
        if x!=y:raise ValueError('cross-model request changed beyond alias')
    return dict(requests=144,checks=checks,negative_grammar_cases=negative,rendered_prompts=rendered,
        max_input_plus_output=max(len(x) for x in ids.values())+3072,
        versions={k:importlib.metadata.version(k) for k in ('vllm','transformers','xgrammar','httpx')},
        gpu_calls=0,model_calls=0,qualification='CPU native typed request+explicit template kwargs+positive/negative exact grammar; GPU execution not yet qualified'),ids


def main():
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('hide GPU for preparation')
    if (s.ROOT/'SPEC.json').exists():raise ValueError('already frozen')
    paths=set()
    for child in s.SIDE.iterdir():
        if child.is_dir() and child!=s.ROOT:
            for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):
                paths.update(p for p in child.glob(pattern) if p.is_file())
    paths=sorted(paths);pattern=r'\b('+'|'.join(map(str,[s.MASTER,*s.SEEDS]))+r')\b'
    result=subprocess.run(['rg','-n',pattern,*map(str,paths)],capture_output=True,text=True,timeout=60)
    if result.returncode!=1:raise ValueError('seed collision/audit failed: '+result.stdout[:1000])
    s.write_once(s.ROOT/'SEED_AUDIT.json',dict(master=s.MASTER,seeds=s.SEEDS,paths=list(map(str,paths)),exit_code=result.returncode,
        scope='Named top-level ready/spec/recipe/campaign/seed and one-level inputs plans; own namespace excluded, not global'))
    data=s.build_data();d=s.build_design(data);requests={r['id']:s.make_request(d,r) for r in d['plan']}
    q,ids=qualify(d,requests);d['rendered_prompts']=q['rendered_prompts']
    sources={};stats={};observed=s.read(s.ROOT/'SHARD_HASH_OBSERVATION.json')['files_sha256'];weights={}
    for name,m in s.MODELS.items():
        root=Path(m['path']);manifest=root/'local-research-manifest.json'
        if s.sha(manifest)!=m['manifest_sha256']:raise ValueError('cache manifest changed')
        meta=s.read(manifest);sources[str(manifest)]=m['manifest_sha256']
        if meta['huggingface_revision']!=m['revision']:raise ValueError('revision mismatch')
        files={}
        for file,expected in meta['files'].items():
            path=root/file
            actual=observed[str(path)] if file.endswith('.safetensors') else s.sha(path)
            if actual!=expected:raise ValueError('cache file changed: '+str(path))
            files[str(path)]=actual
            if file.endswith('.safetensors'):
                st=path.stat();stats[str(path)]=[st.st_size,st.st_mtime_ns,st.st_ino]
            else:sources[str(path)]=actual
        for file in ('LICENSE','README.md'):
            sources[str(root/file)]=s.sha(root/file)
        if sources[str(root/'LICENSE')]!=meta['license_sha256']:raise ValueError('model license changed')
        weights[name]=dict(checkpoint=m,files_sha256=files,license=meta['license'],acquired_utc=meta['created_at_utc'],adapter=None)
    s.write_once(s.ROOT/'WEIGHTS.json',dict(models=weights,full_shard_hashes_observed=observed,weight_stat_identity=stats,
        note='Full weight shards authenticated once before READY; launch compares immutable stat identities, no per-call rehash'))
    import owned,service
    suite=owned.load_suite()
    # Authenticate inherited executable small-source closure, not unused historical model tensors.
    inherited=s.read(s.SPARSE/'SPEC.json')['source_sha256']
    for path,expected in inherited.items():
        if Path(path).suffix in ('.py','.md','.toml','.sh','.jinja') or Path(path).stat().st_size<8*1024*1024:
            if s.sha(path)!=expected:raise ValueError('inherited source changed: '+path)
            sources[path]=expected
    from prime_rl.configs.inference import InferenceConfig
    installed=Path(importlib.util.find_spec('vllm').origin).parent
    for path in (Path(inspect.getfile(InferenceConfig)),installed/'model_executor/models/registry.py',installed/'model_executor/models/qwen3_5.py',
                 installed/'model_executor/layers/mamba/gdn/qwen_gdn_linear_attn.py',installed/'parser/qwen3.py',
                 installed/'entrypoints/openai/chat_completion/protocol.py',installed/'v1/structured_output/backend_xgrammar.py',
                 service.OLD/'scripts/launch.py',service.OLD/'configs/inference-replica0.json',owned.LIFE):
        sources[str(path)]=s.sha(path)
    for name,value in [('DATA.json',data),('CPU_QUALIFICATION.json',q),('PROMPT_IDS.json',ids),('REQUESTS.json',requests),('DISPATCH.json',d['plan'])]:s.write_once(s.ROOT/name,value)
    tests=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_study.py'],cwd=s.ROOT,capture_output=True,text=True,timeout=120)
    if tests.returncode:raise ValueError(tests.stdout+tests.stderr)
    s.write_once(s.ROOT/'CPU_TESTS.json',dict(returncode=tests.returncode,stdout=tests.stdout,stderr=tests.stderr,
        red='Four initial assertion failures, implementation absent; one malformed fixture fixed before green',gpu_calls=0))
    for path in [*s.ROOT.glob('*.py'),*s.ROOT.glob('*.json'),*s.ROOT.glob('*.md'),*s.ROOT.glob('source/*.py')]:sources[str(path)]=s.sha(path)
    spec=dict(schema=s.ROOT.name,design=d,requests=requests,request_sha256={k:s.digest(v) for k,v in requests.items()},
        ordered_request_sha256={k:hashlib.sha256(s.serialize(v).encode()).hexdigest() for k,v in requests.items()},
        source_sha256=sources,weight_stat_identity=stats,budget=dict(calls=144,per_model_calls=72,collection_seconds=900,
        startup_seconds=300,work_seconds=2400,owned_seconds=2640,parent_seconds=2670,cleanup_seconds_per_service=120),
        frozen_before_inference=True,models=s.MODELS)
    spec['spec_id']=s.digest(spec);s.write_once(s.ROOT/'SPEC.json',spec);driver.verify(spec)
    s.write_once(s.ROOT/'READY.json',dict(status='CPU_READY_PARENT_ACCEPTANCE_REQUIRED',spec_sha256=s.sha(s.ROOT/'SPEC.json'),
        source_sha256={**sources,str(s.ROOT/'SPEC.json'):s.sha(s.ROOT/'SPEC.json')},budget=spec['budget'],
        launch_argv=[owned.PYTHON,str(s.ROOT/'owned.py'),'--directory',str(s.ROOT/'owned/attempt-001')],
        verify_argv=[owned.PYTHON,str(s.ROOT/'owned.py'),'--verify'],cwd=str(s.ROOT),output=str(s.ROOT/'outputs'),
        gpu_calls=0,model_calls=0,full_weights_authenticated_once=True,actual_gpu_kernel_qualification='pending parent launch',
        max_input_plus_output=q['max_input_plus_output'],negative_grammar_cases=q['negative_grammar_cases']))
    print('READY '+s.sha(s.ROOT/'READY.json'),flush=True)


if __name__=='__main__':main()
