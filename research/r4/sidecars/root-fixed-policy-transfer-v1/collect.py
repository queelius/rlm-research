"""Free-only qualified native collector; additive attempt ledger, no science/request changes."""
import asyncio
from pathlib import Path
import sys
import types
import transfer_study as s
import transfer_binding as b

def load_original():
    path=s.OLD/'collect.py';s.check(path,'f2e0d2adcfe01ee562488a98e24037781ab81f2f7daab9462eecf7098f4d93ac')
    code=path.read_text()
    before="response=await client.post(f'http://{descriptor[\"host\"]}:{descriptor[\"port\"]}/inference/v1/generate',json=body)"
    if code.count(before)!=2:raise ValueError('exact two actual provider seams')
    code=code.replace(before,"record['physical_request_attempt']=True; "+before)
    before='record.update(status=response.status_code,paid_model_call=True,origin='
    if code.count(before)!=2:raise ValueError('exact two actual response seams')
    code=code.replace(before,'record.update(status=response.status_code,response_text=response.text,paid_model_call=True,origin=')
    module=types.ModuleType('transfer_qualified_free_collector');module.__file__=str(path);sys.modules[module.__name__]=module
    with s.aliases({'joint_study':s,'joint_protocol':s.original_protocol(),'joint_binding':b}):exec(compile(code,str(path),'exec'),module.__dict__)
    return module

original=load_original()
def validate_args(args):
    if (args.mode,args.plan,args.start,args.stop)!=('free','FREE_PLAN.json',0,16):raise ValueError('only complete free16 phase; no capture/controlled/subset')
    return args
def parse_args(argv=None):return validate_args(original.parse_args(argv))
def physical_cost(records):
    attempts=[r for r in records if r.get('physical_request_attempt')]
    returned=[r for r in attempts if r.get('status')==200 and r.get('response',{}).get('choices')]
    return dict(physical_request_attempts=len(attempts),returned_native_completions=len(returned),input_tokens=sum(len(r['body']['token_ids']) for r in attempts),output_tokens_known=sum(len(c['token_ids']) for r in returned for c in r['response']['choices']),output_usage_unknown_attempts=len(attempts)-len(returned),provider_billing=None,cached_tokens=None,legacy_paid_model_call_field_is_not_billing=True)
def ledger(output):
    files=sorted(Path(output).rglob('physical/*.json'));records=[s.read(p) for p in files]
    return dict(**physical_cost(records),physical_record_sha256={str(p):s.sha(p) for p in files},prior_training_is_sunk_not_new_work=True,all_readout_work_new_no_replay=True)
async def run(args):
    validate_args(args)
    try:
        with s.aliases({'joint_study':s,'joint_protocol':s.original_protocol(),'joint_binding':b}):await original.run(args)
    finally:
        if args.output.exists():s.write(args.output/'ATTEMPT_COST_LEDGER.json',ledger(args.output))

if __name__=='__main__':asyncio.run(run(parse_args()))
