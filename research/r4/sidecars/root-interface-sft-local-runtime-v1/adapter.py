"""Future-only storage amendment: original scientific code, private runtime callbacks."""
import argparse
import asyncio
import contextlib
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'root-interface-sft-v1'
LOCAL=ROOT.parent/'runtime-local-cache-v1'
STORE=Path('/tmp/rlmc.0m4242')
PRIOR_READY='397f3ccc6c701f31ac2702383839d6cdee7de621d7fa91bcac748f828734789a'
LOCAL_READY='87a98f89c42b864bd45f34fe35d077513d6a3083a61f77988fe382109dab28b2'
IMAGE='8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def check(path,want):
    if sha(path)!=want:raise ValueError('frozen identity changed: '+str(path))
def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def validate_store(path=STORE):
    path=Path(path)
    if path!=STORE or not path.is_dir() or path.resolve()!=STORE or path.stat().st_uid!=os.getuid():raise ValueError('qualified ephemeral store unavailable; no fallback')
    if not (path/'root/vfs-images/images.json').is_file():raise ValueError('qualified local image catalog absent')
    images=read(path/'root/vfs-images/images.json')
    if IMAGE not in {r['id'] for r in images}:raise ValueError('exact image absent; no fallback')

def cache_path(output):return STORE/('interface-cache-'+hashlib.sha256(str(output).encode()).hexdigest()[:20])

def rewrite(argv):
    result=list(argv)
    if len(result)>1 and result[1]==str(PRIOR/'evaluate.py'):
        result[1:2]=[str(ROOT/'adapter.py'),'collect']
    return result

def verify():
    check(PRIOR/'READY.json',PRIOR_READY);check(LOCAL/'CPU_READY.json',LOCAL_READY)
    prior,local=read(PRIOR/'READY.json'),read(LOCAL/'CPU_READY.json')
    for path,want in prior['source_sha256'].items():check(path,want)
    for path,want in local['source_and_artifact_sha256'].items():check(path,want)
    if local['image_id']!=IMAGE or local['cpu_affinity']!=[34,35] or local['private_store']!=str(STORE):raise ValueError('runtime amendment identity changed')
    validate_store()
    if (ROOT/'READY.json').exists():
        for path,want in read(ROOT/'READY.json')['source_sha256'].items():check(path,want)
    return prior,local

def delta(output):
    return dict(schema='root-interface-local-runtime-amendment-v1',original_ready_sha256=PRIOR_READY,local_runtime_ready_sha256=LOCAL_READY,image_id=IMAGE,storage_root=str(STORE),wrapper=str(LOCAL/'bin/docker'),wrapper_cpu_affinity=[34,35],verifiers_cache=str(cache_path(output)),both_readout_weights_identical_runtime=True,scientific_data_targets_training_recipe_prompt_seed_sampling_score_unchanged=True,qualification='Composed exact3-call runtime token/alias/sampling equality proof + typed new-catalog free-root3-call proof; no new model/native calls.',limitation='Single69.24→22.30s fixture observation is not an established causal/general speedup; ephemeral store has no fallback.')

def configure_interface(output):
    sys.path.insert(0,str(PRIOR));import interface
    if interface.e.IMAGE!=IMAGE:raise ValueError('scientific interface image changed')
    @contextlib.contextmanager
    def installed(binding,target,plan,public):
        validate_store()
        interface.e.capture.q.ROOTLESS=LOCAL
        os.environ['PATH']=str(LOCAL/'bin')+os.pathsep+os.environ.get('PATH','')
        os.environ['VERIFIERS_CACHE_DIR']=str(cache_path(target))
        write(target/'LOCAL_RUNTIME.json',delta(target))
        with interface.hooks.installed(binding,target,plan,interface.catalogs(public)):yield
    interface.installed=installed
    return interface

async def collect(args):
    verify();configure_interface(args.output)
    old=load('local_runtime_original_evaluate',PRIOR/'evaluate.py')
    return await old.collect(args)

def launch(output):
    verify();sys.path.insert(0,str(PRIOR))
    old=load('local_runtime_original_launch',PRIOR/'launch.py')
    dependencies=old.dependencies
    def local_dependencies():
        suite=dependencies();command=suite.command
        write(output/'RUNTIME_AMENDMENT.json',delta(output))
        def local_command(directory,label,argv,cap,deadline):
            return command(directory,label,rewrite(argv),cap,deadline)
        suite.command=local_command
        return suite
    old.dependencies=local_dependencies
    return old.execute(output)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','launch','collect'));p.add_argument('--output',type=Path,default=ROOT/'outputs/attempt-001');p.add_argument('--binding',type=Path);p.add_argument('--endpoint',type=Path);p.add_argument('--weight',choices=('initial','final'));p.add_argument('--training',type=Path);p.add_argument('--deadline',type=float);a=p.parse_args()
    if a.command=='verify':verify();print('CPU verified, no GPU/model calls')
    elif a.command=='collect':raise SystemExit(asyncio.run(collect(a)))
    else:
        result=launch(a.output);print(result);raise SystemExit(0 if result['complete'] else 1)
