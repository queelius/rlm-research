"""Frozen local-stage fan-out comparison; model inputs never consult host eligibility."""
import functools
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDS = ROOT.parent / 'b05-eligible-ids-interface-v1'
spec = importlib.util.spec_from_file_location('width_original_ids_study', IDS / 'study.py')
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
SOURCE, source = original.SOURCE, original.source
for name in ('read','sha','digest','write_x','bytes_x','now','load','aliases','tokenizer','renderer',
             'request_body','decode_response','base_owner','canonical_json','call_id',
             'MUSIQUE','MODEL','MODEL_ALIAS','NATIVE'):
    globals()[name] = getattr(original, name)
DATA = ROOT.parents[1] / 'ideas/b05-helper-width-feasibility-2026-09-12'
DATA_SHA = '6e737f09899d168549464d16178547a419558aabd8a6f8cc463477d2a2c5f1c3'
ATTEMPT, READY_RUN = ROOT / 'outputs/attempt-001', ROOT / 'READY_RUN.json'
OWNER_SECONDS, SCIENCE_SECONDS, EXTERNAL_SECONDS = 700, 600, 800
MAX_PHYSICAL, CONCURRENCY = 126, 4
partition = load('width_frozen_partition', DATA / 'freeze.py').partition_child

@functools.lru_cache(None)
def active_roots():
    return [{**r, 'root_id':r['safe_root']['root_id']} for r in read(DATA/'public/PUBLIC.json')['roots']]

@functools.lru_cache(None)
def calls():
    result=[]
    for ci, root in enumerate(active_roots()):
        for repeat in range(2):
            ks=[1,2,4]; rotate=(ci+repeat)%3; ks=ks[rotate:]+ks[:rotate]
            for k in ks:
                for part in range(k):
                    result.append(dict(root_id=root['root_id'],width=root['width'],kind='child',
                        child_index=root['selected_stage'],alternative=repeat,helpers=k,part=part,
                        max_tokens=384//k,seed=202609310000+ci*100+repeat*10+part))
    return result

@functools.lru_cache(None)
def parts(root_id,k):
    root=next(r for r in active_roots() if r['root_id']==root_id)
    return partition(source.b05().extract_child(root['safe_root'],root['selected_stage']),k)

def child(call):
    return parts(call['root_id'],call['helpers'])[call['part']]

@functools.lru_cache(None)
def prompts():
    return {(r['root_id'],r['helpers'],r['part']):r['prompt']
            for r in read(DATA/'public/PROMPTS.json')['model_visible_only']}

def prompt(call):
    return prompts()[call['root_id'],call['helpers'],call['part']]

def gold():
    return {r['root_id']:r['eligible_ids'] for r in read(DATA/'host/GOLD.json')['stages']}

def b05():
    import interface
    return interface

def verify():
    ready=read(READY_RUN)
    assert ready['identity']==digest({k:v for k,v in ready.items() if k!='identity'})
    for path,expected in ready['closure_sha256'].items():
        assert sha(Path(path))==expected,path
    assert sha(DATA/'CANDIDATE_MANIFEST.json')==DATA_SHA
    assert len(calls())==126 and len(active_roots())==9
    assert len({call_id(c) for c in calls()})==126
    frozen=read(ROOT/'INPUTS.json')['calls']
    assert [r['call'] for r in frozen]==calls()
    for row in frozen:
        c=row['call']
        assert row['prompt']==prompt(c)
        assert row['request']==request_body(prompt(c),c['seed'],c['max_tokens'])
        assert len(row['request']['token_ids'])+c['max_tokens']<=8192
    return ready
