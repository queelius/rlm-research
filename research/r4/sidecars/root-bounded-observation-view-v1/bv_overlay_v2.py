"""V2 clipping overlay: raw evidence remains in the existing RLM session log."""
import hashlib

import bv_study as frozen_v1


def composed_engine_source():
    return frozen_v1.base.o.qnative().stack().interface.e.a.overlay_program.__globals__["patch_engine"](
        frozen_v1.base.o.qnative().stack().interface.e.capture.installed_hooks.__wrapped__.__globals__["role"].patch_engine(
            frozen_v1.base.o.qnative().stack().interface.e.capture.installed_hooks.__wrapped__.__globals__["role"].NANO_SOURCE.read_text()
        )
    )


def patch_engine(source):
    before = """            self.session.log_tool_result(turn, tool_name, result, duration)
            content = truncate_tool_output(result)
"""
    if source.count(before) != 1:
        raise ValueError("exact composed tool-result seam required")
    after = """            self.session.log_tool_result(turn, tool_name, result, duration)
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
                'type':'bounded_observation_view', 'turn':turn,
                'raw_sha256':__import__('hashlib').sha256(_observation_raw).hexdigest(),
                'visible_sha256':__import__('hashlib').sha256(_observation_visible).hexdigest(),
                'raw_bytes':len(_observation_raw), 'visible_bytes':len(_observation_visible),
                'view_cap_bytes':_observation_view_cap,
                'retained_payload_bytes':min(len(_observation_raw), _observation_view_cap),
                'marker_overhead_excluded_from_cap':True,
                'clipped':len(_observation_raw)>_observation_view_cap,
                'omitted_bytes':max(0,len(_observation_raw)-_observation_view_cap)}
            self.session.log(_observation_record)
"""
    result = source.replace(before, after)
    compile(result, "<bounded-observation-engine-v2>", "exec")
    return result


def overlay_program():
    source = composed_engine_source()
    expected = hashlib.sha256(source.encode()).hexdigest()
    replacement = patch_engine(source)
    return """import hashlib,json,pathlib
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
""" % (expected, replacement)
