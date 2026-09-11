"""Require inherited local-provider authority before any attempt artifacts or service."""
import os

KEY_NAME = 'STRICT_RLM_CALIBRATION_API_KEY'

def require_provider_credential(environment=None):
    env = os.environ if environment is None else environment
    value = env.get(KEY_NAME)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Missing nonempty ' + KEY_NAME + '; parent must privately supply the approved local-provider credential before launch')
    # Never return, serialize, log, synthesize, or replace credential bytes.
    return {'provider_credential_present': True, 'credential_environment_variable': KEY_NAME}
