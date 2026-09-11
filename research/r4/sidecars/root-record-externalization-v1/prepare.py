"""Freeze exact CPU-qualified inputs and immutable launch closure; never launch science."""
import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import time
import collect as c
import protocol as p
import study as s

PROOF = s.ROOT / 'qualification-001/RESULT.json'


def inputs():
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    started=time.time(); proof=s.read(PROOF)
    if not proof['passed'] or proof['native_calls'] != 5 or proof['actual_child_calls'] != 1:
        raise ValueError('actual two-arm native proof required')
    worlds=p.worlds(); plan=p.plan(worlds)
    tools=json.loads(proof['ordered_tools_json'])
    renderer=create_renderer(load_tokenizer(s.MODEL['path']),Qwen3RendererConfig(enable_thinking=True))
    packages={w['id']:{a:p.evidence(w,a,[]) for a in p.REPRESENTATIONS} for w in worlds}
    prefixes={r['id']:c.first_prefix(next(w for w in worlds if w['id']==r['world_id']),
        packages[r['world_id']][r['representation']],r,tools,renderer) for r in plan}
    for name,value in {'WORLDS.json':worlds,'PLAN.json':plan,'PACKAGES.json':packages,
        'HOST_GOLD.json':{w['id']:p.oracle(w['records'],w['query_products']) for w in worlds},
        'NATIVE_TOOLS.json':dict(ordered_json=proof['ordered_tools_json'],actual_cpu_source=str(PROOF)),
        'NATIVE_PREFIXES.json':prefixes,
        'PLANNED_NULL_ENDPOINTS.json':[p.null_row(r,'frozen prelaunch slot') for r in plan]}.items():
        s.write(s.ROOT/name,value)
    receipt=dict(source_worlds=str(p.SOURCE/'WORLDS.json'),source_worlds_sha256=s.sha(p.SOURCE/'WORLDS.json'),
        source_exposure='all four original nativejoin worlds; adaptive mechanism panel, no new world claim',
        historical_extractions_used=0, historical_report_gates_unchanged=True,
        paired_seeds=sorted({r['seed'] for r in plan}), master=p.MASTER,
        seed_check='Before new protocol creation, rg word-boundary981492[0-9]{3} on sidecar PLAN/SEED/protocol/study/READY returned no matches',
        order='four I/E and four E/I orders across hash-shuffled eight blocks',
        prefix_lengths={r['id']:len(prefixes[r['id']]['token_ids']) for r in plan},
        host_serialization_and_render_seconds=time.time()-started, gpu_calls=0, model_service_calls=0)
    s.write(s.ROOT/'INPUT_PROVENANCE.json',receipt)
    print(dict(inputs=16, maximum_initial_plus_output=max(receipt['prefix_lengths'].values())+2560))


def qualify():
    command=[str(s.NATIVE),'-m','unittest','-v','test_externalization','test_owner','test_collect']
    started=time.time()
    result=subprocess.run(command,cwd=s.ROOT,capture_output=True,text=True,timeout=90,
        env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2'})
    for path in s.ROOT.glob('*.py'): ast.parse(path.read_text(),filename=str(path))
    data=dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
        passed=result.returncode==0,elapsed_seconds=time.time()-started,gpu_calls=0,model_service_calls=0,
        source_sha256={str(f):s.sha(f) for f in s.ROOT.glob('*.py')})
    s.write(s.ROOT/'CPU_TESTS.json',data)
    if result.returncode: raise ValueError('CPU qualification failed; retained')
    print(dict(passed=True,sha256=s.sha(s.ROOT/'CPU_TESTS.json')))


def seal():
    import owner
    tests=s.read(s.ROOT/'CPU_TESTS.json'); proof=s.read(PROOF)
    for result,key in ((tests,'source_sha256'),(proof,'qualified_source_sha256')):
        if not result['passed'] or any(s.sha(f)!=pin for f,pin in result[key].items()):
            raise ValueError('fresh matching CPU source qualification required')
    suite=owner.suite()
    if suite.SERVE != s.ROOT/'service_wrapper.py': raise ValueError('wrong actual service namespace')
    source=dict(s.read(s.SIDE/'root-record-interface-v1/READY.json')['source_sha256'])
    source[str(p.SOURCE/'READY_V2.json')]=s.sha(p.SOURCE/'READY_V2.json')
    for path in s.ROOT.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts and 'outputs' not in path.parts and path != s.READY_PATH:
            source[str(path)]=s.sha(path)
    for path,pin in source.items():
        if s.sha(path)!=pin: raise ValueError('immutable closure changed: '+path)
    ready=dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE',source_sha256=source,model=s.MODEL,adapter=None,
        planned_root_endpoints=16,planned_acquisitions=0,exposed_world_clusters=4,arms=list(p.REPRESENTATIONS),
        work_seconds=1080,owned_seconds=1170,outer_seconds=1200,cleanup_seconds=90,startup_seconds=180,
        workers=4,episode_seconds=120,collection_reserve_seconds=30,provider_billing='unknown/not measured',
        native_fixture=str(PROOF),focused_tests=9,seed_master=p.MASTER,
        argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],
        actual_service_wrapper=str(suite.SERVE),gpu_calls=0,model_service_calls=0,prepared_epoch=time.time())
    ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify()
    print(dict(sha256=s.sha(s.READY_PATH),identity=ready['identity'],pins=len(source)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('inputs','qualify','seal'))
    globals()[parser.parse_args().command]()

