"""Counterfactual metadata readout; exact policies, changed public task metadata."""
import functools
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
SIDE=ROOT.parent
ATTEMPT=ROOT/'outputs/attempt-001'
ORIGINAL=SIDE/'root-question-sensitive-sft-v1'
RECOVERY=SIDE/'root-question-sensitive-sft-recovery-v1'
sys.path.insert(0,str(ORIGINAL))
sys.path.insert(0,str(RECOVERY))
import qs_study as base
import qs_binding as old_binding
import postcapture_binding as new_binding
new_binding.OUTPUT=RECOVERY/'outputs/attempt-003'
read,write,sha,digest,load,aliases=base.read,base.write,base.sha,base.digest,base.load,base.aliases
NATIVE=base.NATIVE
CHANGED={'id','namespace','seed','repeat','context_window_id'}

def __getattr__(name):return getattr(base,name)

def build_plan(rows):
    result=[]
    for i,row in enumerate(rows):
        value={**row,'namespace':ROOT.name,'seed':988621001+i,'repeat':1,
               'context_window_id':row['context_window_id']+3000000}
        value.pop('id');value['id']=digest(value);result.append(value)
    return result

def binding(arm):
    if arm=='unchanged':return old_binding.binding(arm)
    if arm=='sft6':return new_binding.binding(arm)
    raise ValueError('fixed policy pair only')

def validate(value,descriptor,path):
    arm=value['question_sensitive']['arm']
    if arm=='unchanged':return old_binding.validate(value,descriptor,path)
    return new_binding.validate(value,descriptor,path)

@functools.lru_cache(maxsize=1)
def stack():
    native=base.qnative().stack().native
    def task(context,prompt,gold,name):
        query=read(ROOT/'inputs/PROMPTS_ACCURATE.json')[name]['plain_query']
        value=base.qnative().make_task(context,query,gold,name)
        if value.data.prompt!=prompt:raise ValueError('exact fresh native prefix')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))

def verify():
    value=read(ROOT/'READY.json')
    if digest({k:v for k,v in value.items() if k!='identity'})!=value['identity']:raise ValueError('identity')
    for path,pin in {**value['source_sha256'],**value['input_sha256']}.items():
        if sha(path)!=pin:raise ValueError('frozen source/input changed '+path)
    for arm in ('unchanged','sft6'):binding(arm)
    return value


def transfer_inputs():
    import copy,json
    contexts=copy.deepcopy([c for c in read(ORIGINAL/'inputs/PUBLIC.json') if c['split']=='protected'])
    for context in contexts:
        context['native_context_id']+=3000000
        for record in context['records']:
            record['user']='u'+str(int(record['user'][1:])+4)
            record['weight']=8+int(digest([ROOT.name,'weight',record['id']])[:16],16)%8
        context['text']=''.join(json.dumps(r,sort_keys=True)+'\n' for r in context['records'])
    rows=build_plan(read(ORIGINAL/'inputs/FREE_PLAN.json'))
    for row in rows:
        row['users']=['u'+str(int(u[1:])+4) for u in row['users']]
        if row['threshold'] is not None:row['threshold']={4:13,8:25}[row['threshold']]
        row['question']=base.problem.question(row).replace('u0, u1, u2, or u3','u4, u5, u6, or u7')
        row.pop('id');row['id']=digest(row)
    return contexts,rows
