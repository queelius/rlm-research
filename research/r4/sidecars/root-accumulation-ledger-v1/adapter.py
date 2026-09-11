"""Common native typed hook and study-owned supervisor/observation setup delta."""
import contextlib
import json
import os
import uuid
import study as s
import overlay

def environment():return s.stack().interface.e.environment_config()

def task(context,prompt,gold,name,row):
    original=s.stack().native.task(context,prompt,gold,name)
    class LedgerTask(type(original)):
        async def setup(self,trace,runtime):
            await super().setup(trace,runtime)
            config={'coordinate':row['id'],'arm':row['arm'],'context_id':context['id'],
                    'records':[{'id':r['id'],'text':r['text']} for r in context['records']]}
            await runtime.write('ledger_config.json',json.dumps(config,ensure_ascii=False).encode())
        async def finalize(self,trace,runtime):
            try:
                payload=await runtime.read('ledger_events.jsonl',max_bytes=16*1024*1024)
                trace.info['accumulation_ledger']={'raw':payload.decode(),'trust':'runtime-writable audit; corroborate external native/graph ancestry'}
            except Exception as error:trace.info['accumulation_ledger']={'raw':None,'error':type(error).__name__+': '+str(error)}
            await super().finalize(trace,runtime)
    value=LedgerTask(original.data,original.config)
    value.public_records,value.plain_query,value.controller=original.public_records,original.plain_query,'free'
    return value

@contextlib.contextmanager
def installed(binding,output,plan,public):
    from verifiers.v1.harnesses.rlm.harness import RLMHarness
    st=s.stack();interface=st.interface
    st.local.validate_store()
    interface.e.capture.q.ROOTLESS=st.local.LOCAL
    os.environ['PATH']=str(st.local.LOCAL/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ['VERIFIERS_CACHE_DIR']=str(st.local.STORE/('ledger-cache-'+s.digest(str(output))[:20]))
    catalogs=interface.catalogs(public)
    with interface.hooks.installed(binding,output,plan,catalogs):
        original=RLMHarness.setup
        async def setup(self,runtime):
            await original(self,runtime)
            role=interface.e.capture.installed_hooks.__wrapped__.__globals__['role']
            # The unchanged typed operator closure already installs the adaptive free-root overlay.
            a=interface.e.a
            old_engine=a.overlay_program.__globals__['patch_engine'](role.patch_engine(role.NANO_SOURCE.read_text()))
            program=overlay.program(old_engine)
            result=await runtime.run(['python','-c',program],{})
            s.write(output/'ledger-overlays'/(uuid.uuid4().hex+'.json'),{'runtime':runtime.name,
                    'program_sha256':s.digest(program),'exit_code':result.exit_code,'stdout':result.stdout,'stderr':result.stderr})
            if result.exit_code:raise RuntimeError('owned ledger overlay failed')
        RLMHarness.setup=setup
        try:yield interface
        finally:RLMHarness.setup=original
