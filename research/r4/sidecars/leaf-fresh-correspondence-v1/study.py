"""Fresh label-independent source groups; unchanged released-model component contract."""
import contextlib
import hashlib
import importlib.util
import json
import sys
import unicodedata
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from types import ModuleType

ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;OLD=SIDE/'leaf-qwen35-identity-v1'
FEAS=SIDE.parent/'analyses/fresh-correspondence-data-feasibility-2026-09-09'
PINS={'study.py':'1fe4af21eb476520f93f1732cbb1075d44650761ae65f9c7b4e980415ccf680d',
 'driver.py':'ea5d97df9746cacedcf4820f95925bca88685bb8710ac6243b98136a412fc689',
 'owned.py':'dd2325f034128371d7f719a5cbffd0533629c171acf6189bac64ce29c4fcba78',
 'service.py':'ba11de5f818cb3d44be99a8054b5b36793cb36fde8912918ae3a688cf62b1db8',
 'prepare.py':'3a5623b77e2d60bc042583f6ab2cce1f57d33dd04a5a8b649f119c1551b349aa',
 'source/serve.py':'5d6aab04e29f4f5dd486fbecc03116c81940fb55d615d7462085a8ff9a8164f0'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(path,want):
    if sha(path)!=want:raise ValueError('frozen source changed: '+str(path))


check(OLD/'study.py',PINS['study.py'])
spec=importlib.util.spec_from_file_location('fresh_qualified_component',OLD/'study.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
read,digest,serialize,write_once=old.read,old.digest,old.serialize,old.write_once
MODELS,SPARSE,INPUT_MARKER,ARMS=old.MODELS,old.SPARSE,old.INPUT_MARKER,old.ARMS
MASTER=981318001;SEEDS=[981318011,981318021]
old.ROOT,old.MASTER,old.SEEDS=ROOT,MASTER,SEEDS
sparse=old.sparse


@contextlib.contextmanager
def aliases(mapping):
    previous={k:sys.modules.get(k) for k in mapping};sys.modules.update(mapping)
    try:yield
    finally:
        for k,v in previous.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v


def private(filename,replacements=None,extra=None):
    path=OLD/filename;check(path,PINS[filename]);text=path.read_text()
    for before,(after,count) in (replacements or {}).items():
        if text.count(before)!=count:raise ValueError('counted source seam differs: '+before)
        text=text.replace(before,after)
    module=ModuleType('fresh_private_'+filename.replace('/','_')[:-3]);module.__file__=str(path)
    with aliases({'study':sys.modules[__name__],**(extra or {})}):exec(compile(text,str(path),'exec'),module.__dict__)
    return module


def group(text):return hashlib.sha256(' '.join(unicodedata.normalize('NFKC',text).casefold().split()).encode()).hexdigest()


def choose(rows,excluded,task,n=256):
    groups=defaultdict(list)
    for row in rows:groups[group(row['text'])].append(row)
    conflicts={g for g,v in groups.items() if len({r['label'] for r in v})!=1}
    eligible=set(groups)-set(excluded)-conflicts
    ranked=sorted(eligible,key=lambda g:hashlib.sha256(f'{MASTER}:{task}:selection:{g}'.encode()).hexdigest())
    if len(ranked)<n:raise ValueError('insufficient eligible groups')
    selected=[]
    for g in ranked[:n]:
        first=min(groups[g],key=lambda r:r['index'])
        selected.append({**first,'group_id':g,'source_row_indexes':sorted(r['index'] for r in groups[g]),
          'selection_hash':hashlib.sha256(f'{MASTER}:{task}:selection:{g}'.encode()).hexdigest()})
    return selected,{'rows':len(rows),'groups':len(groups),'conflict_groups':sorted(conflicts),
      'excluded_groups':sorted(set(groups)&set(excluded)),'eligible_groups':len(eligible),'selected_groups':[r['group_id'] for r in selected]}


def build_data():return read(ROOT/'DATA.json')


def build_design(data):
    d=old.build_design(data);d['wall_time_cap_seconds']=600
    if len(d['plan'])!=96 or len(d['contexts'])!=8:raise ValueError('exact96 grid')
    return d


make_request,synthetic,score_labels,score_coordinate,collect_calls=old.make_request,old.synthetic,old.score_labels,old.score_coordinate,old.collect_calls


def summarize(d,records):
    result=old.summarize(d,records);result['cells']=[c for c in result['cells'] if c['planned']]
    result['unit']='four fresh-to-bounded-input-crosswalk contexts/task; two nested seeds; SST text units; invalid0/unavailable NULL'
    return result
