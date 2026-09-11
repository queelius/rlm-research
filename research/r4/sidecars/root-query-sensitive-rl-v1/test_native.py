import asyncio
import importlib
import json
from pathlib import Path
import unittest
import qsr_data as d

class NativeTests(unittest.TestCase):
    def test_endpoint_authentication_replays_the_actual_cpu_native_final(self):
        import qsr_study as s
        import qsr_metrics as m
        row={**s.candidate_plan(1)[0],'id':'QSR_CPU_NATIVE_HEX4','seed':981381901};path=s.ROOT/'qualification-native-001'
        old=s.read(s.SIDE/'leaf-role-routing-v1/BOUND_WEIGHTS.json');child='strict-rlm-qwen3-4b-role-sft-selected-v1';root='qsr-CPU-root-low66c';initial=s.fixed_start()
        binding={**old,'models':{root:{k:initial[k] for k in ('path','adapter_sha256','config_sha256')},child:old['models'][child]},'role_map':dict(root=root,children=[child]),'fixed_child':child}
        result=m.endpoint(s.read(path/'EPISODE.json'),path,dict(binding=binding),row)
        self.assertTrue(result['available'],result);self.assertEqual(result['reply'],'Answer: 0');self.assertEqual(result['cost']['calls'],3)
    def test_exact_helper_catalog_schema_supports_new_ids_and_four_fields(self):
        n=importlib.import_module('qsr_native');context=d.build()['PUBLIC.json'][0];batch=context['records'][:4]
        contract=n.stack().interface.hooks.contract;request=contract.batch.request_for(batch)
        self.assertEqual(json.loads(request.split('\nRecords: ')[1]),[dict(id=r['id'],text=r['text']) for r in batch])
        catalog=n.stack().interface.catalogs({context['id']:context})[str(context['native_context_id'])]
        matched=contract.match_request(request,catalog);self.assertTrue(matched['matched']);self.assertEqual(list(matched['schema']['properties']),[r['id'] for r in batch])
        labels={r['id']:'entity' for r in batch};self.assertEqual(contract.batch.strict_map(json.dumps(labels),[r['id'] for r in batch]),labels)
        self.assertTrue(all(__import__('re').fullmatch(r'q[0-9a-f]{12}',r['id']) for r in batch))
        with self.assertRaises(ValueError):contract.batch.strict_map(json.dumps({'q0001':'entity'}),[r['id'] for r in batch])
    def test_actual_native_operator_scope_conditioning_and_no_host_label_leak(self):
        self.assertTrue((Path(__file__).parent/'qsr_native.py').exists(),'native query task not implemented')
        n=importlib.import_module('qsr_native');v=d.build();context=v['PUBLIC.json'][0]
        queries=[d.query(context,'count','single'),d.query(context,'distinct','single'),d.query(context,'count','all')]
        tasks=[n.make_task(context,d.question(q),4,'fixture-'+str(i)) for i,q in enumerate(queries)]
        self.assertEqual(len({tuple(n.first_prefix(t)) for t in tasks}),3)
        changed_labels={key:'description and abstract concept' for key in v['HOST_GOLD.json'][context['id']]['labels']}
        changed=n.make_task(context,d.question(queries[0]),d.answer(context['records'],changed_labels,queries[0]),'different-host-truth')
        self.assertEqual(n.first_prefix(tasks[0]),n.first_prefix(changed))
        class Memory:
            def __init__(self):self.files={}
            async def write(self,name,value):self.files[name]=value
        async def capture(task):
            runtime=Memory();await task.setup(None,runtime);return runtime.files
        files=asyncio.run(capture(tasks[0]));self.assertEqual(files,asyncio.run(capture(changed)))
        self.assertEqual(json.loads(files['records.json']),context['records'])
        self.assertEqual(files['query.txt'],d.question(queries[0]).encode())
        self.assertFalse({'HOST_GOLD.json','GROUPS.json','operator_program.py'}&set(files))
        self.assertIn('id, user, text, and weight',tasks[0].data.prompt)
        self.assertNotIn('Optional API example',tasks[0].data.prompt)

if __name__=='__main__':unittest.main()
