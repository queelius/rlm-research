"""Source-gated model-visible tool-result clipping with complete raw session audit."""
import hashlib
import json
from pathlib import Path

import bv_study as s

def composed_engine_source():
    interface=s.base.o.qnative().stack().interface
    role=interface.e.capture.installed_hooks.__wrapped__.__globals__['role']
    adaptive=interface.e.a.overlay_program.__globals__['patch_engine']
    return adaptive(role.patch_engine(role.NANO_SOURCE.read_text()))

def patch_engine(source):
    before='''            self.session.log_tool_result(turn, tool_name, result, duration)
            content = truncate_tool_output(result)
'''
    if source.count(before)!=1:raise ValueError('exact composed tool-result seam required')
    after='''            self.session.log_tool_result(turn, tool_name, result, duration)
            _observation_view_config_path = Path(self.cwd) / '.observation_view.json'
            if not hasattr(self, '_observation_view_cap'):
                _observation_view_config = json.loads(_observation_view_config_path.read_text())
                if set(_observation_view_config) != {'schema', 'max_bytes'} or _observation_view_config['schema'] != 'bounded-observation-view-config-v1' or _observation_view_config['max_bytes'] not in (4096, 20000):
                    raise ValueError('invalid bounded observation view config')
                self._observation_view_cap = _observation_view_config['max_bytes']
            _observation_view_cap = self._observation_view_cap
            _observation_raw = result.encode('utf-8')
            if _observation_view_cap == 20000:
                content = truncate_tool_output(result)
            elif len(_observation_raw) <= _observation_view_cap:
                content = result
            else:
                _observation_keep = _observation_view_cap // 2
                _observation_head = _observation_raw[:_observation_keep].decode('utf-8', errors='ignore')
                _observation_tail = _observation_raw[-_observation_keep:].decode('utf-8', errors='ignore')
                content = (f"Warning: truncated output (original token count: {estimated_tokens(result)})\\n"
                           f"Total output lines: {result.count(chr(10)) + 1}\\n\\n"
                           f"{_observation_head}\\n[... {len(_observation_raw) - 2 * _observation_keep} bytes truncated ...]\\n{_observation_tail}")
            _observation_visible = content.encode('utf-8')
            _observation_record = {
                'schema':'bounded-observation-view-turn-v1', 'turn':turn,
                'raw_sha256':__import__('hashlib').sha256(_observation_raw).hexdigest(),
                'visible_sha256':__import__('hashlib').sha256(_observation_visible).hexdigest(),
                'raw_bytes':len(_observation_raw), 'visible_bytes':len(_observation_visible),
                'view_cap_bytes':_observation_view_cap,
                'clipped':len(_observation_raw)>_observation_view_cap,
                'omitted_bytes':max(0,len(_observation_raw)-_observation_view_cap),
                'raw_content':result, 'visible_content':content}
            with (Path(self.cwd) / '.observation_view.jsonl').open('a') as _observation_stream:
                _observation_stream.write(json.dumps(_observation_record, sort_keys=True)+'\\n')
'''
    result=source.replace(before,after);compile(result,'<bounded-observation-engine>','exec');return result

def render_for_test(raw,cap,turn):
    # Exact existing native truncation semantics, isolated for CPU contract tests.
    data=raw.encode('utf-8')
    if len(data)<=cap:visible=raw
    else:
        keep=cap//2;head=data[:keep].decode('utf-8',errors='ignore');tail=data[-keep:].decode('utf-8',errors='ignore')
        visible=(f'Warning: truncated output (original token count: {(len(raw)+3)//4})\nTotal output lines: {raw.count(chr(10))+1}\n\n{head}\n[... {len(data)-2*keep} bytes truncated ...]\n{tail}')
    vb=visible.encode();return visible,dict(turn=turn,raw_content=raw,visible_content=visible,raw_bytes=len(data),visible_bytes=len(vb),view_cap_bytes=cap,clipped=len(data)>cap,omitted_bytes=max(0,len(data)-cap),raw_sha256=hashlib.sha256(data).hexdigest(),visible_sha256=hashlib.sha256(vb).hexdigest())

def apply_to_roots(roots):
    source=composed_engine_source();expected=hashlib.sha256(source.encode()).hexdigest();replacement=patch_engine(source);changed=[]
    for root in roots:
        for path in Path(root).rglob('rlm/engine.py'):
            if not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest()==expected:
                path.write_text(replacement);changed.append(str(path))
    if not changed:raise RuntimeError('pinned composed engine not found')
    return {'patched':changed,'original_sha256':expected,'modified_sha256':hashlib.sha256(replacement.encode()).hexdigest()}

def overlay_program():
    source=composed_engine_source();expected=hashlib.sha256(source.encode()).hexdigest();replacement=patch_engine(source)
    return '''import hashlib,json,pathlib
expected=%r
replacement=%r
changed=[]
for root in [pathlib.Path('/tmp'),pathlib.Path('/root/.local/share/uv'),pathlib.Path('/root/.cache/uv')]:
    if not root.exists():continue
    for path in root.rglob('rlm/engine.py'):
        if path.is_symlink():continue
        if hashlib.sha256(path.read_bytes()).hexdigest()==expected:
            path.write_text(replacement);changed.append(str(path))
if not changed:raise RuntimeError('pinned composed engine not found')
print(json.dumps({'patched':changed,'original_sha256':expected,'modified_sha256':hashlib.sha256(replacement.encode()).hexdigest()}))
'''%(expected,replacement)
