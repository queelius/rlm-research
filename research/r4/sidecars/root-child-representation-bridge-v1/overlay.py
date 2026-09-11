"""Only supervisor source changes inside each newly owned runtime."""
import study as s

old=s.load('bridge_old_overlay',s.OLD/'overlay.py','febb0e22c1b00fbac83c5203df5b5795adc27ca19f5f223aeb3550c078b292fc')
SUPERVISOR=old.SUPERVISOR;SUPERVISOR_SHA=old.SUPERVISOR_SHA

def supervisor(source):
    source=old.replace(source,'        self.root_id = root_id\n','''        self.root_id = root_id
        import json
        from rlm._representation_bridge import Bridge
        self._representation = Bridge(root_id, json.loads((Path(cwd) / 'bridge_config.json').read_text()), Path(cwd) / 'bridge_events.jsonl')
''')
    source=old.replace(source,'                    result = await engine.run(prompt)\n','''                    physical_prompt = self._representation.begin(parent_id, child_id, prompt, child_context.depth)
                    result = await engine.run(physical_prompt)
''')
    source=old.replace(source,'                self.semantic_edges.finish_subagent(child_id)\n                return result\n','''                self.semantic_edges.finish_subagent(child_id)
                return self._representation.finish(asyncio.current_task(), parent_id, child_id, prompt, result, child_context.depth)
''')
    return old.replace(source,'            await write_frame(writer, {"result": result})\n','''            await write_frame(writer, {"result": result})
            self._representation.deliver(operation_task)
''')

def program(original_engine):
    s.check(SUPERVISOR,SUPERVISOR_SHA);source=supervisor(SUPERVISOR.read_text());compile(source,'supervisor.py','exec')
    batch=s.SIDE/'adaptive-filter-pilot-v1/batch_contract.py';s.check(batch,'d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88')
    payload={'_representation_bridge.py':(s.ROOT/'bridge.py').read_text(),'_representation_batch.py':batch.read_text()}
    return '''import hashlib,json,pathlib
source=%r
payload=%r
changed=[]
for root in [pathlib.Path('/tmp'),pathlib.Path('/root/.local/share/uv'),pathlib.Path('/root/.cache/uv')]:
    if not root.exists():continue
    for path in root.rglob('rlm/engine.py'):
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=%r:continue
        target=path.parent/'supervisor.py'
        if hashlib.sha256(target.read_bytes()).hexdigest()!=%r:raise ValueError('supervisor source changed')
        target.write_text(source)
        for name,text in payload.items():(path.parent/name).write_text(text)
        changed.append(str(path.parent))
if not changed:raise RuntimeError('owned runtime source not found')
print(json.dumps({'changed':changed,'supervisor_sha256':hashlib.sha256(source.encode()).hexdigest()}))
'''%(source,payload,s.sha_text(original_engine) if hasattr(s,'sha_text') else __import__('hashlib').sha256(original_engine.encode()).hexdigest(),SUPERVISOR_SHA)
