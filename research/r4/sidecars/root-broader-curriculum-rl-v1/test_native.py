import asyncio
import importlib
import json
from pathlib import Path
import unittest
import broad_study as s

class NativeTests(unittest.TestCase):
    def module(self):
        self.assertTrue((s.ROOT/'broad_native.py').exists(),'actual native task adapter missing')
        return importlib.import_module('broad_native')
    def test_actual_native_tasks_condition_target_and_keep_gold_out_of_setup(self):
        n=self.module();context=s.data()[0][0];cid=context['id']
        a=n.make_task(context,cid+':human_being',0);b=n.make_task(context,cid+':numeric_value',0);changed=n.make_task(context,cid+':human_being',999)
        self.assertIn("'human being'",a.data.prompt);self.assertIn("'numeric value'",b.data.prompt)
        self.assertNotEqual(n.first_prefix(a),n.first_prefix(b));self.assertEqual(n.first_prefix(a),n.first_prefix(changed))
        self.assertEqual(a.plain_query,s.question(cid+':human_being'));self.assertEqual(a.data.context,context['text'])
        class Memory:
            def __init__(self):self.files={}
            async def write(self,name,value):self.files[name]=value
        async def capture(task):
            runtime=Memory();await task.setup(None,runtime);return runtime.files
        files=asyncio.run(capture(a));different_gold=asyncio.run(capture(changed))
        self.assertEqual(files,different_gold)
        self.assertEqual(files['context.txt'],context['text'].encode())
        self.assertEqual(files['query.txt'],s.question(cid+':human_being').encode())
        self.assertEqual(json.loads(files['records.json']),context['records'])
        self.assertFalse({'HOST_GOLD.json','GROUPS.json','operator_program.py'}&set(files))

if __name__=='__main__':unittest.main()
