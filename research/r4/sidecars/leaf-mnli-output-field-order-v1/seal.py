"""Seal exact inputs and local source after focused CPU checks."""
import time
import study as s,protocol_v2 as p
def main():
    assert s.read(s.ROOT/'CPU_NATIVE_v2.json')['requests']==48
    source={str(path):s.sha(path) for path in s.ROOT.iterdir() if path.is_file() and (path.suffix in ('.py','.md') or path.name=='CPU_TESTS.json')}
    prior=s.read(s.PRIOR/'READY_v2.json')
    source.update(prior['source_sha256'])
    source[str(s.PRIOR/'READY_v2.json')]=s.sha(s.PRIOR/'READY_v2.json')
    inputs={str(s.ROOT/name):s.sha(s.ROOT/name) for name in ('PLAN_v2.json','REQUESTS_v2.json','ORDERED_REQUESTS_v2.json','PROMPT_IDS_v2.json','CPU_NATIVE_v2.json','PLANNED_NULL_ENDPOINTS_v2.json')}
    for name in ('DATA.json','PUBLIC.json','ALIEN_DICTIONARIES_v2.json'):
        inputs[str(s.PRIOR/name)]=s.sha(s.PRIOR/name)
    ready=dict(schema='mnli-output-field-order-ready-v1',source_sha256=source,input_sha256=inputs,
               model=s.MODEL,adapter=None,planned_endpoints=48,contexts=8,arms=list(p.ARMS),
               factorial='visible_reference3_by_output_field_order2',seed_master=p.MASTER,
               context_exposure='exact eight prior wording-control contexts, no outcome ranking',
               outer_seconds=1440,work_seconds=1320,owned_seconds=1410,workers=4,request_seconds=90,
               created_epoch=time.time(),gpu_calls=0,service_calls=0)
    ready['identity']=s.digest(ready);s.write(s.READY_PATH,ready);s.verify()
    print(dict(identity=ready['identity'],ready_sha256=s.sha(s.READY_PATH),source_pins=len(source),input_pins=len(inputs)))
if __name__=='__main__':main()
