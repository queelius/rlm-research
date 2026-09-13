"""Frozen balanced four-needle transfer schedule; proven MRCR runtime only."""
from __future__ import annotations
import functools, hashlib, importlib.util, json, os, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent; SIDE=ROOT.parent
PARENT=SIDE/'openai-mrcr-fourneedle-ordinal-transfer-eval-v1'
DATA=SIDE/'openai-mrcr-fourneedle-balanced32-transfer-data-v1'; INPUTS=ROOT/'inputs'; READY=ROOT/'READY.json'
OWNER_SECONDS=1100; SCIENCE_SECONDS=900

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); assert spec.loader
    spec.loader.exec_module(m); return m

parent=load('mrcr_balanced32_parent_study',PARENT/'study.py')
for _name in dir(parent):
    if not _name.startswith('_'):globals()[_name]=getattr(parent,_name)
ROOT=Path(__file__).resolve().parent; SIDE=ROOT.parent
PARENT=SIDE/'openai-mrcr-fourneedle-ordinal-transfer-eval-v1'
DATA=SIDE/'openai-mrcr-fourneedle-balanced32-transfer-data-v1'; INPUTS=ROOT/'inputs'; READY=ROOT/'READY.json'
OWNER_SECONDS=1100; SCIENCE_SECONDS=900

@functools.lru_cache(maxsize=1)
def model_inputs():
    value=read(DATA/'MODEL_INPUTS.json')
    if value.get('schema')!='mrcr-fourneedle-balanced32-public-v1' or len(value.get('records',[]))!=32:
        raise ValueError('balanced32 public inventory changed')
    return {'records':[{**row,'source_row_sha256':row['row_sha256']} for row in value['records']]}

def records(phase='long'):
    if phase!='long':raise ValueError('only frozen balanced32 phase')
    return model_inputs()['records']

@functools.lru_cache(maxsize=1)
def schedule(phase='long'):
    if phase!='long':raise ValueError('only frozen balanced32 phase')
    values=[]
    for index,row in enumerate(records()):
        coordinate={'study':ROOT.name,'phase':'long','record_id':row['id'],'source_row_sha256':row['source_row_sha256'],
          'ordered_core_sha256':row['ordered_core_sha256'],'context_sha256':row['prompt_json_sha256'],
          'row_index':index,'repeat':0,'seed':row['seed'],'temperature':0.5}
        values.append({**coordinate,'id':digest(coordinate)})
    return values

def input_dir(phase='long'):
    if phase!='long':raise ValueError('only frozen balanced32 phase')
    return INPUTS

_globals=parent.environment.__globals__
_globals.update(ROOT=ROOT,SIDE=SIDE,DATA=DATA,INPUTS=INPUTS,READY=READY,OWNER_SECONDS=OWNER_SECONDS,
                SCIENCE_SECONDS=SCIENCE_SECONDS,model_inputs=model_inputs,records=records,schedule=schedule,input_dir=input_dir)

def prepare_inputs():
    ready=read(DATA/'DATA_READY.json')
    if sha(DATA/'DATA_READY.json')!='255f0f2c5fa4067eca9f5e1e17c962d893c7c08421466f62fd546d2e74fbdf0e' or ready['identity']!='35cf255465759a18d359616626d39fef81b2c881c0791dd642f6147fe9556f4d':
        raise ValueError('balanced32 DATA_READY changed')
    old=source().v7_study().old_module(); teacher=load('balanced32_teacher',eval_study().TRAINING/'teacher.py')
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    system,tools=teacher._system_and_ordered_tools(); renderer=create_renderer(load_tokenizer(str(BASE)),Qwen3RendererConfig(enable_thinking=True))
    source_gold=read(DATA/'host/HOST_GOLD.json'); selected={row['id']:row for row in records()}; tasks=[]; contexts={}
    for row in selected.values():
        payload=Path(row['prompt_json_path']).read_bytes()
        if hashlib.sha256(payload).hexdigest()!=row['prompt_json_sha256']:raise ValueError('frozen context changed')
        target=INPUTS/'contexts'/(row['prompt_json_sha256']+'.json'); target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=payload:raise ValueError('prepared context differs')
        if not target.exists():target.write_bytes(payload);target.chmod(0o444)
        contexts[row['id']]=row['prompt_json_sha256']
    for index,coordinate in enumerate(schedule()):
        row=selected[coordinate['record_id']]; question=Path(row['final_question_path']).read_text()
        if hashlib.sha256(question.encode()).hexdigest()!=row['final_question_sha256']:raise ValueError('question changed')
        tasks.append(old.MRCRData(idx=index,name=coordinate['id'],prompt=source().root_prompt(question,row['prompt_json_bytes']),
          row_id=row['id'],document_sha256=row['prompt_json_sha256'],arm='fourneedle_balanced32_transfer').model_dump(mode='json',exclude_none=True))
    prefixes={}
    for task,coordinate in zip(tasks,schedule(),strict=True):
        ids=renderer.render([system,{'role':'user','content':task['prompt']}],tools=tools,add_generation_prompt=True).token_ids
        if len(ids)>8192:raise ValueError('neural prefix exceeds 8192')
        prefixes[coordinate['id']]={'token_ids':ids,'token_ids_sha256':digest(ids),'task_prompt_sha256':hashlib.sha256(task['prompt'].encode()).hexdigest()}
    values=[(INPUTS/'tasks.json',tasks),(INPUTS/'PREFIXES.json',prefixes),
      (INPUTS/'PUBLIC.json',{'phase':'long','plan':schedule(),'record_ids':list(selected),'context_sha256_by_record':contexts,
       'seed_namespace':'202609270000+fixed-row-index','requested_ordinal_counts':{str(i):8 for i in range(1,5)},'gold_in_model_input':False}),
      (INPUTS/'HOST_GOLD.json',{k:source_gold[k] for k in selected})]
    for path,value in values:
        if path.exists() and read(path)!=value:raise ValueError('immutable prepared input differs: '+str(path))
        if not path.exists():write_x(path,value)
    (INPUTS/'HOST_GOLD.json').chmod(0o600)
    return {'records':32,'episodes':32,'contexts':32,'prefixes':32,'schedule_sha256':digest(schedule())}

def environment_config(phase='long'):return parent.environment_config(phase)
def environment(phase='long'):return parent.environment(phase)
def official_grade():return parent.official_grade()
def dependencies():return parent.dependencies()
def terminal_hooks():return parent.terminal_hooks()
