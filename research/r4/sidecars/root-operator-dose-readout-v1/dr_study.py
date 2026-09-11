"""Independent readout namespace over immutable training and evaluation inputs."""
import functools
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;TRAINING=SIDE/'root-operator-dose-continuation-v1';ATTEMPT=ROOT/'outputs/attempt-001'
TRAIN_READY_SHA='76f1462596352a423546fe3f338d78247960d7a298871681244e04325b496191'
_spec=importlib.util.spec_from_file_location('dose_readout_training_study',TRAINING/'dose_study.py');dose=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=dose;_spec.loader.exec_module(dose)
dose.check(TRAINING/'READY.json',TRAIN_READY_SHA)
dose.check(TRAINING/'dose_study.py',dose.read(TRAINING/'READY.json')['source_sha256'][str(TRAINING/'dose_study.py')])
sha,read,write,digest=dose.sha,dose.read,dose.write,dose.digest
o=dose.original();aliases=o.aliases;NATIVE=o.NATIVE;OLD=dose.OLD;JOINT=o.JOINT;CHILD_SHA=o.CHILD_SHA

def load(name,path,pin,mapping=None):return o.load(name,path,pin,mapping)
def runtime():return o.runtime()
def interface(output):return o.interface(output)
@functools.lru_cache(maxsize=1)
def protocol():
    module=dose.protocol()
    # Resolve the legacy lazy import against its own immutable study before entering new aliases.
    with aliases({'od_study':o}):module.shared()
    return module
def answer(records,labels,row):return o.answer(records,labels,row)
@functools.lru_cache(maxsize=1)
def stack():
    native=o.qnative().stack().native
    def task(context,prompt,gold,name):
        query=read(ROOT/'inputs/PROMPTS_ACCURATE.json')[name]['plain_query'];value=o.qnative().make_task(context,query,gold,name)
        if value.data.prompt!=prompt:raise ValueError('frozen native prompt changed')
        value.data=value.data.model_copy(update={'source_split':'prepared-catalog-child-train-exposed-root-unexecuted-under-named-inventory' if context['stratum']=='root_new' else 'exposed-repeatability-original-operator-panel'})
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))

def selected(policy):
    if policy=='sft6':
        directory=dose.START;state=read(directory/'state.json')
        for name,pin in state['files_sha256'].items():dose.check(directory/name,pin)
        return dict(checkpoint=str(directory),step=6,adapter_sha256=dose.START_SHA,config_sha256=sha(directory/'adapter_config.json'),state_sha256=sha(directory/'state.json'))
    if policy!='sft24':raise ValueError('fixed6/24 only')
    with aliases({'dose_study':dose}):
        owner=load('dose_readout_training_owner',TRAINING/'dose_owner.py',read(TRAINING/'READY.json')['source_sha256'][str(TRAINING/'dose_owner.py')],{'dose_study':dose})
        chosen=owner.selected(dose.ATTEMPT)
    result=read(dose.ATTEMPT/'training/RESULT.json');identity=read(TRAINING/'READY.json')['identity']
    if result['identity']!=identity:raise ValueError('new training identity')
    for step in range(7,25):
        if read(dose.ATTEMPT/'training'/f'checkpoint-{step:04d}'/'state.json')['identity']!=identity:raise ValueError('checkpoint identity drift')
    directory=Path(chosen['checkpoint'])
    for name,key in [('adapter_model.safetensors','adapter_sha256'),('adapter_config.json','config_sha256'),('state.json','state_sha256')]:
        if sha(directory/name)!=chosen[key]:raise ValueError('actual final selected artifact hash')
    return chosen

def binding(policy,chosen=None):
    chosen=chosen or selected(policy);receipt=read(OLD/'inputs/START_BINDING.json');value=read(receipt['lineage_receipt_path']);value['models'].pop(value['role_map']['root'])
    alias='strict-rlm-qwen3-4b-operator-dose-'+policy+'-v1';model=dict(path=chosen['checkpoint'],adapter_sha256=chosen['adapter_sha256'],config_sha256=chosen['config_sha256'])
    value['models'][alias]=model;value['role_map']['root']=alias;state=read(Path(chosen['checkpoint'])/'state.json')
    value['campaign_policy']={**model,'step':chosen['step'],'state_sha256':chosen['state_sha256'],'optimizer_sha256':state['files_sha256']['optimizer.pt'],'rng_sha256':state['files_sha256']['rng_state.pt']}
    value['study']=ROOT.name;value['operator_dose']=dict(policy=policy,training_ready_sha256=TRAIN_READY_SHA,starting_step=6,final_rule='fixed24 or fixed6 comparator; no selection by outcomes')
    selection=Path(chosen['checkpoint']).parent/'SELECTION.json'
    value['campaign_id']=ROOT.name;value['selection_path']=str(selection);value['selection_sha256']=sha(selection)
    value['selection_semantics']='fixed6 contemporaneous comparator' if policy=='sft6' else 'fixed24 exact Adam/RNG continuation; no readout selection'
    value.pop('diagnostic_no_training',None);value.pop('fixed_root',None)
    if value['models'][value['fixed_child']]['adapter_sha256']!=CHILD_SHA:raise ValueError('fixed child changed')
    return value

def validate(value,descriptor,path):
    if value!=binding(value['operator_dose']['policy']):raise ValueError('actual binding differs')
    j=o.joint();old=load('dose_readout_descriptor_validator',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original})
    old.validate_descriptor(value,descriptor,sha(path))

def verify():
    r=read(ROOT/'READY.json')
    if digest({k:v for k,v in r.items() if k!='identity'})!=r['identity']:raise ValueError('readout identity')
    for path,pin in {**r['source_sha256'],**r['input_sha256']}.items():dose.check(path,pin)
    dose.verify();return r
