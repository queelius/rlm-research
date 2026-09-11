"""CPU freeze and parent-only96 collection using pinned padding/native helpers."""
import argparse
import asyncio
import importlib.util
import json
import os
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import httpx
import study as s

ROOT=s.ROOT
path=s.padding.GRAMMAR/'driver.py'
if s.file_hash(path)!=s.padding.PINS[path]:raise ValueError('frozen native helper changed')
loader=importlib.util.spec_from_file_location('counter_private_native_http',path)
qualified_http=importlib.util.module_from_spec(loader)
loader.loader.exec_module(qualified_http)
BASE=qualified_http.BASE
wire_hook=qualified_http.wire_hook


def weights():
    old={'path':str(s.anchor.corr.ADAPTER),'model_sha256':s.anchor.corr.SELECTED_SHA,'config_sha256':s.anchor.corr.CONFIG_SHA}
    sources={}
    s.anchor.sst.authenticate_weight('old_sft',{'adapter':old,'base_model':BASE},sources)
    return {'models':{'old_sft':old},'base_model':BASE,'source_sha256':sources,
        'selection':'Existing validation-selected c32de only; no new outcome-based selection'}


def qualify(design,requests):
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(BASE['path'],local_files_only=True,trust_remote_code=False)
    tags=[]
    for i in range(65):
        q,p=f'q{i:04d}',f'p{i:04d}'
        qi,pi=tokenizer.encode(q,add_special_tokens=False),tokenizer.encode(p,add_special_tokens=False)
        if len(qi)!=len(pi):raise ValueError('q/p lengths differ; stop before freeze and choose qualified prefix')
        tags.append({'number':i,'source':q,'control':p,'q_tokens':qi,'p_tokens':pi,'length':len(qi)})
    if any(len(tokenizer.encode(prefix,add_special_tokens=False))!=1 for prefix in ['q','p']):
        raise ValueError('disjoint prefixes are not single-token')
    # Parent qualifier groups context/arm/seed: encode presentation into its
    # temporary grouping key only. Actual coordinates and requests never change.
    grouping=deepcopy(design)
    for row in grouping['plan']:
        row['context_index']=row['context_index']*2+row['permutation']
    result=qualified_http.qualify(grouping,requests)
    full_ids={key:qualified_http.typed_prompt_ids(tokenizer,body) for key,body in requests.items()}
    assert all(s.digest(ids)==result['rendered_prompts'][key]['typed_token_ids_sha256'] for key,ids in full_ids.items())
    for i in range(0,96,3):
        bodies=[requests[row['id']] for row in design['plan'][i:i+3]]
        assert len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in bodies})==1
        assert all(b['messages'][0]==bodies[0]['messages'][0] and b['tools']==bodies[0]['tools'] for b in bodies)
    result.update(tag_token_audit=tags,prefix_decision='q and p both single-token; all corresponding full tags equal token length; p retained before inference',
        paired_id_bearing_input_groups=32,full_prompt_ids_sha256=s.digest(full_ids))
    return result,full_ids


def verify(spec):
    if s.digest({k:v for k,v in spec.items() if k!='spec_id'})!=spec['spec_id']:raise ValueError('spec identity changed')
    s.anchor.sst.verify_hashes(spec['source_sha256'])
    expected=s.build_design(s.read(ROOT/'DATA.json'))
    expected['rendered_prompts']=s.read(ROOT/'CPU_QUALIFICATION.json')['rendered_prompts']
    if expected!=spec['design'] or len(expected['plan'])!=96:raise ValueError('fixed design changed')
    for row in expected['plan']:
        body=s.make_request(expected,row)
        if s.serialize(body)!=s.serialize(spec['requests'][row['id']]) or s.digest(body)!=spec['request_sha256'][row['id']]:
            raise ValueError('fixed request changed')


def prepare():
    if (ROOT/'SPEC.json').exists():raise ValueError('already frozen')
    pattern=r'\b('+ '|'.join(str(seed) for seed in s.SEEDS)+r')\b'
    seed_audit=subprocess.run(['rg','-n',pattern,str(s.SIDE),'-g','*SPEC*.json','-g','*READY*.json',
        '-g','*RECIPE*.json','-g','!**/outputs/**','-g','!**/leaf-identity-counter-v1/**'],capture_output=True,text=True,timeout=30)
    if seed_audit.returncode!=1 or seed_audit.stdout:raise ValueError('sampling seed collision/audit failure')
    data=s.build_data(s.read(s.PARENT/'DATA.json'))
    design=s.build_design(data)
    requests={r['id']:s.make_request(design,r) for r in design['plan']}
    qualified,ids=qualify(design,requests)
    design['rendered_prompts']=qualified['rendered_prompts']
    tests=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(ROOT/'test_study.py')],
        capture_output=True,text=True,timeout=90,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'})
    if tests.returncode:raise ValueError(tests.stdout[-3000:])
    weight=weights()
    for name,value in [('DATA.json',data),('CPU_QUALIFICATION.json',qualified),('PROMPT_IDS.json',ids),
        ('WEIGHTS.json',weight),('CPU_TESTS.json',{'returncode':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,
            'prior_red':'Five desired tests failed because study.py absent, pytest111','gpu_calls':0,'fake_http_calls':3}),
        ('SEED_AUDIT.json',{'seeds':s.SEEDS,'master':s.MASTER,'argv':seed_audit.args,'exit_code':seed_audit.returncode,'matches':seed_audit.stdout})]:
        s.write_once(ROOT/name,value)
    sources=dict(s.read(s.PARENT/'SPEC.json')['source_sha256'])
    sources.update({str(p):h for p,h in s.PINS.items()})
    sources.update(weight['source_sha256'])
    import owned
    sources.update({str(p):h for p,h in owned.PINNED.items()})
    sources.update({str(p):s.file_hash(p) for p in [*ROOT.glob('*.py'),*ROOT.glob('*.md'),*ROOT.glob('*.json')]})
    spec={'schema':ROOT.name,'design':design,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},
        'source_sha256':sources,'weight':weight,'budget':{'calls':96,'collection_seconds':600,'owned_seconds':1200,
            'parent_seconds':1230,'cleanup_reserve_seconds':120,'workers':4,'request_timeout_seconds':120,'output_cap':3072,'retries':0},
        'frozen_before_inference':True,'question':'Matching randomized source ID versus changing unrelated ordinal counter versus constant tag'}
    spec['spec_id']=s.digest(spec)
    s.write_once(ROOT/'SPEC.json',spec)
    verify(spec)
    owned.load_suite()
    s.write_once(ROOT/'PREPARED.json',{'status':'CPU_FROZEN_PARENT_LAUNCH_REQUIRED','spec_sha256':s.file_hash(ROOT/'SPEC.json'),
        'spec_id':spec['spec_id'],'calls':96,'sampling_seeds':s.SEEDS,'schemas_compiled':qualified['schemas_compiled'],
        'max_prompt_tokens':qualified['max_prompt_tokens'],'gpu_calls':0,'model_calls':0})
    print(s.serialize(s.read(ROOT/'PREPARED.json')),flush=True)


async def run(endpoint_path, output, overall_start_epoch):
    started = time.time()
    launch = started if overall_start_epoch is None else overall_start_epoch
    if launch > started + 1:
        raise ValueError("future launch epoch")
    spec = s.read(ROOT / "SPEC.json")
    verify(spec)
    endpoint = s.read(endpoint_path)
    qualified_http.validate_descriptor("old_sft", endpoint, spec["weight"])
    if endpoint["model_alias"] != s.ALIAS:
        raise ValueError("endpoint alias differs from all96 frozen requests")
    if output.parent != ROOT / "outputs":
        raise ValueError("output must be direct child of this namespace outputs")
    output.mkdir(parents=True, exist_ok=False)
    s.write_once(output / "SPEC.json", spec)
    s.write_once(output / "ATTEMPT.json", {"entered_epoch": started, "overall_start_epoch": launch,
        "overall_deadline_epoch": launch + 1200, "endpoint_path": str(endpoint_path),
        "endpoint_sha256": s.file_hash(endpoint_path), "endpoint": endpoint,
        "spec_sha256": s.file_hash(ROOT / "SPEC.json"), "service_owner": "owned wrapper"})
    reason, collection_started = None, None
    try:
        async with asyncio.timeout(max(.001, launch + 1080 - time.time())):
            url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
            async with httpx.AsyncClient(headers={"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]},
                    trust_env=False, timeout=120, event_hooks={"request": [wire_hook(spec, output)]}) as client:
                response = await client.get(url.removesuffix("/v1") + "/version")
                response.raise_for_status()
                s.write_once(output / "VERSION_PREFLIGHT.json", response.json())
                if response.json().get("version") != "0.28.0":
                    raise ValueError("unqualified live vLLM version")
                response = await client.get(url + "/models")
                response.raise_for_status()
                qualified_http.validate_live_models({"old_sft": endpoint}, response.json())
                s.write_once(output / "MODELS_PREFLIGHT.json", response.json())
                collection_started = time.time()
                left = min(600, launch + 1080 - collection_started)
                if left <= 0:
                    raise TimeoutError("no collection time remains")
                _, reason = await s.collect_calls(client, url, spec, output, time.monotonic() + left)
    except TimeoutError:
        reason = "owned_work_deadline"
    except Exception as error:
        reason = "preflight_or_runtime_error:" + type(error).__name__
        s.write_once(output / "ERROR.json", {"type": type(error).__name__, "message": str(error)[:1200]})
    finally:
        records = [s.read(p) for p in sorted((output / "calls").glob("*.json"))]
        analysis = s.summarize(spec["design"], records)
        s.write_once(output / "analysis.json", analysis)
        physical = [p for c in analysis["coordinates"] for p in c["physical_prompts"]]
        if any(p["typed_template_equal"] is not True or p["reported_usage_length_equal"] is not True for p in physical):
            reason = reason or "physical_prompt_identity_unverified"
        seen = {r["coordinate"]["id"] for r in records}
        s.write_once(output / "STATUS.json", {"planned": 96, "recorded": len(records), "stop_reason": reason,
            "actual_typed_prompt_matches": sum(p["typed_template_equal"] is True for p in physical),
            "collection_seconds": time.time() - collection_started if collection_started else None,
            "overall_elapsed_seconds": time.time() - launch,
            "unrun": [r["id"] for r in spec["design"]["plan"] if r["id"] not in seen]})
    return 0 if reason is None and len(records) == 96 else 2



def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['prepare','verify','run'])
    parser.add_argument('--endpoint',type=Path)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/attempt-001')
    parser.add_argument('--overall-start-epoch',type=float)
    args=parser.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='verify':verify(s.read(ROOT/'SPEC.json'));print('verified',flush=True)
    else:
        if not args.endpoint:parser.error('actual endpoint required')
        raise SystemExit(asyncio.run(run(args.endpoint.resolve(),args.output_dir.resolve(),args.overall_start_epoch)))


if __name__=='__main__':main()
