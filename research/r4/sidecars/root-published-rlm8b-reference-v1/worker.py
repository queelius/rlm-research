"""Runs only inside the no-network qualified container, never on the host."""
import asyncio,http.client,json,os,socket,sys,threading,time
sys.path[:0]=['/official','/deps']
from rlm.core import rlm as core
from rlm.clients.base_lm import BaseLM
from rlm.core.types import ModelUsageSummary,UsageSummary
from rlm.environments.local_repl import LocalREPL
from rlm.logger import RLMLogger

class UnixHTTP(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect('/bridge/inference.sock')
def rpc(value):
    client=UnixHTTP('localhost',timeout=125)
    try:
        client.request('POST','/',json.dumps(value),{'Content-Type':'application/json'});response=client.getresponse();data=json.loads(response.read())
        if response.status!=200:raise RuntimeError(data['error'])
        return data
    finally:client.close()
def emit(kind,value):return rpc(dict(kind=kind,value=value))
class Client(BaseLM):
    def __init__(self,model_name,role):super().__init__(model_name);self.role=role;self.cursor=0;self.lock=threading.Lock();self.inputs=self.outputs=self.calls=0;self.last=None
    def request(self,prompt):
        with self.lock:index=self.cursor;self.cursor+=1
        return dict(role=self.role,prompt=prompt,index=index)
    def send(self,request):
        result=rpc(dict(kind='completion',value=request));u=result['usage']
        with self.lock:self.calls+=1;self.inputs+=u['prompt_tokens'];self.outputs+=u['completion_tokens'];self.last=u
        return result['content']
    def completion(self,prompt,model=None):return self.send(self.request(prompt))
    async def acompletion(self,prompt,model=None):return await asyncio.to_thread(self.send,self.request(prompt))
    def get_usage_summary(self):return UsageSummary(model_usage_summaries={self.model_name:ModelUsageSummary(total_calls=self.calls,total_input_tokens=self.inputs,total_output_tokens=self.outputs)})
    def get_last_usage(self):
        u=self.last or {};return ModelUsageSummary(total_calls=1,total_input_tokens=u.get('prompt_tokens',0),total_output_tokens=u.get('completion_tokens',0))
class ObservedREPL(LocalREPL):
    def execute_code(self,code):
        emit('execution_start',dict(code=code));r=super().execute_code(code)
        emit('observation',dict(code=code,stdout=r.stdout,stderr=r.stderr,final_answer=r.final_answer,execution_time=r.execution_time,child_calls=len(r.rlm_calls)))
        return r
class Logger(RLMLogger):
    def log(self,iteration):
        emit('iteration',dict(response=iteration.response,final=iteration.final_answer,prompt=iteration.prompt,code=[b.code for b in iteration.code_blocks]))
class NoFinal(RuntimeError):pass
class BoundedRLM(core.RLM):
    def _default_answer(self,*args):raise NoFinal('root turn limit reached; no fallback request')
def main():
    if os.environ.get('RLM_REFERENCE_ISOLATED')!='1' or not os.path.exists('/bridge/inference.sock'):raise RuntimeError('isolated container entry required')
    task=json.load(open('/task.json'));clients={}
    def client(backend,kwargs):
        role=kwargs['role']
        if role not in clients:clients[role]=Client(kwargs['model_name'],role)
        return clients[role]
    core.get_client=client;core.get_environment=lambda name,kwargs:ObservedREPL(**kwargs)
    # Historical builder performs one format pass. Escape rendered example braces.
    system=task['system'].replace('{','{{').replace('}','}}')
    model=BoundedRLM(backend='openai',backend_kwargs=dict(model_name='qwen3-8b',role='root'),other_backends=['openai'],other_backend_kwargs=[dict(model_name='qwen3-8b',role='child')],environment='local',max_depth=1,max_iterations=task.get('max_iterations',12),max_timeout=task.get('seconds',120),custom_system_prompt=system,logger=Logger(),persistent=False,compaction=False)
    final=None;error=None
    try:final=model.completion(task['context'],root_prompt=task['query']).response
    except BaseException as e:error=dict(type=type(e).__name__,message=str(e))
    finally:model.close()
    emit('terminal',dict(final=final,error=error,python=sys.version,official=core.__file__))
if __name__=='__main__':main()
