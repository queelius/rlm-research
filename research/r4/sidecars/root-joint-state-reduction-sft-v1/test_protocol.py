import asyncio
import contextlib
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

class ProtocolTests(unittest.TestCase):
    def module(self):
        self.assertTrue((Path(__file__).parent/'joint_protocol.py').exists(),'live-state protocol not implemented')
        return importlib.import_module('joint_protocol')

    def test_live_batch_accumulation_and_actual_wrong_label_reduction(self):
        p=self.module();row=dict(width=4,variable='ledger',users=['u03'])
        records=[dict(id=f'q{i:04}',user=f'u{i%4:02}',text='record') for i in range(16)]
        # The authored target must preserve these observations even if semantically wrong.
        labels={r['id']:'numeric value' for r in records}
        async def fake_run(batch):return types.SimpleNamespace(answer={r['id']:labels[r['id']] for r in batch})
        api=types.ModuleType('rlm.api');api.run=fake_run
        contract=types.ModuleType('batch_contract');contract.request_for=lambda batch:batch;contract.strict_map=lambda answer,ids:answer
        namespace={};observations=[]
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d,patch.dict(sys.modules,{'rlm.api':api,'batch_contract':contract}):
            path=Path(d)/'records.json';path.write_text(json.dumps(records))
            namespace['open']=lambda name: io.StringIO(path.read_text())
            for index in range(4):
                out=io.StringIO()
                with contextlib.redirect_stdout(out):asyncio.run(eval(compile(p.producer(row,index),'<authored>', 'exec',flags=__import__('ast').PyCF_ALLOW_TOP_LEVEL_AWAIT),namespace))
                observations.append(out.getvalue())
                self.assertEqual(len(namespace['ledger']),4*(index+1))
            pieces,merged=p.visible_maps(observations,dict(records=records))
            self.assertEqual(merged,labels)
            code,_=p.correction(pieces,row,'numeric value')
            self.assertNotIn('q000',code)
            out=io.StringIO()
            with contextlib.redirect_stdout(out):exec(code,namespace)
            self.assertEqual(out.getvalue(),'4\n')

    def test_cumulative_observations_cannot_silently_change_prior_labels(self):
        p=self.module()
        with self.assertRaises(ValueError):p.visible_maps(['{"a":"numeric value"}','{"a":"human being","b":"numeric value"}'],dict(records=[dict(id='a'),dict(id='b')]))

    def test_controlled_replay_checks_sampling_and_caps_not_only_tokens(self):
        p=self.module();source=dict(model='c32',token_ids=[1,2],temperature=.5,max_tokens=2048)
        p.verify_replay(dict(source),source)
        for field,value in (('temperature',.6),('max_tokens',1024),('model','other'),('token_ids',[1,3])):
            with self.assertRaises(ValueError):p.verify_replay({**source,field:value},source)

if __name__=='__main__':unittest.main()
