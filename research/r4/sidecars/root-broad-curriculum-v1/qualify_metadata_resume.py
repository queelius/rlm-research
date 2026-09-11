"""Qualification-only metadata correction; frozen campaign/training code is unchanged."""
import argparse
import importlib.metadata
import json
import subprocess
import types
from contextlib import redirect_stderr,redirect_stdout
from pathlib import Path

import campaign_common as c


def native_version(name,lookup=importlib.metadata.version):
    try:
        return lookup(name)
    except importlib.metadata.PackageNotFoundError:
        if name!='peft': raise
        return 'not installed in native serving interpreter'


def main(command):
    c.verify_campaign()
    original_write=c.write_once
    extra=[Path(__file__),c.ROOT/'test_qualification_resume.py',c.ROOT/'QUALIFICATION_FAILURE.json',
           c.ROOT/'qualification-resume.stdout.log',c.ROOT/'qualification-resume.stderr.log']
    if command=='ready':
        import seal
        def publish(path,value):
            if path==c.ROOT/'READY.json':
                value['source_sha256'].update({str(p):c.file_hash(p) for p in extra})
            return original_write(path,value)
        c.write_once=publish
        print(json.dumps(seal.ready()))
        return
    import qualify as q
    q.importlib=types.SimpleNamespace(metadata=types.SimpleNamespace(version=native_version))
    def retain_identical(path,value):
        if path in [c.ROOT/'qualification/SEED_AUDIT.json',c.ROOT/'qualification/TASK_TOKEN_COUNTS.json'] and path.exists():
            if c.read(path)!=value: raise ValueError('existing CPU-only qualification input changed')
            return
        if path==c.ROOT/'qualification/RESULT.json':
            result=subprocess.run([str(c.TRAIN_PYTHON),'-c',
                'import importlib.metadata,json,sys;print(json.dumps({"python":sys.version,"packages":{n:importlib.metadata.version(n) for n in ["torch","peft","transformers","safetensors"]}}))'],
                check=True,capture_output=True,text=True,timeout=30)
            value={**value,'training_interpreter_versions':json.loads(result.stdout),
                'metadata_resume':{'source':str(Path(__file__)),'sha256':c.file_hash(__file__),
                    'prior_failure':str(c.ROOT/'QUALIFICATION_FAILURE.json'),'research_execution_changed':False}}
        return original_write(path,value)
    c.write_once=retain_identical
    with (c.ROOT/'qualification-resume.stdout.log').open('x') as stdout,(c.ROOT/'qualification-resume.stderr.log').open('x') as stderr:
        with redirect_stdout(stdout),redirect_stderr(stderr):
            result=q.qualify(rootless=True)
            print(json.dumps(result,sort_keys=True))
    print(json.dumps({'rootless':result['rootless_fixture'],'gpu_calls':0}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['qualify','ready']);args=parser.parse_args()
    main(args.command)
