"""CPU exact grammar/prompt freeze; old full shard hashes plus unchanged stat IDs."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
import study as s
import driver


def main():
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':raise ValueError('CPU qualification must hide GPUs')
    if (s.ROOT/'READY.json').exists():raise ValueError('already frozen')
    paths=set()
    for child in s.SIDE.iterdir():
        if child.is_dir() and child!=s.ROOT:
            for pattern in ('*SPEC*.json','*READY*.json','*RECIPE*.json','*CAMPAIGN*.json','*SEED*.json','inputs/*PLAN*.json'):
                paths.update(p for p in child.glob(pattern) if p.is_file())
    command=['rg','-n',r'\b(981318001|981318011|981318021)\b',*map(str,sorted(paths))]
    scan=subprocess.run(command,capture_output=True,text=True,timeout=60)
    if scan.returncode!=1:raise ValueError('fresh seed collision: '+scan.stdout[:1000])
    s.write_once(s.ROOT/'SEED_AUDIT.json',{'argv':command,'returncode':scan.returncode,'scope':'named top-level manifests and one-level input plans, own namespace excluded'})
    oldprepare=s.private('prepare.py',{'range(72)':('range(48)',1),'i+72':('i+48',1),'requests=144':('requests=96',1)},extra={'driver':driver})
    data=s.build_data();d=s.build_design(data);requests={r['id']:s.make_request(d,r) for r in d['plan']}
    q,ids=oldprepare.qualify(d,requests);d['rendered_prompts']=q['rendered_prompts']
    for c in d['contexts']:
        subset=[requests[r['id']] for r in d['plan'] if r['context_index']==c['index']]
        if len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in subset})!=1:raise ValueError('paired physical input differs')
    weights=s.read(s.OLD/'WEIGHTS.json');oldspec=s.read(s.OLD/'SPEC.json');stats=oldspec['weight_stat_identity']
    if weights['weight_stat_identity']!=stats:raise ValueError('old shard identities disagree')
    for path,expected in stats.items():
        st=Path(path).stat()
        if [st.st_size,st.st_mtime_ns,st.st_ino]!=expected:raise ValueError('historically hashed shard changed')
    sources=dict(oldspec['source_sha256'])
    for name in ('READY.json','SPEC.json','WEIGHTS.json'):
        sources[str(s.OLD/name)]=s.sha(s.OLD/name)
    sources.update(data['source_provenance']['source_sha256'])
    sources[str(s.SIDE.parent/'ideas/2026-09-09-fresh-correspondence-main-design.md')]=s.sha(s.SIDE.parent/'ideas/2026-09-09-fresh-correspondence-main-design.md')
    for name,value in [('CPU_QUALIFICATION.json',q),('PROMPT_IDS.json',ids),('REQUESTS.json',requests),('DISPATCH.json',d['plan']),('WEIGHTS.json',weights)]:s.write_once(s.ROOT/name,value)
    tests=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(s.ROOT/'test_study.py')],cwd=s.ROOT,capture_output=True,text=True,timeout=90)
    s.write_once(s.ROOT/('CPU_TESTS.json' if tests.returncode==0 else 'FAILED_TESTS.json'),{'returncode':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,'gpu_calls':0})
    if tests.returncode:raise ValueError(tests.stdout+tests.stderr)
    for path in [*s.ROOT.glob('*.py'),*s.ROOT.glob('*.md'),*s.ROOT.glob('*.json'),*s.ROOT.glob('source/*.py')]:sources[str(path)]=s.sha(path)
    for path,want in sources.items():s.check(path,want)
    spec={'schema':s.ROOT.name,'design':d,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},
      'ordered_request_sha256':{k:__import__('hashlib').sha256(s.serialize(v).encode()).hexdigest() for k,v in requests.items()},
      'source_sha256':sources,'weight_stat_identity':stats,'models':s.MODELS,'frozen_before_inference':True,
      'budget':{'calls':96,'per_model_calls':48,'collection_seconds':600,'startup_seconds':300,'work_seconds':1650,'owned_seconds':1770,'parent_seconds':1800,'final_cleanup_seconds':120},
      'freshness':'exact normalized groups disjoint from frozen bounded named input/reservation crosswalk; no global/pretraining/near-duplicate guarantee'}
    spec['spec_id']=s.digest(spec);s.write_once(s.ROOT/'SPEC.json',spec);driver.verify(spec)
    import owned
    owned.load_suite()
    ready={'status':'CPU_READY_PARENT_ACCEPTANCE_REQUIRED','spec_sha256':s.sha(s.ROOT/'SPEC.json'),
      'source_sha256':{**sources,str(s.ROOT/'SPEC.json'):s.sha(s.ROOT/'SPEC.json')},'budget':spec['budget'],
      'launch_argv':[owned.PYTHON,str(s.ROOT/'owned.py'),'--directory',str(s.ROOT/'owned/attempt-001')],
      'verify_argv':[owned.PYTHON,str(s.ROOT/'owned.py'),'--verify'],'cwd':str(s.ROOT),'output':str(s.ROOT/'outputs'),
      'gpu_calls':0,'model_calls':0,'full_shard_hashes':'reused exact prior authenticated hashes; current stat identities unchanged',
      'max_input_plus_output':q['max_input_plus_output'],'negative_grammar_cases':q['negative_grammar_cases']}
    s.write_once(s.ROOT/'READY.json',ready);print('READY '+s.sha(s.ROOT/'READY.json'),flush=True)


if __name__=='__main__':main()
