"""Private launcher identity recovery; original fresh96 science stays byte-identical."""
import functools
import importlib.util
import os
import signal
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
SCIENCE=ROOT.parent/'leaf-fresh-correspondence-v1'
ORIGINAL_READY_SHA='09e3071801e07bd78d998013b666eeb7e6437c7062228b2a0ef925f87e135545'
PYTHON='/project/alex_phd/envs/prime-rl-5990b1b/bin/python'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

@functools.lru_cache(maxsize=1)
def science():
    import hashlib,json
    ready_path=SCIENCE/'READY.json'
    if hashlib.sha256(ready_path.read_bytes()).hexdigest()!=ORIGINAL_READY_SHA:raise ValueError('original scientific READY changed')
    ready=json.loads(ready_path.read_text())
    for path in (SCIENCE/'study.py',SCIENCE/'service.py',SCIENCE/'owned.py',SCIENCE/'driver.py'):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=ready['source_sha256'][str(path)]:raise ValueError('original science entrypoint changed')
    s=load('fresh_recovery_scientific_study',SCIENCE/'study.py')
    with s.aliases({'study':s}):service=load('fresh_recovery_scientific_service',SCIENCE/'service.py')
    with s.aliases({'study':s,'service':service}):
        owned=load('fresh_recovery_scientific_owned',SCIENCE/'owned.py')
        driver=load('fresh_recovery_scientific_driver',SCIENCE/'driver.py')
    return SimpleNamespace(s=s,service=service,owned=owned,driver=driver)

def load_suite():
    suite=science().owned.load_suite()
    suite.SERVE=ROOT/'source/serve.py'
    suite.c.ROLE=ROOT
    if suite.life.c.ROLE!=ROOT:raise ValueError('lifecycle and suite do not share the authenticated launcher root')
    return suite

def validate_destination(directory,outputs_exist):
    directory=Path(directory).resolve()
    if directory.parent!=ROOT/'owned' or directory.exists() or outputs_exist:
        raise ValueError('new recovery owned namespace and unused original outputs required; no retry')
    return directory

def verify():
    pack=science();s=pack.s;ready=s.read(ROOT/'READY.json')
    for path,want in ready['source_sha256'].items():s.check(path,want)
    if ready['original_ready_sha256']!=ORIGINAL_READY_SHA:raise ValueError('wrong original science relation')
    pack.driver.verify(s.read(SCIENCE/'SPEC.json'))
    load_suite()  # Imports and namespace checks only, no live observation/service.
    return ready

def execute(directory):
    import time
    started=time.time();ready=verify();pack=science();s=pack.s
    directory=validate_destination(directory,(SCIENCE/'outputs').exists())
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu or not os.environ.get('STRICT_RLM_CALIBRATION_API_KEY'):
        raise ValueError('MAIN exclusively assigns GPU/API environment')
    s.write_once(directory.parent/(directory.name+'-RECOVERY.json'),
        {'started_epoch':started,'recovery_ready_sha256':s.sha(ROOT/'READY.json'),
         'original_ready_sha256':ORIGINAL_READY_SHA,'old_failed_attempt':ready['old_failed_attempt'],
         'new_owned_directory':str(directory),'unchanged_scientific_outputs':str(SCIENCE/'outputs'),
         'new_separately_authorized_parent_cap_seconds':1800,'work_deadline_epoch':started+1650,
         'owned_deadline_epoch':started+1770,'no_retry':True})
    def interrupted(sig,frame):raise KeyboardInterrupt('owned signal '+str(sig))
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    # Exact frozen1650/1770 execute, including original48/model driver and finally
    # release. Only load_suite's actual launcher/owner root differs.
    return pack.owned.execute(directory,load_suite(),started)
