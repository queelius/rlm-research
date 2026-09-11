"""Single-process parent-owned HF conditional replay; never serves, trains or samples."""
import time
ENTRY=time.monotonic()
import argparse
import hashlib
import importlib.metadata
import json
import os
import signal
import sys
from pathlib import Path
import replay

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise ValueError('immutable output exists')
    temporary=path.with_suffix(path.suffix+'.partial')
    with temporary.open('x') as f:json.dump(value,f,separators=(',',':'),ensure_ascii=False,allow_nan=False);f.flush();os.fsync(f.fileno())
    os.replace(temporary,path)

def verify():
    ready=read(ROOT/'READY.json')
    for path,want in ready['source_sha256'].items():
        if sha(path)!=want:raise ValueError('frozen input changed: '+path)
    recipe=read(ROOT/'RECIPE.json');weights=read(ROOT/'WEIGHTS.json')
    for path,identity in weights['stat_identity'].items():
        st=Path(path).stat()
        if [st.st_size,st.st_mtime_ns,st.st_ino]!=identity:raise ValueError('authenticated model shard changed')
    for key,want in recipe['versions'].items():
        if importlib.metadata.version(key)!=want:raise ValueError('inference environment changed: '+key)
    return recipe

def evaluate_units(model,units,output,deadline,device,clock=time.monotonic):
    results=[];stop=None
    for unit in units:
        if clock()>=deadline:stop='work_deadline';break
        result={k:unit[k] for k in ('id','dataset','context_index','position','displayed_gold','named_shifted_gold')}
        result.update(conditions={arm:None for arm in unit['conditions']},complete=False,started_epoch=time.time())
        try:
            for arm,condition in unit['conditions'].items():
                current={'candidates':{},'normalized_probabilities':None};result['conditions'][arm]=current
                for label,candidate in condition['candidates'].items():
                    if clock()>=deadline:raise TimeoutError('work_deadline')
                    current['candidates'][label]=replay.score_candidate(model,candidate['input_ids'],condition['score_start'],device)
                probabilities=replay.normalize_scores({k:v['sequence_logprob'] for k,v in current['candidates'].items()})
                current.update(normalized_probabilities=probabilities,displayed_gold_probability=probabilities[unit['displayed_gold']],
                    named_shifted_gold_probability=probabilities[unit['named_shifted_gold']],argmax_label=max(probabilities,key=probabilities.get))
            result['complete']=True
            result['matching_minus_constant_displayed_probability']=(result['conditions']['matching']['displayed_gold_probability']-result['conditions']['constant']['displayed_gold_probability'])
            result['displayed_vs_shifted_gold_disagree']=unit['displayed_gold']!=unit['named_shifted_gold']
        except BaseException as error:
            stop='work_deadline' if isinstance(error,TimeoutError) else type(error).__name__
            result['error']={'type':type(error).__name__,'message':str(error)[:1500]}
        finally:
            result['ended_epoch']=time.time();atomic(Path(output)/'units'/(unit['id']+'.json'),result);results.append(result)
        if stop:break
    return {'units':results,'stop_reason':stop,'unrun':[u['id'] for u in units[len(results):]]}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');parser.add_argument('--output',type=Path,default=ROOT/'outputs/attempt-001');args=parser.parse_args()
    recipe=verify()
    if args.verify:print('exact source/model stat/environment verified; no model load');return
    gpu=os.environ.get('CUDA_VISIBLE_DEVICES','')
    if not gpu or ',' in gpu:raise ValueError('MAIN must assign exact single GPU/MIG environment')
    output=args.output.resolve()
    if output.parent!=ROOT/'outputs':raise ValueError('output must be new direct owned outputs child')
    output.mkdir(parents=True,exist_ok=False);units=read(ROOT/'UNITS.json');started_epoch=time.time();model=None
    outcome={'units':[],'stop_reason':'not_started','unrun':[u['id'] for u in units]};error=None
    def expired(*_):raise TimeoutError('work_deadline')
    def interrupted(*_):raise InterruptedError('parent termination; preserve partial unit')
    signal.signal(signal.SIGALRM,expired);signal.signal(signal.SIGTERM,interrupted)
    signal.setitimer(signal.ITIMER_REAL,max(.001,ENTRY+recipe['work_seconds']-time.monotonic()))
    atomic(output/'INPUTS.json',{'recipe_sha256':sha(ROOT/'RECIPE.json'),'ready_sha256':sha(ROOT/'READY.json'),
        'units_sha256':sha(ROOT/'UNITS.json'),'started_epoch':started_epoch,'work_seconds':750,'outer_seconds':900,
        'CUDA_VISIBLE_DEVICES':gpu,'versions':recipe['versions'],'argv':sys.argv,'sampled':False,'training':False})
    try:
        import torch
        from transformers import AutoModelForCausalLM
        if not torch.cuda.is_available():raise ValueError('assigned CUDA unavailable; no CPU fallback')
        torch.manual_seed(recipe['master']);torch.cuda.reset_peak_memory_stats()
        load_started=time.monotonic()
        model=AutoModelForCausalLM.from_pretrained(recipe['checkpoint']['path'],local_files_only=True,
            trust_remote_code=False,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':'cuda'})
        model.eval();model.requires_grad_(False)
        atomic(output/'MODEL_LOADED.json',{'seconds':time.monotonic()-load_started,'class':type(model).__name__,
            'attention_backend':model.config._attn_implementation,'dtype':str(next(model.parameters()).dtype),
            'training':model.training,'any_requires_grad':any(p.requires_grad for p in model.parameters())})
        outcome=evaluate_units(model,units,output,ENTRY+recipe['work_seconds'],'cuda')
    except BaseException as exc:
        error={'type':type(exc).__name__,'message':str(exc)[:1500]}
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        memory={}
        if 'torch' in locals() and torch.cuda.is_available():
            memory={'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved()}
            del model;torch.cuda.empty_cache()
        done=[read(p) for p in sorted((output/'units').glob('*.json'))]
        seen={x['id'] for x in done}
        status={'planned_units':32,'recorded_units':len(done),'complete_units':sum(x['complete'] for x in done),
            'candidate_forwards':sum(len(c['candidates']) for x in done for c in x['conditions'].values() if c),
            'unrun':[u['id'] for u in units if u['id'] not in seen],'error':error,'stop_reason':outcome['stop_reason'],
            'elapsed_seconds_including_imports':time.monotonic()-ENTRY,'ended_epoch':time.time(),**memory}
        status['complete']=status['complete_units']==32 and error is None and outcome['stop_reason'] is None
        atomic(output/'STATUS.json',status)
        print(json.dumps(status),flush=True)
    if not status['complete']:raise SystemExit(2)

if __name__=='__main__':main()
