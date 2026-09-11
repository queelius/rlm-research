"""Counted private source overlays, only inside newly owned runtimes."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SUPERVISOR=Path('/tmp/rlmc.0m4242/root/vfs/dir/b50ce4f5b31918d4d2b15d21586825a9320f10fc20818b76f982bcd465d75efc/tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d/checkout/src/rlm/supervisor.py')
SUPERVISOR_SHA='1b9a1b303b7c2a389d8981d0c7ea9d3e5603b49f8a420f354220c6a28c9cc78e'
def replace(source,before,after):
    if source.count(before)!=1:raise ValueError('source seam must match exactly once: '+before[:100])
    return source.replace(before,after)

def engine(source):
    before='''            self.session.log_tool_result(turn, tool_name, result, duration)
            content = truncate_tool_output(result)
'''
    after='''            content = truncate_tool_output(result)
            if self.depth == 0:
                content = self._supervisor._accumulation.observe(self._invocation_id, content, result)
            self.session.log_tool_result(turn, tool_name, content, duration)
'''
    return replace(source,before,after)

def supervisor(source):
    source=replace(source,'        self.root_id = root_id\n','''        self.root_id = root_id
        import json
        from rlm._accumulation_ledger import Ledger
        from rlm._accumulation_batch import request_for, strict_map
        self._accumulation = Ledger(root_id, json.loads((Path(cwd) / 'ledger_config.json').read_text()),
                                    request_for, strict_map, Path(cwd) / 'ledger_events.jsonl')
''')
    source=replace(source,'                self.semantic_edges.finish_subagent(child_id)\n                return result\n','''                self.semantic_edges.finish_subagent(child_id)
                self._accumulation.stage(asyncio.current_task(), parent_id, child_id, prompt,
                                         result.answer, child_context.depth)
                return result
''')
    source=replace(source,'            await write_frame(writer, {"result": result})\n','''            await write_frame(writer, {"result": result})
            self._accumulation.deliver(operation_task)
''')
    return source

def program(original_engine):
    original_supervisor=SUPERVISOR.read_text()
    if hashlib.sha256(original_supervisor.encode()).hexdigest()!=SUPERVISOR_SHA:raise ValueError('supervisor changed')
    batch=ROOT.parent/'adaptive-filter-pilot-v1/batch_contract.py'
    if hashlib.sha256(batch.read_bytes()).hexdigest()!='d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88':raise ValueError('public contract changed')
    sources={'engine.py':(hashlib.sha256(original_engine.encode()).hexdigest(),engine(original_engine)),
             'supervisor.py':(SUPERVISOR_SHA,supervisor(original_supervisor))}
    for name,(_,source) in sources.items():compile(source,name,'exec')
    payload={'_accumulation_ledger.py':(ROOT/'ledger.py').read_text(),'_accumulation_batch.py':batch.read_text()}
    return '''import hashlib,json,pathlib
sources=%r
payload=%r
changed=[]
for root in [pathlib.Path('/tmp'),pathlib.Path('/root/.local/share/uv'),pathlib.Path('/root/.cache/uv')]:
    if not root.exists():continue
    for path in root.rglob('rlm/engine.py'):
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=sources['engine.py'][0]:continue
        parent=path.parent
        for name,(expected,replacement) in sources.items():
            target=parent/name
            if hashlib.sha256(target.read_bytes()).hexdigest()!=expected:raise ValueError('installed source mismatch: '+str(target))
            target.write_text(replacement)
        for name,source in payload.items():(parent/name).write_text(source)
        changed.append(str(parent))
if not changed:raise RuntimeError('owned pinned engine/supervisor not found')
print(json.dumps({'patched':changed,'hashes':{k:hashlib.sha256(v[1].encode()).hexdigest() for k,v in sources.items()}}))
'''%(sources,payload)
