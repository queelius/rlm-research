import unittest
import contract

ROWS=[{'id':'q0001','user':'u00','text':'How many?'},{'id':'q0002','user':'u01','text':'Where?'}]
CAT={'context_sha256':'fixture','records':ROWS}
class Tests(unittest.TestCase):
    def test_exact_public_batch_matches_order(self):
        result=contract.match_request(contract.batch.request_for(ROWS[::-1]),CAT)
        self.assertTrue(result['matched']);self.assertEqual(result['requested_ids'],['q0002','q0001'])
    def test_changed_unknown_duplicate_or_substring_does_not_match(self):
        original=contract.batch.request_for(ROWS)
        for value in [original.replace('How many?','Altered'),original.replace('q0001','q9999'),original.replace('q0002','q0001'),'prefix'+original,original+'\nRecords: []']:
            self.assertFalse(contract.match_request(value,CAT)['matched'])

if __name__=='__main__':unittest.main()
