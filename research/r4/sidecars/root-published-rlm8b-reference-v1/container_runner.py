"""Owned no-network containers; only JSON events cross the inference socket."""
import http.server,json,os,signal,socketserver,subprocess,tempfile,threading,time,uuid
from pathlib import Path
import rv_study as s
class Server(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):daemon_threads=True
def argv(task_path,bridge,name):
    return [str(s.RUNTIME/'bin/docker'),'run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--pids-limit','128','--memory','2g','--tmpfs','/tmp:rw,nosuid,nodev,size=512m','--workdir','/app','--env','PYTHONPATH=/official:/deps','--env','PYTHONDONTWRITEBYTECODE=1','--env','RLM_REFERENCE_ISOLATED=1','-v',f'{s.OFFICIAL}:/official:ro','-v',f'{s.DEPS}:/deps:ro','-v',f'{s.ROOT/"worker.py"}:/worker.py:ro','-v',f'{task_path}:/task.json:ro','-v',f'{bridge}:/bridge:ro','--entrypoint','/usr/local/bin/python',s.IMAGE,'/worker.py']
def run(task,output,provider,seconds):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);s.write(output/'TASK.json',task)
    bridge=Path(tempfile.mkdtemp(prefix='rv8b.'));name='rv8b-'+uuid.uuid4().hex;events=[];lock=threading.Lock();counter=[0]
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            value=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            with lock:
                index=counter[0];counter[0]+=1;entry=dict(index=index,epoch=time.time(),**value);events.append(entry);s.write(output/'events'/f'{index:04d}.json',entry)
            try:result=provider(value['value']) if value['kind']=='completion' else dict(recorded=True);status=200
            except Exception as e:result=dict(error=f'{type(e).__name__}: {e}');status=400
            data=json.dumps(result).encode();self.send_response(status);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    server=Server(str(bridge/'inference.sock'),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    command=argv(output/'TASK.json',bridge,name);s.write(output/'CONTAINER_COMMAND.json',dict(argv=command,name=name,bridge=str(bridge),deadline=time.time()+seconds))
    error=None;returncode=None
    try:
        with (output/'stdout.log').open('x') as log:
            process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:returncode=process.wait(timeout=max(.1,seconds))
            except subprocess.TimeoutExpired:
                error='endpoint hard deadline';os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=2)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    finally:
        cleanup=subprocess.run([str(s.RUNTIME/'bin/docker'),'rm','--force','--ignore',name],capture_output=True,text=True,timeout=20)
        s.write(output/'CONTAINER_STOPPED.json',dict(name=name,returncode=cleanup.returncode,stdout=cleanup.stdout,stderr=cleanup.stderr))
        server.shutdown();server.server_close();thread.join(timeout=2)
    terminal=next((e['value'] for e in reversed(events) if e['kind']=='terminal'),dict(final=None,error=dict(type='Unreturned',message=error or 'worker exited without terminal')))
    result=dict(terminal=terminal,events=events,returncode=returncode,error=error,container_released=cleanup.returncode==0)
    s.write(output/'WORKER_RESULT.json',result);return result
