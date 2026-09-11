"""Outside physical/native recorder. Never executes a sampled program."""
import argparse,concurrent.futures,json,os,re,threading,time
from pathlib import Path
import httpx
import rv_study as s,rv_protocol as p,paper_prompt,container_runner

def prompt_ids(tok,messages):
    return tok.encode(tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True),add_special_tokens=False)
def authenticate(raw,prompt_ids,tok):
    if raw.get('model')!='qwen3-8b' or len(raw.get('choices',[]))!=1:raise ValueError('model/choice identity')
    c=raw['choices'][0];m=c.get('message') or {};ids=c.get('token_ids');u=raw.get('usage') or {}
    if raw.get('prompt_token_ids')!=prompt_ids or not isinstance(ids,list) or not ids or any(type(i)!=int for i in ids):raise ValueError('native token identity')
    if u.get('prompt_tokens')!=len(prompt_ids) or u.get('completion_tokens')!=len(ids) or u.get('total_tokens')!=len(ids)+len(prompt_ids):raise ValueError('native usage identity')
    if m.get('role')!='assistant' or c.get('finish_reason') not in ('stop','length') or m.get('tool_calls') or m.get('reasoning') or m.get('reasoning_content'):raise ValueError('non-content branch under no-tool/no-reasoning-parser configuration')
    if not isinstance(m.get('content'),str) or tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)!=m['content']:raise ValueError('native text identity')
    return m
def final_capture(result,calls,active):
    terminal=result.get('terminal') or {};final=terminal.get('final')
    if not isinstance(final,str) or terminal.get('error') or active:return False
    roots=[c for c in calls if c['role']=='root'];iterations=[e['value'] for e in result['events'] if e['kind']=='iteration']
    if not roots or not iterations or not roots[-1].get('native_verified'):return False
    text=roots[-1]['content'];it=iterations[-1]
    if it['response']!=text or it['final']!=final:return False
    literal=re.search(r'^\s*FINAL\((.*)\)\s*$',text,re.M|re.S)
    if literal and literal[1].strip()==final:return True
    var=re.search(r'^\s*FINAL_VAR\((.*?)\)',text,re.M|re.S)
    observations=[e['value'] for e in result['events'] if e['kind']=='observation']
    if var:
        name=var[1].strip().strip('"').strip("'");code=f'print(FINAL_VAR({name!r}))'
        return bool(observations and observations[-1]['code']==code and observations[-1]['stdout'].strip()==final and not observations[-1]['stderr'])
    blocks=re.findall(r'```repl\s*\n(.*?)\n```',text,re.S)
    return any(o.get('final_answer')==final and o['code'] in [b.strip() for b in blocks] for o in observations)
class Recorder:
    def __init__(self,row,endpoint,directory,tok,deadline):
        self.row=row;self.endpoint=endpoint;self.directory=directory;self.tok=tok;self.deadline=deadline;self.lock=threading.Lock();self.calls=[];self.active=0;self.seen=set()
    def __call__(self,request):
        role,index=request['role'],request['index'];key=(role,index)
        with self.lock:
            if role not in ('root','child') or type(index)!=int or index<0 or index>=(12 if role=='root' else 36) or key in self.seen or len(self.seen)>=48:raise ValueError('planned call budget or duplicate logical request')
            self.seen.add(key);self.active+=1
        directory=self.directory/f'{role}-{index:03d}';directory.mkdir(parents=True)
        result=dict(role=role,index=index,native_verified=False,physical_attempt=False,usage=None,started_epoch=time.time())
        try:
            prompt=request['prompt'];messages=[dict(role='user',content=prompt)] if isinstance(prompt,str) else prompt
            if not isinstance(messages,list) or any(not isinstance(m,dict) or not isinstance(m.get('content'),str) for m in messages):raise ValueError('official client prompt must contain string messages')
            ids=prompt_ids(self.tok,messages)
            seed=int(s.digest([self.row['seed'],role,index])[:8],16)%2147483647
            body=dict(model='qwen3-8b',messages=messages,temperature=.6,top_p=.95,top_k=20,min_p=0,repetition_penalty=1,presence_penalty=0,frequency_penalty=0,seed=seed,max_tokens=8192 if role=='root' else 4096,return_token_ids=True,cache_salt=s.ROOT.name)
            wire=json.dumps(body,ensure_ascii=False,separators=(',',':')).encode();left=self.deadline-time.time()
            if left<=0:raise TimeoutError('episode deadline before physical request')
            headers={'Authorization':'Bearer '+os.environ[self.endpoint['api_key_env']],'Content-Type':'application/json'}
            def dispatch(req):
                s.write(directory/'REQUEST.json',dict(body=req.content.decode(),expected_prompt_ids=ids,dispatch_epoch=time.time()));result['physical_attempt']=True
            with httpx.Client(trust_env=False,timeout=left,headers=headers,event_hooks={'request':[dispatch]}) as client:
                response=client.post(f'http://{self.endpoint["host"]}:{self.endpoint["port"]}/v1/chat/completions',content=wire)
            s.write(directory/'RESPONSE.json',dict(status=response.status_code,body=response.text,received_epoch=time.time()))
            raw=response.json();result['usage']=raw.get('usage') if isinstance(raw,dict) else None;result['status']=response.status_code;response.raise_for_status()
            m=authenticate(raw,ids,self.tok);result.update(native_verified=True,content=m['content'],finish_reason=raw['choices'][0]['finish_reason'])
            return dict(content=m['content'],usage=raw['usage'])
        except BaseException as e:result['error']=dict(type=type(e).__name__,message=str(e));raise
        finally:
            result['elapsed_seconds']=time.time()-result['started_epoch'];s.write(directory/'RESULT.json',result)
            with self.lock:self.calls.append(result);self.active-=1
def run(policy,endpoint_path,output,deadline):
    ready=s.verify();endpoint=s.read(endpoint_path)
    if endpoint['base_model']!=s.MODELS[policy]:raise ValueError('wrong policy endpoint')
    output.mkdir(parents=True,exist_ok=False);rows=[r for r in s.read(s.ROOT/'inputs/PLAN.json') if r['policy']==policy]
    tasks=s.read(s.ROOT/'inputs/TASKS.json');golds=s.read(s.ROOT/'inputs/HOST_GOLD.json');template=(s.ROOT/'inputs/paper-Qwen8B.txt').read_text();tok=s.tokenizer(policy)
    s.write(output/'PLANNED_NULL_ENDPOINTS.json',[p.null(r,'not yet dispatched') for r in rows]);s.write(output/'RUN.json',dict(identity=ready['identity'],policy=policy,endpoint_sha256=s.sha(endpoint_path),deadline=deadline))
    def episode(row):
        if time.time()>=deadline:return p.null(row,'policy budget before episode')
        directory=output/'episodes'/row['id'];directory.mkdir(parents=True);end=min(deadline,time.time()+120)
        task=tasks[row['id']];task=dict(task,system=paper_prompt.render(template,task['context']),seconds=max(.1,end-time.time()))
        recorder=Recorder(row,endpoint,directory/'calls',tok,end)
        try:
            result=container_runner.run(task,directory/'worker',recorder,max(.1,end-time.time()));available=final_capture(result,recorder.calls,recorder.active)
            value=dict(coordinate=row,score=p.score(result['terminal'].get('final'),available,golds[row['id']]),terminal=result['terminal'],container_released=result['container_released'],calls=recorder.calls,outstanding_requests=recorder.active)
        except BaseException as e:value=dict(p.null(row,f'{type(e).__name__}: {e}'),calls=recorder.calls)
        s.write(directory/'RESULT.json',value);return value
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:values=list(pool.map(episode,rows))
    s.write(output/'ROWS.json',values);status=dict(planned=24,recorded=len(values),available=sum(r['score']['available'] for r in values),correct=sum(r['score']['correct'] is True for r in values),physical_requests=sum(c['physical_attempt'] for r in values for c in r.get('calls',[])))
    s.write(output/'STATUS.json',status);return status
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--policy',required=True,choices=('base','rlm'));ap.add_argument('--endpoint',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--deadline',required=True,type=float);a=ap.parse_args()
    expected=s.ATTEMPT/a.policy
    if a.output.resolve()!=expected/'rollout' or a.endpoint.resolve()!=expected/'service/endpoint-original.json':raise ValueError('exact scientific namespace required')
    print(run(a.policy,a.endpoint,a.output,a.deadline))
