"""Authored transport fixtures, never a model call or generated-code execution."""
import asyncio,json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import httpx
import collect,protocol as p,study as s

class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.tok=s.tokenizer()
    def test_actual_32_wires_preserve_schema_native_branches_and_nulls(self):
        plan=s.read(s.ROOT/'PLAN.json');wires=s.read(s.ROOT/'ORDERED_REQUESTS.json')
        prompts=s.read(s.ROOT/'PROMPT_IDS.json');rows={r['id']:r for r in plan}
        key_by_wire={wire:key for key,wire in wires.items()};seen=[]
        def response(request):
            wire=request.content.decode();key=key_by_wire[wire];row=rows[key];seen.append(key)
            ctx=p.contexts()[row['context_index']];body=json.loads(wire)
            self.assertEqual(body['structured_outputs'],p.schema(ctx,row['arm']))
            self.assertNotIn('tools',body)
            content=s.serialize([dict(tag=t,label='neutral') for t in p.expected_tags(ctx,row['arm'])])
            message=dict(role='assistant',content=content);finish='stop'
            if key==plan[0]['id']:
                content='<tool_call>'+s.serialize(dict(name='forbidden',arguments={'code':'NEVER EXECUTE'}))+'</tool_call>'
                message=dict(role='assistant',content=None,tool_calls=[dict(id='cpu',type='function',
                    function=dict(name='forbidden',arguments='{"code":"NEVER EXECUTE"}'))]);finish='tool_calls'
            tokens=self.tok.encode(content,add_special_tokens=False)
            raw=dict(model=s.MODEL['alias'],prompt_token_ids=prompts[key],
                choices=[dict(index=0,message=message,finish_reason=finish,token_ids=tokens)],
                usage=dict(prompt_tokens=len(prompts[key]),completion_tokens=len(tokens),
                    total_tokens=len(prompts[key])+len(tokens)))
            if key==plan[1]['id']:raw['choices'][0]['message']['content']='unauthenticated'
            return httpx.Response(503 if key==plan[2]['id'] else 200,json=raw)
        with tempfile.TemporaryDirectory(prefix='exact-tag-transport-') as tmp:
            root=Path(tmp);endpoint=root/'endpoint.json';output=root/'rollout'
            s.write(endpoint,dict(host='fixture.invalid',port=1234,api_key_env='EXACT_TAG_FIXTURE'))
            with patch.object(s,'verify',lambda:{'identity':'cpu'}),patch.object(s,'tokenizer',lambda:self.tok),patch.object(s.service,'validate_descriptor',lambda *a:None),patch.dict(os.environ,{'EXACT_TAG_FIXTURE':'fixture'}):
                status=asyncio.run(collect.run(endpoint,output,time.time()+120,transport=httpx.MockTransport(response)))
            actual=s.read(output/'ROWS.json');summary=s.read(output/'SUMMARY.json')
            self.assertEqual(len(set(seen)),32);self.assertEqual(status['physical_attempts'],32)
            self.assertEqual(status['available'],30)
            self.assertEqual(actual[0]['score']['strict_correct'],0)
            self.assertTrue(actual[0]['native_verified'])
            self.assertIsNone(actual[1]['score']['strict_correct']);self.assertIsNone(actual[2]['score']['strict_correct'])
            self.assertEqual(summary['costs']['requests_with_usage'],32)
    def test_expired_clock_retains_32_nulls_and_zero_attempts(self):
        def forbidden(request):raise AssertionError('expired clock cannot dispatch')
        with tempfile.TemporaryDirectory(prefix='exact-tag-clock-') as tmp:
            root=Path(tmp);endpoint=root/'endpoint.json';output=root/'rollout'
            s.write(endpoint,dict(host='fixture.invalid',port=1234,api_key_env='EXACT_TAG_FIXTURE'))
            with patch.object(s,'verify',lambda:{'identity':'cpu'}),patch.object(s,'tokenizer',lambda:self.tok),patch.object(s.service,'validate_descriptor',lambda *a:None),patch.dict(os.environ,{'EXACT_TAG_FIXTURE':'fixture'}):
                status=asyncio.run(collect.run(endpoint,output,time.time(),transport=httpx.MockTransport(forbidden)))
            self.assertEqual(status['recorded'],32);self.assertEqual(status['physical_attempts'],0)
            self.assertTrue(all(r['score']['strict_correct'] is None for r in s.read(output/'ROWS.json')))
if __name__=='__main__':unittest.main()
