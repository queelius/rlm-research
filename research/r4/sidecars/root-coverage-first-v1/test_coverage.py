import asyncio
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def module(name):
    path=ROOT/(name+'.py')
    if not path.exists():raise AssertionError('implementation missing: '+name)
    spec=importlib.util.spec_from_file_location('coverage_test_'+name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def ledger(arm):
    contract=module('study').contract()
    return module('ledger').Ledger('root',{'coordinate':'c','context_id':'ctx','arm':arm,
        'records':[{'id':'a','text':'Which city?'},{'id':'b','text':'Who wrote it?'}]},contract.request_for,contract.strict_map)


def add(value,ids,labels):
    key=object();prompt=value.request_for([value.public[i] for i in ids])
    value.stage(key,'root','child'+str(len(value.events)),prompt,json.dumps(dict(zip(ids,labels))),1)
    value.deliver(key)


class CoverageTests(unittest.TestCase):
    def test_partial_has_no_category_bins_and_original_text_is_untouched(self):
        value=ledger('coverage_first');add(value,['a'],['location'])
        actual=value.observe('root','original count 99','original count 99')
        self.assertTrue(actual.startswith('original count 99\n\n'))
        shown=json.loads(actual.split('\n')[-1]);self.assertNotIn('counts',shown)
        self.assertEqual((shown['resolved'],shown['unqueried'],shown['partial']),(1,1,True))
        self.assertFalse(any(label in json.dumps(shown) for label in value.summary()['counts']))

    def test_complete_suffix_equals_always_counts_bytes(self):
        a,b=ledger('always_counts'),ledger('coverage_first')
        for value in (a,b):add(value,['a','b'],['location','human being'])
        self.assertEqual(a.observe('root','original'),b.observe('root','original'))
        self.assertEqual(ledger('map').observe('root','original'),'original')

    def test_repeats_idempotent_conflicts_permanent_and_counts_stay_hidden(self):
        value=ledger('coverage_first')
        add(value,['a','b'],['location','human being']);add(value,['a'],['location'])
        self.assertEqual(value.summary()['resolved'],2)
        add(value,['a'],['entity']);add(value,['a'],['location'])
        self.assertEqual((value.summary()['resolved'],value.summary()['conflicts']),(1,1))
        self.assertNotIn('counts',json.loads(value.observe('root','original').split('\n')[-1]))

    def test_plan_has_48_balanced_rotating_coordinates(self):
        s=module('study');plan=s.plan_for(s.inputs()[0]);self.assertEqual(len(plan),48)
        self.assertEqual(len({r['id'] for r in plan}),48)
        for weight in s.WEIGHTS:
            phase=[r for r in plan if r['weight']==weight];self.assertEqual(len(phase),24)
            for offset in range(0,24,3):
                triple=phase[offset:offset+3]
                self.assertEqual({r['arm'] for r in triple},set(s.ARMS))
                self.assertEqual(len({(r['context_id'],r['seed']) for r in triple}),1)


class DispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_three_arms_sequential_within_each_block(self):
        import time
        c=module('collect');events=[]
        plan=[{'triple_id':str(i),'triple_order':j,'id':f'{i}:{j}'} for i in range(5) for j in range(3)]
        async def one(row):
            events.append(('start',row['id']));await asyncio.sleep(.001);events.append(('end',row['id']))
        self.assertIsNone(await c.dispatch(plan,one,time.time()+3))
        for i in range(5):
            for j in range(2):self.assertLess(events.index(('end',f'{i}:{j}')),events.index(('start',f'{i}:{j+1}')))


if __name__=='__main__':unittest.main()
