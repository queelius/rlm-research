"""Temperature-1.0 schedule over the fixed completed cp32 G4 scientific inputs."""
from __future__ import annotations
import functools,hashlib,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent
SOURCE_SCREEN=SIDE/'openai-mrcr-procedural-sft32-onpolicy-screen-v1'
SOURCE_READY=SOURCE_SCREEN/'CPU_READY_V4.json';SOURCE_EVAL=SIDE/'openai-mrcr-procedural-sft-eval-v1';CHECKPOINT_EVAL=SIDE/'openai-mrcr-procedural-sft-continue32-eval-v1';SOURCE=SIDE/'openai-mrcr-short32-base-calibration-v1';TRAINING=SIDE/'openai-mrcr-procedural-sft-continue32-v1';TRAIN_OUTPUT=TRAINING/'outputs/attempt-001';DATA=SIDE/'openai-mrcr-short-root-data-v1';INPUTS=ROOT/'inputs';READY=ROOT/'READY.json';OWNER_SECONDS=1100;SCIENCE_SECONDS=900
BASE=Path('/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554');ADAPTED_ALIAS='Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step32';BASE_ALIAS='Qwen3-4B-Instruct-2507-procedural-eval-zero';ROLE_SOURCE=SIDE/'root-only-credit-v1/native_routing.py';NATIVE=Path('/project/alex_phd/envs/prime-rl-5990b1b/bin/python')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_x(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
@functools.lru_cache(None)
def source_study():
    if sha(SOURCE_READY)!='4d954294a98a24dc59b4e8cc9191c386e975a9e727109ba10606717bdea514d8':raise ValueError('completed T0.5 source READY changed')
    return load('mrcr_t1_source_screen_study',SOURCE_SCREEN/'study_v4.py')
def records(phase):
    if phase!='train':raise ValueError('fixed training-only phase')
    return source_study().records('train')
@functools.lru_cache(None)
def schedule(phase):
    if phase!='train':raise ValueError('fixed training-only phase')
    rows=[]
    for index,record in enumerate(records(phase)):
        for repeat in range(4):
            c={'study':ROOT.name,'phase':'train','record_id':record['id'],'source_row_sha256':record['source_row_sha256'],'ordered_core_sha256':record['ordered_core_sha256'],'context_sha256':record['prompt_json_sha256'],'row_index':index,'repeat':repeat,'seed':202609200000+4*index+repeat,'temperature':1.0}
            rows.append({**c,'id':digest(c)})
    return rows
def input_dir(phase):
    if phase!='train':raise ValueError('fixed training-only phase')
    return INPUTS/'train'
@functools.lru_cache(None)
def _bound():
    # Keep the V4 reference module immutable: records() reads it to prove that
    # temperature is the only scientific schedule change.  Bind a separate
    # instance of the original hook-qualified study for execution.
    m=load('mrcr_t1_bound_screen_study',SOURCE_SCREEN/'study.py')
    m.ROOT=ROOT;m.INPUTS=INPUTS;m.READY=READY;m.records=records;m.schedule=schedule;m.input_dir=input_dir;return m
def source():return _bound().source()
def prepare_inputs():return _bound().prepare_inputs()
def environment_config(phase):return _bound().environment_config(phase)
def environment(phase):return _bound().environment(phase)
def dependencies():return _bound().dependencies()
def official_grade():return _bound().official_grade()
def terminal_hooks():return _bound().terminal_hooks()
