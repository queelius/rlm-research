import unittest
from credential_preflight import KEY_NAME, require_provider_credential

class CredentialRegression(unittest.TestCase):
    def test_missing_credential_stops_before_dispatch_and_valid_value_is_never_returned(self):
        for environment in ({}, {KEY_NAME:''}, {KEY_NAME:'   '}):
            with self.subTest(environment_keys=list(environment)), self.assertRaisesRegex(ValueError, KEY_NAME):
                require_provider_credential(environment)
        sentinel = 'test-fixture-only-not-a-real-credential'
        environment = {KEY_NAME:sentinel}
        result = require_provider_credential(environment)
        self.assertEqual(result, {'provider_credential_present':True, 'credential_environment_variable':KEY_NAME})
        self.assertNotIn(sentinel, str(result))
        self.assertEqual(environment[KEY_NAME], sentinel)

if __name__ == '__main__':
    unittest.main()
