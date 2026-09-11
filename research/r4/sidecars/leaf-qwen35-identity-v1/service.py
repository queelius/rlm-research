"""Base-checkpoint configuration and identity; never pretend a base is a LoRA."""
from pathlib import Path
import study as s

OLD=s.SIDE/'strict-rlm-temperature-adherence-v1'


def config(model,directory,key):
    value=s.read(OLD/'configs/inference-replica0.json')
    value['vllm'].update(model=model['path'],served_model_name=[model['alias']],dtype='bfloat16',enable_lora=False,
        enforce_eager=True,enable_prefix_caching=False,generation_config='vllm',max_model_len=8192,max_num_seqs=4,
        api_key=[key],reasoning_parser='qwen3' if model==s.MODELS['qwen35'] else None,
        tool_call_parser='qwen3_coder' if model==s.MODELS['qwen35'] else 'hermes')
    for k in ('max_loras','max_lora_rank','max_cpu_loras','lora_dtype'):value['vllm'].pop(k,None)
    if model==s.MODELS['qwen35']:value['vllm'].update(language_model_only=True,mamba_cache_mode='align')
    value.update(enable_fp32_lm_head=False,enable_fp32_router_logits=False,output_dir=str(Path(directory)/'launcher'))
    return value


def descriptor(model,directory):
    return dict(host='127.0.0.1',port=18601,replica=0,api_key_env='STRICT_RLM_CALIBRATION_API_KEY',
        model_alias=model['alias'],base_model=model,adapter=None,inference_only=True,
        prime_inference_config=str(Path(directory)/'inference.json'),vllm_version='0.28.0',max_model_len=8192,
        model_semantics='Released post-trained instruction checkpoint without research adapters')


def validate_descriptor(endpoint,model):
    if endpoint.get('adapter') is not None or endpoint.get('base_model')!=model or endpoint.get('model_alias')!=model['alias']:
        raise ValueError('not exact no-adapter checkpoint')
    if endpoint.get('max_model_len')!=8192 or endpoint.get('vllm_version')!='0.28.0':raise ValueError('runtime mismatch')


def validate_models(payload,model):
    cards=payload.get('data',[])
    if len(cards)!=1 or cards[0].get('id')!=model['alias'] or cards[0].get('root')!=model['path'] or cards[0].get('parent') is not None:
        raise ValueError('live base card/alias differs or adapter exposed')
