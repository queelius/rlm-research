"""Qualified no-adapter service configuration rebound to cached Mistral."""
import study as s
module=s.load('mistral_qualified_service',s.FREE/'service.py','51215324f767d3b7fc214bed4c64e61592fb3be8223c8d5f1dd4773fae4c48cd',{'study':s});OLD=module.OLD;validate_models=module.validate_models
def config(model,directory,key):
 value=module.config(model,directory,key);value['vllm']['max_model_len']=s.MAX_MODEL_LEN;return value
def descriptor(model,directory):
 value=module.descriptor(model,directory);value['max_model_len']=s.MAX_MODEL_LEN;return value
def validate_descriptor(endpoint,model):
 value=dict(endpoint);value['max_model_len']=8192;module.validate_descriptor(value,model)
 if endpoint.get('max_model_len')!=s.MAX_MODEL_LEN:raise ValueError('Mistral context bound differs')
