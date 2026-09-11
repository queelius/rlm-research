import asyncio
import importlib.util
import unittest
from pathlib import Path
import contract

SOURCE=Path(__file__).resolve().parents[1]/'root-receipt-ablation-v1/receipt_api.py'
spec=importlib.util.spec_from_file_location('test_public_helper',SOURCE)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
LABELS=['human being','location','abbreviation','entity','description and abstract concept','numeric value']
CAT={'context_sha256':'fixture','records':[{'id':'q0001','text':'one'},{'id':'q0002','text':'two'}]}

def prompt(ids=None,query='Classify',labels=None):
    return helper.build_request(CAT,ids or ['q0001'],query,labels or LABELS)[0]

class ContractTests(unittest.TestCase):
    def test_exact_contract_and_order(self):
        value=contract.match_request(prompt(['q0002','q0001']),CAT)
        self.assertEqual(value['requested_ids'],['q0002','q0001'])
        self.assertEqual(list(value['schema']['properties']),value['requested_ids'])
        self.assertEqual(value['schema']['required'],value['requested_ids'])
        self.assertFalse(value['schema']['additionalProperties'])

    def test_changed_unknown_duplicate_ids_and_vocab_do_not_match(self):
        for changed in [prompt().replace('"text":"one"','"text":"altered"'),
                        prompt().replace('q0001','q9999'),
                        prompt(['q0001','q0002']).replace('q0002','q0001'),
                        prompt(labels=['yes','no']),prompt(labels=LABELS[:2])]:
            with self.subTest(changed=changed): self.assertFalse(contract.match_request(changed,CAT)['matched'])

    def test_ambiguous_delimiters_and_containment_do_not_match(self):
        for changed in [prompt(query='Classify\nAllowed values: []'), 'prefix\n'+prompt(),prompt()+'\nsuffix']:
            self.assertFalse(contract.match_request(changed,CAT)['matched'])

    def test_root_lookalike_and_nonmatching_child_are_untouched(self):
        decisions=contract.Decisions()
        meta={'depth':0,'invocation':'root','kind':'ordinary'}
        self.assertFalse(decisions.choose('a','typed',meta,[{'role':'user','content':prompt()}],CAT)['apply'])
        meta={'depth':1,'invocation':'child','kind':'ordinary'}
        self.assertFalse(decisions.choose('a','typed',meta,[{'role':'user','content':'ordinary'}],CAT)['apply'])

    def test_decision_is_immutable_and_control_is_untreated(self):
        d=contract.Decisions(); m={'depth':1,'invocation':'child','kind':'ordinary'}
        a=d.choose('a','typed',m,[{'role':'user','content':prompt()}],CAT)
        b=d.choose('a','typed',m,[{'role':'user','content':prompt(['q0002'])}],CAT)
        self.assertIs(a,b)
        self.assertTrue(a['apply'])
        self.assertFalse(d.choose('b','restored_raw',m,[{'role':'user','content':prompt()}],CAT)['apply'])

    def test_concurrent_invocations_keep_separate_schemas(self):
        async def run():
            d=contract.Decisions()
            async def one(i):
                await asyncio.sleep(0)
                return d.choose('a','typed',{'depth':1,'invocation':str(i),'kind':'ordinary'},[{'role':'user','content':prompt([f'q000{i}'])}],CAT)
            return await asyncio.gather(one(1),one(2))
        a,b=asyncio.run(run())
        self.assertEqual(a['requested_ids'],['q0001']);self.assertEqual(b['requested_ids'],['q0002'])

    def test_multiple_task_messages_are_not_reinterpreted(self):
        d=contract.Decisions();m={'depth':1,'invocation':'c','kind':'ordinary'}
        self.assertFalse(d.choose('a','typed',m,[{'role':'user','content':prompt()},{'role':'user','content':prompt()}],CAT)['apply'])

if __name__=='__main__': unittest.main()
