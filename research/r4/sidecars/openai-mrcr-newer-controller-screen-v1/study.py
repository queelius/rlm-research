"""Frozen released-model MRCR controller screen; no model weights loaded here."""
import contextlib
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
STORE=ROOT.parents[1];SIDE=ROOT.parent
SHORT=SIDE/'openai-mrcr-short32-base-calibration-v1'
DATA=SIDE/'openai-mrcr-short-root-data-v1'
MUSIQUE=SIDE/'musique-semantic-depth-pilot-v1'
QWEN35=SIDE/'leaf-qwen35-identity-v1'
INPUTS=ROOT/'inputs';ATTEMPT=ROOT/'outputs/attempt-001'
PREFIX_FILE=INPUTS/'PREFIXES_NATIVE.json'
NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
HEADER='X-Controller-Screen-Coordinate'
ARMS=('qwen3','qwen35')
OWNER_SECONDS,SCIENCE_SECONDS_PER_ARM,EXTERNAL_SECONDS=1800,600,1900


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def write_x(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())


@contextlib.contextmanager
def aliases(mapping,directory):
    old={name:sys.modules.get(name) for name in mapping};before=list(sys.path)
    try:sys.modules.update(mapping);sys.path.insert(0,str(directory));yield
    finally:
        sys.path[:]=before
        for name,value in old.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module


@functools.lru_cache(None)
def short():return load('controller_screen_short',SHORT/'study.py')
@functools.lru_cache(None)
def qwen_source():return load('controller_screen_qwen_source',QWEN35/'study.py')
@functools.lru_cache(None)
def qwen_service():
    with aliases({'study':qwen_source()},QWEN35):return load('controller_screen_qwen_config',QWEN35/'service.py')
@functools.lru_cache(None)
def musique():return load('controller_screen_musique',MUSIQUE/'musique_study.py')
def recorder():return musique().recorder()
def causal():return musique().causal()
def configure_runtime():musique().configure_runtime()
def official_grade():return short().official_grade()

MODELS={
 'qwen3':{'alias':'Qwen3-4B-Instruct-2507-no-research-adapter',
   'path':'/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554',
   'revision':'cdbee75f17c01a7cc42f958dc650907174af0554',
   'manifest_sha256':'19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f'},
 'qwen35':{'alias':'Qwen3.5-4B-no-research-adapter',
   'path':'/project/alex_phd/research-cache/models/Qwen--Qwen3.5-4B--851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a',
   'revision':'851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a',
   'manifest_sha256':'7c1cc9dc3dba23a31bff3ccbefbe23ee46b39cb5dd9b2675ac93c806d2c07e90'}}
MODEL_ALIAS=MODEL=None
def bind_arm(arm):
    global MODEL_ALIAS,MODEL
    assert arm in ARMS
    MODEL_ALIAS=MODELS[arm]['alias'];MODEL=Path(MODELS[arm]['path'])
def selected():return read(INPUTS/'MANIFEST.json')['selected']
def plan(arm=None):return [x for x in read(INPUTS/'SCHEDULE.json') if arm is None or x['arm']==arm]
def binding(arm):return {'schema':'released-controller-screen-binding-v1','arm':arm,'checkpoint':MODELS[arm],
                        'adapter':None,'source_weights_receipt_sha256':sha(QWEN35/'WEIGHTS.json')}


def renderer_config(arm):
    from renderers import DefaultRendererConfig,Qwen35RendererConfig
    return (DefaultRendererConfig(tool_parser='qwen3',reasoning_parser='think',enable_thinking=False)
            if arm=='qwen3' else Qwen35RendererConfig(enable_thinking=False))
@functools.lru_cache(None)
def tokenizer(arm):
    from renderers.base import load_tokenizer
    return load_tokenizer(MODELS[arm]['path'])
@functools.lru_cache(None)
def renderer(arm):
    from renderers import create_renderer
    return create_renderer(tokenizer(arm),renderer_config(arm))


def environment(arm):
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    config=short().environment_config(INPUTS)
    config['taskset']['tasks_file']=str(INPUTS/f'tasks_{arm}.json')
    config['agent']['harness']['max_depth']=0
    config['agent']['max_turns']=2
    env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(config))
    contexts={x['prompt_json_sha256']:Path(x['prompt_json_path']) for x in selected()}
    async def setup(self,trace,runtime):
        payload=contexts[self.data.document_sha256].read_bytes()
        assert hashlib.sha256(payload).hexdigest()==self.data.document_sha256
        await runtime.write('/context.json',payload)
        assert hashlib.sha256(await runtime.read('/context.json')).hexdigest()==self.data.document_sha256
    classes={type(task) for task in env.taskset};assert len(classes)==1
    task=classes.pop();assert task.__module__=='mrcr_rootless_document_baseline_v2'
    task.setup=setup
    sys.modules[task.__module__].NANO_CACHE='/tmp/vf-rlm-'+hashlib.sha256(env.config.agent.harness.version.encode()).hexdigest()
    return env


def verify():
    value=read(ROOT/'READY.json')
    assert value['identity']==digest({k:v for k,v in value.items() if k!='identity'})
    for path,expected in value['closure_sha256'].items():assert sha(path)==expected,path
    assert MODELS==qwen_source().MODELS
    assert len(selected())==8 and len(plan())==16
    assert value['schedule_sha256']==digest(plan())
    for path,expected in value['model_stat_receipts'].items():
        stat=Path(path).stat()
        assert [stat.st_size,stat.st_mtime_ns,stat.st_ino]==expected,path
    return value
