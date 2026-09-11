"""Tokenizer-only preparation; full teacher-forced inputs fixed before model inference."""
import ast
import difflib
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
import replay

ROOT=Path(__file__).resolve().parent;STORE=ROOT.parents[1];SIDE=ROOT.parent
FRESH=SIDE/'leaf-fresh-correspondence-v1';SHIFT=SIDE/'leaf-shifted-cue-v1'
TRAIN='/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python'
MASTER=981328001
PINS={FRESH/'SPEC.json':'9e0618c5714b82374328e7679acf65dd8bdd691f1edfd83e072b4281930ec580',
 SHIFT/'study.py':'02bc222d4b78cc6ab7375568630257c7d724450247c9730244b604b808d1d941',
 SIDE/'leaf-qwen35-identity-v1/driver.py':'ea5d97df9746cacedcf4820f95925bca88685bb8710ac6243b98136a412fc689',
 STORE/'ideas/2026-09-09-local-cue-replay-main-design.md':'fb6e4a1dd492181c641a268fcd301ed93a8e2747d459f76b83df4c0fb6933582',
 STORE/'ideas/2026-09-09-local-cue-replay-prompt-amendment.md':'612e64ed11c9adf3da979dc98e9f613317cce76d8c96cf8436c274158819c91e'}
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(name,x):
    with (ROOT/name).open('x') as f:json.dump(x,f,separators=(',',':'),ensure_ascii=False,allow_nan=False);f.write('\n')

def main():
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='' or (ROOT/'READY.json').exists():raise ValueError('CPU-only new freeze required')
    for p,h in PINS.items():assert sha(p)==h,str(p)
    spec=read(FRESH/'SPEC.json');old_ids=read(FRESH/'PROMPT_IDS.json')
    assert sha(FRESH/'PROMPT_IDS.json')==spec['source_sha256'][str(FRESH/'PROMPT_IDS.json')]
    tree=ast.parse((SHIFT/'study.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INSTRUCTION' for t in n.targets));instruction=ast.literal_eval(node.value)
    source=SIDE/'leaf-qwen35-identity-v1/driver.py';node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='typed_ids')
    scope={'deepcopy':deepcopy};exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),scope)
    from transformers import AutoTokenizer
    model=spec['models']['qwen3'];tok=AutoTokenizer.from_pretrained(model['path'],local_files_only=True,trust_remote_code=False)
    contexts=spec['design']['contexts'];units=[];proof=[];requests={};rendered={};mismatch=[]
    for context in contexts:
        index=context['index'];rows=[r for r in spec['design']['plan'] if r['model']=='qwen3' and r['context_index']==index and r['seed']==981318011]
        matching=next(r for r in rows if r['arm']=='matching');constant=next(r for r in rows if r['arm']=='constant')
        old=deepcopy(spec['requests'][matching['id']]);other=spec['requests'][constant['id']]
        assert scope['typed_ids'](tok,old)==old_ids[matching['id']] and scope['typed_ids'](tok,other)==old_ids[constant['id']]
        a,b=old_ids[matching['id']],old_ids[constant['id']]
        mismatch.append({'context':index,'matching_tokens':len(a),'constant_tokens':len(b),'equal':a==b,
            'first_difference':next((i for i,(u,v) in enumerate(zip(a,b)) if u!=v),None)})
        text=old['messages'][1]['content'];before,rest=text.split('Return only',1);rest=rest.split('\nAllowed labels:',1)[1]
        old['messages'][1]['content']=before+instruction+'\nAllowed labels:'+rest
        # Renderer ignores decoding grammar; this request is a rendering reference, never sent.
        old.pop('structured_outputs',None)
        ids=scope['typed_ids'](tok,old);requests[str(index)]=old;rendered[str(index)]=ids
        if not tok.decode(ids[-16:]).endswith('<|im_start|>assistant\n'):raise ValueError('unexpected native assistant prefix')
        diff='\n'.join(difflib.unified_diff(text.splitlines(),old['messages'][1]['content'].splitlines()))
        proof.append({'context':index,'new_prompt_tokens':len(ids),'prompt_ids_sha256':digest(ids),'old_to_new_diff':diff,
            'new_prompt_not_original_fresh_prefix':ids!=a and ids!=b,'tools_unchanged':old['tools']==other['tools']})
        for position in (16,32,48,64):
            conditions={}
            for arm in ('matching','constant','shifted'):
                prefix=replay.history_prefix(context['records'],position,arm);closing='"}]' if position==64 else '"},'
                encoded=replay.encode_candidates(tok,ids,prefix,context['labels'],closing)
                conditions[arm]={'prefix_text':prefix,'closing_boundary':closing,**encoded}
            unit={'context_index':index,'dataset':context['dataset'],'position':position,'displayed_gold':context['records'][position-1]['gold_label'],
                'named_shifted_gold':context['records'][(position-1+17)%64]['gold_label'],'prompt_ids_sha256':digest(ids),'conditions':conditions}
            unit['id']=digest([ROOT.name,MASTER,index,position]);units.append(unit)
    assert len(units)==32 and sum(len(c['candidates']) for u in units for c in u['conditions'].values())==288
    assert all(not x['equal'] for x in mismatch)
    paths=set()
    for directory in SIDE.iterdir():
        if directory.is_dir() and directory!=ROOT:
            for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):paths.update(p for p in directory.glob(pattern) if p.is_file())
    scan=subprocess.run(['rg','-n',rf'\b{MASTER}\b',*map(str,sorted(paths))],text=True,capture_output=True,timeout=60)
    if scan.returncode!=1:raise ValueError('master collision or scan failure: '+scan.stdout[:1000])
    tests=subprocess.run([TRAIN,'-m','pytest','-q','-p','no:cacheprovider','test_replay.py'],cwd=ROOT,text=True,capture_output=True,timeout=90)
    if tests.returncode:raise ValueError(tests.stdout+tests.stderr)
    version=subprocess.run([TRAIN,'-c',"import importlib.metadata,json; print(json.dumps({k:importlib.metadata.version(k) for k in ('torch','transformers','tokenizers','safetensors')}))"],text=True,capture_output=True,check=True)
    installed=subprocess.run([TRAIN,'-c',"import inspect,json; from transformers.models.qwen3.modeling_qwen3 import Qwen3ForCausalLM; from transformers.masking_utils import create_causal_mask; print(json.dumps([inspect.getfile(Qwen3ForCausalLM),inspect.getfile(create_causal_mask)]))"],text=True,capture_output=True,check=True)
    weights=read(FRESH/'WEIGHTS.json');weight=weights['models']['qwen3'];stats={p:v for p,v in weights['weight_stat_identity'].items() if str(model['path']) in p}
    for p,identity in stats.items():
        st=Path(p).stat();assert [st.st_size,st.st_mtime_ns,st.st_ino]==identity
    sources={str(p):h for p,h in PINS.items()}
    sources.update({p:sha(p) for p in json.loads(installed.stdout)})
    for p,h in spec['source_sha256'].items():
        if not p.endswith('.safetensors') and (str(model['path']) in p or p.startswith(str(FRESH))):
            assert sha(p)==h;sources[p]=h
    import inspect
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    for p in (Path(inspect.getfile(ChatCompletionRequest)),Path(tok.__class__.__module__.replace('.','/'))):
        if p.is_file():sources[str(p.resolve())]=sha(p)
    values={'UNITS.json':units,'PROMPT_IDS.json':rendered,'RENDER_REQUESTS.json':requests,'CONTEXTS.json':contexts,
        'PREFIX_CORRECTION_EVIDENCE.json':{'old_matching_constant':mismatch,'new_shared_prompts':proof},
        'QUALIFICATION.json':{'units':32,'conditions':96,'candidate_forwards':288,'gpu_calls':0,'real_model_loaded':False,
            'displayed_shifted_gold_disagreement_units':sum(u['displayed_gold']!=u['named_shifted_gold'] for u in units),
            'max_complete_input_tokens':max(c['complete_input_tokens'] for u in units for arm in u['conditions'].values() for c in arm['candidates'].values()),
            'backed_off_conditions':sum(c['backed_off_prefix_tokens']>0 for u in units for c in u['conditions'].values()),
            'native_versions':{k:importlib.metadata.version(k) for k in ('vllm','transformers','tokenizers')},
            'training_versions':json.loads(version.stdout),'focused_tests':{'returncode':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr},
            'red':'Five desired tests failed before replay.py existed; tiny real CPU causal model only'},
        'SEED_AUDIT.json':{'master':MASTER,'sampling_seeds':[],'scan_exit':scan.returncode,'paths':list(map(str,sorted(paths))),
            'scope':'Named top-level sidecar source specs/readies/recipes/campaigns/seeds and one-level input plans, not global; deterministic forwards'},
        'WEIGHTS.json':{'checkpoint':model,'weight':weight,'stat_identity':stats,'scope':'Prior complete shard hashes, current immutable stat check; no real model loaded in preparation'}}
    for name,value in values.items():write(name,value)
    sources.update({str(p):sha(p) for p in ROOT.iterdir() if p.is_file()})
    recipe={'master':MASTER,'checkpoint':model,'training_python':TRAIN,'versions':json.loads(version.stdout),
        'dtype':'bfloat16','probability_dtype':'float32','attention_backend':'sdpa','use_cache':False,'model_eval':True,
        'units':32,'conditions':96,'candidate_forwards':288,'max_input_tokens':8192,'work_seconds':750,
        'cleanup_seconds':120,'outer_seconds':900,'objective':'Raw complete-candidate logprob sum, finite-label softmax; no length normalization',
        'teacher_forced_prior_gold':True,'new_neutral_prompt_amendment':True,'source_sha256':sources}
    write('RECIPE.json',recipe)
    write('READY.json',{'status':'CPU_READY_MAIN_ACCEPTANCE_REQUIRED','source_sha256':{**sources,str(ROOT/'RECIPE.json'):sha(ROOT/'RECIPE.json')},
        'launch_argv':[TRAIN,str(ROOT/'run.py'),'--output',str(ROOT/'outputs/attempt-001')],
        'verify_argv':[TRAIN,str(ROOT/'run.py'),'--verify'],'cwd':str(ROOT),'outer_seconds':900,
        'work_seconds':750,'cleanup_seconds':120,'gpu_calls':0,'real_model_loaded':False})
    print(json.dumps({'ready_sha256':sha(ROOT/'READY.json'),'max_tokens':values['QUALIFICATION.json']['max_complete_input_tokens']}))

if __name__=='__main__':main()
