"""Pin local batch/model comparison after focused CPU qualification."""
import time
import bg_study as s
def main():
    assert s.read(s.ROOT/'CPU_TESTS.json')['exit_code']==0
    source={str(p):s.sha(p) for p in s.ROOT.iterdir() if p.is_file() and p.name!='READY.json'}
    inputs={str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')}
    source.update(s.read(s.ROOT/'inputs/PROVENANCE.json')['source_sha256'])
    binding=s.binding();child=binding['models'][binding['fixed_child']]
    from pathlib import Path
    for name in ('adapter_model.safetensors','adapter_config.json'):
        source[str(Path(child['path'])/name)]=s.sha(Path(child['path'])/name)
    ready=dict(schema='leaf-adapter-granularity-ready-v1',source_sha256=source,input_sha256=inputs,
        created_epoch=time.time(),planned=152,contexts=2,seeds=list(s.SEEDS),model_policies=['base','c32'],
        outer_seconds=1800,owned_seconds=1770,work_seconds=1650,workers=4,request_seconds=90,
        base_model=s.BASE_MODEL,child=child,exposure='purposive prior error contexts',no_training=True)
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready);s.verify()
    print(dict(identity=ready['identity'],ready_sha256=s.sha(s.ROOT/'READY.json')))
if __name__=='__main__':main()
