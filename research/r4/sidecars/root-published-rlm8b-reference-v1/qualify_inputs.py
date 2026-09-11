"""Freeze CPU-only rendered prefixes, seed inventory and immutable dependency receipts."""
import importlib.metadata,json,platform,subprocess,sys
from pathlib import Path
import collect as c,paper_prompt,rv_protocol as p,rv_study as s
def main():
    native_path=s.ROOT/'qualification-native-001/test_composed_native_acquisiti0/NATIVE_RECEIPT.json'
    actual=s.read(native_path);first=p.task(p.plan()[0]);template=(s.ROOT/'inputs/paper-Qwen8B.txt').read_text()
    a,b=s.tokenizer('base'),s.tokenizer('rlm');assert a.get_vocab()==b.get_vocab()
    frozen=[]
    for row in p.plan()[:24]:
        task=p.task(row);length=len(task['context']);oldlen=len(first['context'])
        assert actual['first_messages'][2]['content'].count(first['query'])==1
        messages=[dict(role='system',content=paper_prompt.render(template,task['context'])),
                  dict(role='user',content=actual['first_messages'][1]['content'].replace(f'{oldlen} total',f'{length} total').replace(f'[{oldlen}]',f'[{length}]')),
                  dict(role='user',content=actual['first_messages'][2]['content'].replace(first['query'],task['query']))]
        ids=c.prompt_ids(a,messages);assert ids==c.prompt_ids(b,messages) and len(ids)+8192<=32768
        if row==p.plan()[0]:assert messages==actual['first_messages'] and ids==actual['first_prompt_ids']
        frozen.append(dict(coordinate=row,messages=messages,prompt_ids=ids,input_tokens=len(ids),context_characters=length))
    s.write(s.ROOT/'inputs/NATIVE_PREFIXES.json',dict(rows=frozen,source_fixture=str(native_path),source_fixture_sha256=s.sha(native_path),vocabulary_equal=True,vocabulary_size=len(a.get_vocab()),construction='First actual historical worker prefix; only context metadata, exactly rendered system, and literal task query substituted for remaining 23 fixed tasks; both real tokenizer outputs compared.',min_tokens=min(x['input_tokens'] for x in frozen),max_tokens=max(x['input_tokens'] for x in frozen)))
    command=['rg','-l',r'\b2026091[01][0-9]{2}\b',str(s.SIDE),'--glob','*.py','--glob','*.json','--glob','*.md','--glob','!**/outputs/**','--glob','!**/qualification*/**','--glob','!**/__pycache__/**','--glob','!**/root-published-rlm8b-reference-v1/**']
    scan=subprocess.run(command,capture_output=True,text=True);assert scan.returncode==1 and not scan.stdout
    s.write(s.ROOT/'inputs/SEED_INVENTORY.json',dict(command=command,returncode=scan.returncode,stdout=scan.stdout,stderr=scan.stderr,master=2026091001,task_seeds=[r['seed'] for r in p.plan()[:24]],scope='Prepared sidecar Python/JSON/Markdown excluding outputs, qualification artifacts and this new sidecar; not an outcome scan. Earlier conflicting981651xxx and981671xxx abandoned before execution.'))
    deps={str(path):s.sha(path) for path in s.DEPS.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc'}
    versions={name:importlib.metadata.version(name) for name in ['torch','transformers','tokenizers','vllm','httpx','pytest']}
    pure={dist.metadata['Name']:dist.version for dist in importlib.metadata.distributions(path=[str(s.DEPS)])}
    s.write(s.ROOT/'inputs/ENVIRONMENT.json',dict(host_python=sys.version,host_executable=sys.executable,versions=versions,pure_dependency_versions=pure,pure_dependency_sha256=deps,worker_python='3.11.16; actual container terminal captured in qualification',image=s.IMAGE,image_wrapper=str(s.RUNTIME/'bin/docker'),new_dependency_install_only=True,full_model_gpu_load_tested=False))
    print(dict(prefix_tokens=[min(x['input_tokens'] for x in frozen),max(x['input_tokens'] for x in frozen)],seed_collisions=0,dependency_files=len(deps),versions=versions))
if __name__=='__main__':main()
