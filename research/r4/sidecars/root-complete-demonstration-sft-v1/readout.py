"""New panel in unchanged qualified native16 collector; no decoder repair."""
import argparse
import asyncio
import contextlib
import os
from pathlib import Path
from types import ModuleType
import study as s
import binding as b

def native_unavailable(last,trace):
    return (not last or last.get('status')!='returned' or
      (trace.get('ok') is False and trace.get('stop_condition')=='error' and not trace.get('root_reply')))

def compose():
    st=s.stack();view=ModuleType('complete_native_collector_view');view.__dict__.update(st.prior.__dict__);view.ROOT=s.ROOT
    source=s.PRIOR/'evaluate.py';pin=s.read(s.PRIOR/'READY.json')['source_sha256'][str(source)]
    collector=s.private('complete_native_collector',source,pin,{'planned=24':('planned=16',1),'len(records)==24':('len(records)==16',2),
      "unavailable=not last or last.get('status')!='returned'":('unavailable=native_unavailable(last,trace)',1)},extra={'native':st.native})
    collector.native_unavailable=native_unavailable
    collector.s=view
    return collector,st

async def collect(args):
    import httpx
    ready=s.verify();chosen=b.selected(args.weight);binding=s.read(args.binding);descriptor=s.read(args.endpoint)
    if args.training.resolve()!=b.training_source(args.weight) or binding!=b.binding(args.weight,chosen):raise ValueError('actual fixed policy binding')
    b.validate_descriptor(binding,descriptor,s.sha(args.binding))
    with httpx.Client(trust_env=False,timeout=15,headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}) as client:
        response=client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models');response.raise_for_status();cards={x['id']:x for x in response.json()['data']}
    for alias,model in binding['models'].items():
        if cards.get(alias,{}).get('root')!=model['path'] or cards[alias].get('parent')!=descriptor['base_model']['path']:raise ValueError('live cards')
    collector,st=compose()
    def verify_binding(actual,arm,training):
        if actual!=binding or arm!=args.weight or training.resolve()!=args.training.resolve():raise ValueError('collector binding changed')
    collector.verify_binding=verify_binding
    with s.aliases({'interface':st.interface}):interface=st.local.configure_interface(args.output)
    @contextlib.contextmanager
    def hooks(recipe,actual,output,plan,public):
        if actual!=binding or recipe['child_interface']['pins']!=interface.PINS:raise ValueError('same typed child contract')
        with interface.installed(actual,output,plan,public):yield interface
    collector.child_hooks=hooks
    s.write(args.output.parent/'READOUT_BINDING.json',dict(identity=ready['identity'],binding_sha256=s.sha(args.binding),descriptor_sha256=s.sha(args.endpoint),models=cards,selected=chosen))
    return await collector.collect(args)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--weight',choices=('unchanged',*s.ARMS),required=True)
    for name in ('training','binding','endpoint','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--deadline',type=float,required=True);raise SystemExit(asyncio.run(collect(p.parse_args())))
