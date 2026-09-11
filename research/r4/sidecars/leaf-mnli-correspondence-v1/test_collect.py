import asyncio
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import httpx
import collect
import protocol as p
import study as s


class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.tokenizer=s.tokenizer()

    def test_actual_80_http_native_calls_wrongroute_zero_mismatch_null_length_observed(self):
        tok=self.tokenizer;plan=s.read(s.ROOT/'PLAN.json');data=s.read(s.ROOT/'DATA.json')
        wires=s.read(s.ROOT/'ORDERED_REQUESTS_V2.json');prompts=s.read(s.ROOT/'PROMPT_IDS_V2.json')
        key_by_wire={v:k for k,v in wires.items()};rows={r['id']:r for r in plan};seen=[]
        def respond(request):
            wire=request.content.decode();key=key_by_wire[wire];row=rows[key];seen.append(key)
            body=json.loads(wire);self.assertNotIn('tools',body);self.assertNotIn('tool_choice',body)
            ctx=p.selected_context(data['contexts'][row['context_index']],row)
            content=s.serialize([dict(tag=r['id'] if row['arm']=='matching' else data['constant'],label='neutral') for r in ctx['records']])
            message=dict(role='assistant',content=content);finish='stop';encoded=content
            if key==plan[0]['id']:
                encoded='<tool_call>'+s.serialize(dict(name='forbidden',arguments={'code':'NEVER EXECUTE'}))+'</tool_call>'
                message=dict(role='assistant',content=None,tool_calls=[dict(id='cpu-tool',type='function',function=dict(name='forbidden',arguments='{"code":"NEVER EXECUTE"}'))]);finish='tool_calls'
            if key==plan[4]['id']:encoded='not JSON';message['content']=encoded
            if key in (plan[3]['id'],plan[4]['id']):finish='length'
            tokens=tok.encode(encoded,add_special_tokens=False)
            raw=dict(model=s.MODEL['alias'],prompt_token_ids=prompts[key],choices=[dict(index=0,message=message,finish_reason=finish,token_ids=tokens)],
                usage=dict(prompt_tokens=len(prompts[key]),completion_tokens=len(tokens),total_tokens=len(prompts[key])+len(tokens)))
            if key==plan[1]['id']:raw['choices'][0]['message']['content']='mismatched physical text'
            return httpx.Response(503 if key==plan[2]['id'] else 200,json=raw)
        with tempfile.TemporaryDirectory(prefix='mnli-native-80-') as directory:
            root=Path(directory);endpoint=root/'endpoint.json';output=root/'rollout'
            s.write(endpoint,dict(host='fixture.invalid',port=1234,api_key_env='MNLI_CPU_FIXTURE_KEY'))
            with patch.object(s,'verify',lambda:{'identity':'cpu-fixture'}),patch.object(s,'tokenizer',lambda:tok),\
                 patch.object(s.service,'validate_descriptor',lambda *args:None),patch.dict(os.environ,{'MNLI_CPU_FIXTURE_KEY':'fixture'}):
                status=asyncio.run(collect.run(endpoint,output,time.time()+120,transport=httpx.MockTransport(respond)))
            result=s.read(output/'ROWS.json');summary=s.read(output/'SUMMARY.json')
            self.assertEqual(len(seen),80);self.assertEqual(len(set(seen)),80);self.assertEqual(status['available'],78)
            self.assertEqual(status['physical_attempts'],80);self.assertTrue(status['inventory_complete'])
            self.assertEqual(result[0]['score']['strict_correct'],0);self.assertTrue(result[0]['native_verified'])
            self.assertIsNone(result[1]['score']['strict_correct']);self.assertIsNone(result[2]['score']['strict_correct'])
            self.assertTrue(result[3]['length_capped']);self.assertTrue(result[3]['score']['contract_valid'])
            self.assertTrue(result[4]['length_capped']);self.assertEqual(result[4]['score']['strict_correct'],0)
            self.assertEqual(summary['singleton_reference']['planned_endpoints'],16)
            self.assertEqual(sum(c['planned_endpoints'] for c in summary['primary'].values()),64)
            self.assertEqual(summary['costs']['requests_with_observed_usage'],80)

    def test_expired_shared_clock_preserves_all_80_nulls_without_requests(self):
        def forbidden(request):raise AssertionError('no time means no HTTP call')
        with tempfile.TemporaryDirectory(prefix='mnli-deadline-') as directory:
            root=Path(directory);endpoint=root/'endpoint.json';output=root/'rollout'
            s.write(endpoint,dict(host='fixture.invalid',port=1234,api_key_env='MNLI_CPU_FIXTURE_KEY'))
            with patch.object(s,'verify',lambda:{'identity':'cpu-fixture'}),patch.object(s,'tokenizer',lambda:self.tokenizer),\
                 patch.object(s.service,'validate_descriptor',lambda *args:None),patch.dict(os.environ,{'MNLI_CPU_FIXTURE_KEY':'fixture'}):
                status=asyncio.run(collect.run(endpoint,output,time.time(),transport=httpx.MockTransport(forbidden)))
            self.assertEqual(status['recorded'],80);self.assertEqual(status['available'],0);self.assertEqual(status['physical_attempts'],0)
            self.assertTrue(all(r['score']['strict_correct'] is None for r in s.read(output/'ROWS.json')))

    def test_frozen_selection_and_grammar_native_proofs(self):
        proof=s.read(s.ROOT/'CPU_NATIVE_V2.json');selection=s.read(s.ROOT/'SELECTION_QUALIFICATION.json')
        self.assertTrue(proof['passed']);self.assertLessEqual(proof['max_input_plus_output'],8192)
        self.assertEqual(proof['tools_advertised'],0);self.assertEqual(proof['requests'],80)
        self.assertEqual(proof['generic_grammar_positive_cases'],9);self.assertEqual(proof['generic_grammar_negative_cases'],4)
        self.assertTrue(selection['per_row_arbitrary_valid_label_mutation_public_invariant'])
        self.assertTrue(selection['all_selected_raw_premises_identical'])
        self.assertEqual(selection['selected_premises'],128)
        tokens=s.read(s.ROOT/'CONTROL_TAG_TOKENS.json');self.assertEqual(tokens['chosen']['tokens'],tokens['modal_target'])
        self.assertNotIn(tokens['chosen']['tag'],tokens['source_field_token_lengths'])
        schema=p.schema(48);text=json.dumps(schema)
        for tag in tokens['source_field_token_lengths']:self.assertNotIn(tag,text)
        self.assertNotIn(tokens['chosen']['tag'],text);self.assertNotIn('uniqueItems',text)


if __name__=='__main__':unittest.main()
