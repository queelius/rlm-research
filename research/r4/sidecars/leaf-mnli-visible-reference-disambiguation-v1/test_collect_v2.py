import asyncio,json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import httpx

import collect_v2 as collect
import protocol_v2 as p


class CollectorV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.tok=collect.s.tokenizer()
    def test_summary_preserves_all_six_arms_and_48_planned_nulls(self):
        rows = [{"coordinate": row, "score": collect.scoring.missing(p.contexts()[row["context_index"]]),
            "physical_attempt": False, "usage_observed": None} for row in p.plan()]
        summary = collect.summarize(rows)
        self.assertEqual(set(summary["arms"]), set(p.ARMS))
        self.assertEqual(sum(cell["planned"] for cell in summary["arms"].values()), 48)
        self.assertEqual(sum(cell["null"] for cell in summary["arms"].values()), 48)

    def test_collector_argv_accepts_only_exact_v2_namespace(self):
        endpoint = collect.s.ATTEMPT / "owned-service/service/endpoint-original.json"
        parsed = collect.owner.validate_argv([str(collect.s.NATIVE), str(collect.s.ROOT / "collect_v2.py"),
            "run", "--endpoint", str(endpoint), "--output",
            str(collect.s.ATTEMPT / "rollout"), "--deadline", "123.0"])
        self.assertEqual(parsed["output"], collect.s.ATTEMPT / "rollout")
        with self.assertRaises(ValueError):
            collect.owner.validate_argv([str(collect.s.NATIVE), str(collect.s.ROOT / "collect_v2.py"),
                "run", "--endpoint", str(endpoint), "--output", "/tmp/wrong",
                "--deadline", "123.0"])

    def test_actual_48_frozen_wires_native_auth_and_null_taxonomy(self):
        rows=p.plan();requests=collect.s.read(collect.s.ROOT/'REQUESTS_v2.json');wires=collect.s.read(collect.s.ROOT/'ORDERED_REQUESTS_v2.json');prompts=collect.s.read(collect.s.ROOT/'PROMPT_IDS_v2.json');bywire={wire:key for key,wire in wires.items()};byid={r['id']:r for r in rows};seen=[]
        def response(request):
            wire=request.content.decode();key=bywire[wire];row=byid[key];seen.append(key);context=p.contexts()[row['context_index']];body=json.loads(wire)
            self.assertEqual(body,requests[key]);self.assertEqual(body['structured_outputs'],p.schema(context,row['arm']));self.assertNotIn('tools',body)
            content=collect.s.serialize([{'tag':tag,'label':'neutral'} for tag in p.requested_tags(context)]);tokens=self.tok.encode(content,add_special_tokens=False);prompt=list(prompts[key])
            if key==rows[0]['id']:prompt[-1]+=1
            raw={'model':collect.s.MODEL['alias'],'prompt_token_ids':prompt,'choices':[{'index':0,'message':{'role':'assistant','content':content},'finish_reason':'stop','token_ids':tokens}],'usage':{'prompt_tokens':len(prompt),'completion_tokens':len(tokens),'total_tokens':len(prompt)+len(tokens)}}
            return httpx.Response(500 if key==rows[1]['id'] else 200,json=raw)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);endpoint=root/'endpoint.json';out=root/'rollout';collect.s.write(endpoint,{'host':'fixture.invalid','port':1,'api_key_env':'VISIBLE_REF_FIX'})
            with patch.object(collect.s,'verify',lambda:{'identity':'cpu'}),patch.object(collect.s.service,'validate_descriptor',lambda *a:None),patch.dict(os.environ,{'VISIBLE_REF_FIX':'fixture'}):
                status=asyncio.run(collect.run(endpoint,out,time.time()+120,transport=httpx.MockTransport(response)))
            actual=collect.s.read(out/'ROWS.json')
        self.assertEqual(len(set(seen)),48);self.assertEqual(status['physical_attempts'],48);self.assertEqual(status['available'],46)
        self.assertIsNone(actual[0]['score']['strict_correct']);self.assertIsNone(actual[1]['score']['strict_correct'])
        self.assertTrue(all(row['score']['strict_correct'] is not None for row in actual[2:]))


if __name__ == "__main__":
    unittest.main()
