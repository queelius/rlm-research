"""Real template/native recorder through actual isolated official worker; fake HTTP only."""
import http.server,json,threading,time
import collect as c,container_runner as cr,paper_prompt,rv_protocol as p,rv_study as s

def test_composed_native_acquisition_FINAL_VAR(tmp_path,monkeypatch):
    tok=s.tokenizer();row=p.plan()[0];task=p.task(row)
    task.update(system=paper_prompt.render((s.ROOT/'inputs/paper-Qwen8B.txt').read_text(),task['context']))
    seen=[]
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));seen.append(body)
            assert not {'tools','tool_choice','structured_outputs'} & body.keys()
            index=len(seen)-1
            text=["```repl\nobserved=llm_query(context)\nprint(observed)\n```",'actual child result',"```repl\nanswer='Answer: '+str(len(observed.split()))\nprint(answer)\n```",'FINAL_VAR(answer)'][index]
            ids=tok.encode(text,add_special_tokens=False);prefix=c.prompt_ids(tok,body['messages'])
            raw=dict(model='qwen3-8b',prompt_token_ids=prefix,choices=[dict(index=0,finish_reason='stop',token_ids=ids,message=dict(role='assistant',content=text))],usage=dict(prompt_tokens=len(prefix),completion_tokens=len(ids),total_tokens=len(prefix)+len(ids)))
            data=json.dumps(raw).encode();self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('RLM8B_SYNTHETIC_FIXTURE_KEY','not-a-real-credential')
    endpoint=dict(host='127.0.0.1',port=server.server_port,api_key_env='RLM8B_SYNTHETIC_FIXTURE_KEY')
    recorder=c.Recorder(row,endpoint,tmp_path/'calls',tok,time.time()+30)
    try:result=cr.run(task,tmp_path/'worker',recorder,30)
    finally:server.shutdown();server.server_close();thread.join()
    assert c.final_capture(result,recorder.calls,recorder.active)
    assert result['terminal']['final']=='Answer: 3' and result['container_released']
    assert [r['role'] for r in recorder.calls]==['root','child','root','root']
    assert all(r['native_verified'] and r['physical_attempt'] for r in recorder.calls)
    assert seen[0]['messages'][0]['content']==task['system']
    assert len(seen[0]['messages'])==3 and task['context'] not in json.dumps(seen[0]['messages'])
    assert seen[1]['messages']==[dict(role='user',content=task['context'])]
    assert len(c.prompt_ids(tok,seen[0]['messages']))>1000
    s.write(tmp_path/'NATIVE_RECEIPT.json',dict(first_messages=seen[0]['messages'],first_prompt_ids=c.prompt_ids(tok,seen[0]['messages']),actual_calls=recorder.calls,template_sha256=s.sha(s.TEMPLATE),rendered_system_sha256=s.digest(task['system'])))
