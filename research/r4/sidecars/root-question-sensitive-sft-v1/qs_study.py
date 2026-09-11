"""Isolated fixed24/c32 source, exact corpus and qualified native/training aliases."""
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import qs_problem as problem
ROOT=Path(__file__).resolve().parent;SIDE=ROOT.parent;STORE=SIDE.parent;ATTEMPT=ROOT/'outputs/attempt-001'
CF=SIDE/'root-counterfactual-card-signatures-v1';CF_READY_SHA='cc4067934f518f98477fcfda50a185dc9e892e0f87cde644540ac39083d2be22'
assert hashlib.sha256((CF/'READY.json').read_bytes()).hexdigest()==CF_READY_SHA
cf_ready=json.loads((CF/'READY.json').read_text());path=CF/'cf_study.py';assert hashlib.sha256(path.read_bytes()).hexdigest()==cf_ready['source_sha256'][str(path)]
problem_path=CF/'cf_problem.py';assert hashlib.sha256(problem_path.read_bytes()).hexdigest()==cf_ready['source_sha256'][str(problem_path)]
problem_spec=importlib.util.spec_from_file_location('question_sensitive_qualified_cf_problem',problem_path);cf_problem=importlib.util.module_from_spec(problem_spec);problem_spec.loader.exec_module(cf_problem)
previous_problem=sys.modules.get('cf_problem');sys.modules['cf_problem']=cf_problem
try:
    spec=importlib.util.spec_from_file_location('question_sensitive_qualified_cf',path);cf=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cf;spec.loader.exec_module(cf)
finally:
    if previous_problem is None:sys.modules.pop('cf_problem',None)
    else:sys.modules['cf_problem']=previous_problem
sha,read,write,digest,load,aliases=cf.sha,cf.read,cf.write,cf.digest,cf.load,cf.aliases
OLD,JOINT,NATIVE,CHILD_SHA,TRAIN=cf.OLD,cf.JOINT,cf.NATIVE,cf.CHILD_SHA,cf.o.TRAIN
CT,ss=cf.CT,cf.ss
NAMESPACE='question-sensitive-sft72-20260910-v1';SEED=985731003
runtime,interface,joint,qnative=cf.runtime,cf.interface,cf.o.joint,cf.o.qnative
def starting_policy():return cf.selected()
def answer(records,labels,row):return problem.answer(records,labels,row)
def make_task(context,row,gold):return qnative().make_task(context,row['question'],gold,row['id'])
@functools.lru_cache(maxsize=1)
def stack():
    native=qnative().stack().native
    def task(context,prompt,gold,name):
        query=read(ROOT/'inputs/PROMPTS_ACCURATE.json')[name]['plain_query'];value=qnative().make_task(context,query,gold,name)
        if value.data.prompt!=prompt:raise ValueError('exact question-sensitive native prefix')
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native),'task':task}))
def corpus(limit=None):
    directory=ATTEMPT/'capture';plan=read(ROOT/'inputs/TRAIN_PLAN.json')
    if len(plan)!=72:raise ValueError('exact72 source plan')
    if limit is None:
        frozen=read(directory/'CORPUS_READY.json')
        if frozen['identity']!=verify()['identity'] or frozen['examples']!=72:raise ValueError('complete72 captured corpus required')
        for path,pin in frozen['files_sha256'].items():
            if sha(path)!=pin:raise ValueError('captured corpus changed')
    values=[read(directory/r['id']/'TEACHER.json') for r in plan[:limit]]
    import qs_learning as learning
    child_paths=[]
    for coordinate,teacher in zip(plan,values):
        if not teacher['prefix_ids_verified'] or len(teacher['actual_child_records'])!=1 or teacher['masked_history_turns'] or set(teacher['turns'])!={'first_producer','corrective','terminal'}:raise ValueError('one genuine child and three authored root actions required')
        if teacher['episode_id']!=coordinate['id'] or teacher['coordinate']!=coordinate:raise ValueError('captured coordinate mismatch')
        path=Path(teacher['actual_child_records'][0]);expected=directory/coordinate['id']/'physical'
        if path.resolve().parent!=expected.resolve() or not path.exists():raise ValueError('one episode-local actual child record required')
        physical=read(path)
        if physical.get('origin')!='actual c32' or not physical.get('physical_request_attempt'):raise ValueError('genuine acquisition receipt required')
        child_paths.append(str(path.resolve()))
        for turn in teacher['turns'].values():learning.validate_turn(turn)
    if len(set(child_paths))!=len(values):raise ValueError('separate actual acquisition per trajectory')
    return values
def verify():
    ready=read(ROOT/'READY.json')
    if digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('READY identity')
    for path,pin in {**ready['source_sha256'],**ready['input_sha256']}.items():
        if sha(path)!=pin:raise ValueError('READY source changed '+path)
    starting_policy();return ready
