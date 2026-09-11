import asyncio,json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import httpx
import collect,protocol as p,study as s
class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.tok=s.tokenizer()
    def test_actual_48_wire_collector_entry_and_null_inventory(self):
        plan=s.read(s.ROOT/'PLAN.json');wires=s.read(s.ROOT/'ORDERED_REQUESTS.json');prompts=s.read(s.ROOT/'PROMPT_IDS.json');rows={r['id']:r for r in plan};bywire={v:k for k,v in wires.items()};seen=[]
        def response(request):
            key=bywire[request.content.decode()];row=rows[key];seen.append(key);c=p.contexts()[row['context_index']];content=s.serialize([{'tag':t,'label':'neutral'} for t in p.expected_tags(c,row['arm'])]);tokens=self.tok.encode(content,add_special_tokens=False)
            raw={'model':s.MODEL['alias'],'prompt_token_ids':prompts[key],'choices':[{'index':0,'message':{'role':'assistant','content':content},'finish_reason':'stop','token_ids':tokens}],'usage':{'prompt_tokens':len(prompts[key]),'completion_tokens':len(tokens),'total_tokens':len(prompts[key])+len(tokens)}}
            return httpx.Response(200,json=raw)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);endpoint=root/'endpoint.json';s.write(endpoint,{'host':'fixture.invalid','port':1,'api_key_env':'ALIEN_FIX'});out=root/'rollout'
            with patch.object(s,'verify',lambda:{'identity':'cpu'}),patch.object(s.service,'validate_descriptor',lambda *a:None),patch.dict(os.environ,{'ALIEN_FIX':'fixture'}):status=asyncio.run(collect.run(endpoint,out,time.time()+120,transport=httpx.MockTransport(response)))
            self.assertEqual(len(set(seen)),48,(status,s.read(out/'ROWS.json')[0]));self.assertEqual(status['planned'],48);self.assertEqual(status['recorded'],48);self.assertTrue(status['inventory_complete']);self.assertEqual(status['available'],48);self.assertEqual(len(s.read(out/'PLANNED_NULL_ENDPOINTS.json')),48)
if __name__=='__main__':unittest.main()
