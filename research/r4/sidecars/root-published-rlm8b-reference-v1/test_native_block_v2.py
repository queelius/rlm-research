"""Actual isolated execution, native child observation and in-block FINAL_VAR."""
import http.server,json,threading,time
import collect,collect_v2,container_runner,paper_prompt,rv_protocol as p,rv_study as s
def test_actual_native_in_block_FINAL_VAR(tmp_path,monkeypatch):
    tok=s.tokenizer();row=p.plan()[0];task=p.task(row)
    task['system']=paper_prompt.render((s.ROOT/'inputs/paper-Qwen8B.txt').read_text(),task['context'])
    bodies=[]
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));bodies.append(body)
            content=["```repl\nobserved=llm_query(context)\nanswer='Answer: '+str(len(observed.split()))\nprint(answer)\n```",'actual child result',"```repl\nFINAL_VAR('answer')\n``` "][len(bodies)-1]
            ids=tok.encode(content,add_special_tokens=False);prompt=collect.prompt_ids(tok,body['messages'])
            raw=dict(model='qwen3-8b',prompt_token_ids=prompt,choices=[dict(index=0,finish_reason='stop',token_ids=ids,message=dict(role='assistant',content=content))],usage=dict(prompt_tokens=len(prompt),completion_tokens=len(ids),total_tokens=len(prompt)+len(ids)))
            wire=json.dumps(raw).encode();self.send_response(200);self.send_header('Content-Length',str(len(wire)));self.end_headers();self.wfile.write(wire)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('RLM8B_BLOCK_FIXTURE','synthetic-only')
    endpoint=dict(host='127.0.0.1',port=server.server_port,api_key_env='RLM8B_BLOCK_FIXTURE')
    recorder=collect.Recorder(row,endpoint,tmp_path/'calls',tok,time.time()+30)
    try:result=container_runner.run(task,tmp_path/'worker',recorder,30)
    finally:server.shutdown();server.server_close();thread.join()
    assert result['terminal']['final']=='Answer: 3' and result['container_released']
    assert not collect.final_capture(result,recorder.calls,recorder.active)
    assert collect_v2.final_capture(result,recorder.calls,recorder.active)
    assert [r['role'] for r in recorder.calls]==['root','child','root']
    assert len(bodies)==3 and all(r['native_verified'] for r in recorder.calls)
