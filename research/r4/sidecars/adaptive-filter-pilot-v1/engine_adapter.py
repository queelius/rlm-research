"""Source shaping only; execution is in a newly owned pinned rootless runtime."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def patch_engine(source):
    before = '    async def _run_loop(self) -> RLMResult:\n'
    if source.count(before) != 1:
        raise ValueError('exactly one depth-zero run-loop seam required')
    source = source.replace(before, before + '''        if self.depth == 0:
            operator_config = Path(self.cwd) / 'operator_config.json'
            if operator_config.exists() and json.loads(operator_config.read_text())['controller'] != 'free':
                return await _adaptive_operator_loop(self)
''')
    # Retain the pinned tool execution/cancellation/scope cleanup block verbatim,
    # changing only its indentation and its honest non-model parent request ID.
    begin = source.index('                repl = self._repl\n')
    end = source.index('            duration = time.time() - t0\n', begin)
    block = source[begin:end]
    if block.count('self._invocation_id, call_id') != 1:
        raise ValueError('exactly one nullable spawning-request seam required')
    block = block.replace('self._invocation_id, call_id', 'self._invocation_id, None')
    block = '\n'.join(line[12:] if line.startswith('            ') else line for line in block.splitlines())+'\n'
    helper = '''
async def _adaptive_operator_loop(self):
    messages = self._messages
    tool_name = 'ipython'
    tool = get_builtin_tool(tool_name)
    program = (Path(self.cwd) / 'operator_program.py').read_text()
    tool_args = {'code': program}
''' + block + '''    for event in tool_result.metric_events:
        self._metrics.record(event)
    transcript_path = Path(self.cwd) / 'operator_result.json'
    transcript = json.loads(transcript_path.read_text()) if transcript_path.exists() else {
        'status': 'operator_execution_failure', 'answer': None}
    (Path(self.cwd) / 'operator_native.json').write_text(json.dumps({
        'operator_invocation': self._invocation_id,
        'session_relations': [{'invocation': key, 'parent_invocation': value.parent_session_id,
            'spawned_by_request_id': value.spawned_by_request_id, 'last_request_id': value.last_request_id}
            for key, value in self._semantic_edges._sessions.items()],
        'semantic_edges': self._semantic_edges.snapshot()}))
    self.session.write_meta(operator_controller={
        'kind': 'operator', 'root_behavior_likelihood': None,
        'transcript_path': str(transcript_path), 'status': transcript['status'],
        'tool_output': tool_result.content})
    self._metrics.stop_reason = 'done' if transcript['status'] == 'complete' else 'error'
    return RLMResult(answer=transcript['answer'] or '', session_dir=self.session.dir,
                     usage=self._total_usage, turns=0)
'''
    return source + helper


def overlay_program(role):
    original = role.patch_engine(role.NANO_SOURCE.read_text())
    modified = patch_engine(original)
    compile(modified, '<owned-adaptive-engine>', 'exec')
    return '''import hashlib,json,pathlib
expected = %r
replacement = %r
changed = []
for root in [pathlib.Path('/tmp'), pathlib.Path('/root/.local/share/uv'), pathlib.Path('/root/.cache/uv')]:
    if not root.exists(): continue
    for path in root.rglob('rlm/engine.py'):
        if path.is_symlink(): continue
        if hashlib.sha256(path.read_bytes()).hexdigest() == expected:
            path.write_text(replacement)
            changed.append({'path':str(path),'original_sha256':expected,'modified_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
if not changed: raise RuntimeError('pinned role-patched engine not found in owned runtime')
print(json.dumps({'patched':changed}))
''' % (hashlib.sha256(original.encode()).hexdigest(), modified)
