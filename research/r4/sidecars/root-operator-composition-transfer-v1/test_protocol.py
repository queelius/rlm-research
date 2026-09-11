import unittest
import ct_protocol as p

class OracleTests(unittest.TestCase):
    def fixture(self):
        records=[dict(id=str(i),user=u,weight=w,text='fixture') for i,(u,w) in enumerate([('u0',2),('u0',3),('u0',7),('u1',6),('u1',4),('u1',1),('u2',5),('u2',2),('u3',7)])]
        labels=dict(zip([r['id'] for r in records],['A','A','B','A','B','B','B','C','C']))
        return records,labels
    def test_literal_all_six(self):
        records,labels=self.fixture()
        expected=[3,2,11,1,6,12]
        for op,want in zip(p.OPERATORS,expected):
            row=dict(operator=op,target='A',target_b='B')
            self.assertEqual(p.answer(records,labels,row),want)
            self.assertEqual(p.enumerated_answer(records,labels,row),want)
    def test_empty_qualifier_and_no_b(self):
        records,labels=self.fixture()
        for op in p.OPERATORS:
            row=dict(operator=op,target='missing',target_b='B')
            self.assertEqual(p.answer(records,labels,row),0)
            self.assertEqual(p.enumerated_answer(records,labels,row),0)
        self.assertEqual(p.answer(records,labels,dict(operator='conditional_weight',target='A',target_b='missing')),0)
    def test_threshold_and_tied_max(self):
        records=[dict(id='x',user='u0',weight=5),dict(id='y',user='u1',weight=5)]
        labels={'x':'A','y':'A'}
        self.assertEqual(p.answer(records,labels,dict(operator='threshold_users',target='A')),0)
        self.assertEqual(p.answer(records,labels,dict(operator='maximum_weight',target='A')),5)
    def test_missing_map_not_repaired(self):
        with self.assertRaises(KeyError):p.answer([dict(id='x',user='u0',weight=1)],{},dict(operator='count',target='A'))
    def test_questions_are_unambiguous_and_not_algorithms(self):
        for i in range(8):
            specs=p.specs(i)
            self.assertEqual(len(specs),6)
            self.assertTrue(all('regardless of which user owns' in x['question'] for x in specs))
            self.assertNotEqual(specs[0]['target'],specs[0]['target_b'])
        self.assertIn('strictly greater than 5',p.specs(0)[3]['question'])

if __name__=='__main__':unittest.main()
