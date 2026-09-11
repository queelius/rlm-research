"""Bounded endpoint/decoder tests; no provider or GPU."""
import unittest

class Contracts(unittest.TestCase):
    def test_length_is_observed_invalid_or_correct_not_null(self):
        import protocol as p
        self.assertEqual(p.score('["c01"]',['c01'],'length')['reward'],1)
        self.assertEqual(p.score('["c01"',['c01'],'length')['reward'],0)
        self.assertIsNone(p.score(None,['c01'],None,available=False)['reward'])

    def test_parser_never_reorders_deduplicates_or_extracts_prose(self):
        import protocol as p
        for value in ('["c02","c01"]','["c01","c01"]','answer: ["c01"]','["c99"]'):
            self.assertEqual(p.score(value,['c01'],'stop')['reward'],0)

    def test_decoder_pair_only_differs_in_schema(self):
        import protocol as p
        source={'messages':[{'role':'user','content':'original unchanged'}]}
        a=p.request(source,981360001,'free','base');b=p.request(source,981360001,'exact','base')
        schema=b.pop('structured_outputs')['json'];self.assertEqual(a,b)
        self.assertEqual(schema,{'type':'array','items':{'type':'string','enum':[f'c{i:02}' for i in range(1,13)]}})
        self.assertEqual(a['max_tokens'],2560);self.assertEqual(a['messages'],source['messages'])

    def test_owner_argv_rejects_old_output_namespace(self):
        import owner
        import study as s
        argv=owner.collector_argv(s.ATTEMPT/'owned-service',s.ATTEMPT,999)
        value=owner.validate_argv(argv);self.assertEqual(value['output'],s.ATTEMPT/'rollout')
        wrong=list(argv);wrong[6]=str(s.FREE/'outputs/attempt-003/rollout')
        with self.assertRaises(ValueError):owner.validate_argv(wrong)

    def test_actual_qualified_weight_schema_is_checked(self):
        import study as s
        self.assertGreater(s.validate_weights(),0)

if __name__=='__main__':unittest.main()
