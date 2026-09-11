"""Independent hand-counted fixtures: removing dedup/conflict/source gates must fail."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('frozen_test_batch',HERE.parent/'adaptive-filter-pilot-v1/batch_contract.py')
batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)

class LedgerTests(unittest.TestCase):
    def create(self,root='root-A',arm='ledger'):
        import ledger
        config={'coordinate':'episode-A','arm':arm,'context_id':'context-A','records':[
            {'id':'q0001','text':'How many planets?'},{'id':'q0002','text':'Which city?'},
            {'id':'q0003','text':'Who wrote this?'}]}
        return ledger.Ledger(root,config,batch.request_for,batch.strict_map)

    def stage(self,l,key,rows,labels,parent='root-A',child=None):
        raw=json.dumps(labels,separators=(',',':'))
        l.stage(key,parent,child or str(key),batch.request_for(rows),raw,1)
        return raw

    def test_repeated_ids_count_once_and_pending_is_not_delivered(self):
        l=self.create();rows=l.records[:2]
        raw=self.stage(l,'one',rows,{'q0001':'numeric value','q0002':'location'})
        self.assertEqual(l.summary()['unique_seen'],0)
        self.assertEqual(l.observe('root-A','unchanged'),'unchanged')
        l.deliver('one');self.assertEqual(l.summary()['unique_seen'],2)
        self.stage(l,'two',rows,{'q0001':'numeric value','q0002':'location'});l.deliver('two')
        summary=l.summary();self.assertEqual(summary['counts'],{'human being':0,'location':1,'abbreviation':0,'entity':0,'description and abstract concept':0,'numeric value':1})
        self.assertEqual((summary['unique_seen'],summary['unqueried'],summary['conflicts'],summary['partial']),(2,1,0,True))
        self.assertEqual(next(e for e in l.events if e['event']=='child_result')['raw_answer'],raw)
        self.assertFalse(l.deliver('one'))

    def test_conflicting_id_stays_excluded_without_gold_resolution(self):
        l=self.create();rows=l.records[:1]
        for key,label in [('a','numeric value'),('b','location'),('c','numeric value')]:
            self.stage(l,key,rows,{'q0001':label});l.deliver(key)
        summary=l.summary();self.assertEqual(sum(summary['counts'].values()),0)
        self.assertEqual((summary['unique_seen'],summary['resolved'],summary['conflicts']),(1,0,1))

    def test_source_text_unknown_id_and_root_episode_isolation(self):
        l=self.create()
        for key,rows,parent in [('changed',[{'id':'q0001','text':'changed'}],'root-A'),('unknown',[{'id':'q9999','text':'x'}],'root-A'),('otherroot',l.records[:1],'root-B')]:
            self.stage(l,key,rows,{rows[0]['id']:'numeric value'},parent);l.deliver(key)
        self.assertEqual(l.summary()['unique_seen'],0)
        self.assertEqual(l.observe('root-A','unchanged'),'unchanged')
        self.stage(l,'good',l.records[:1],{'q0001':'numeric value'});l.deliver('good')
        self.assertEqual(self.create('root-B').summary()['unique_seen'],0)
        self.assertEqual(l.observe('root-B','already truncated'),'already truncated')
        self.assertEqual(self.create(arm='map').observe('root-A','already truncated'),'already truncated')
        observed=l.observe('root-A','already truncated')
        self.assertTrue(observed.startswith('already truncated\n\n[Harness accumulation ledger'))
        self.assertLessEqual(len(observed)-len('already truncated'),2048)
        self.assertIn('"partial":true',observed)

if __name__=='__main__':unittest.main()
