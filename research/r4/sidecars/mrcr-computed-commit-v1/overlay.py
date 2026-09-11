"""Exact-source patch installed only in a newly owned rootless container."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NANO_ENGINE = Path('/project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py')
ENGINE_SHA = '2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed'


def patched_engine(source):
    if hashlib.sha256(source.encode()).hexdigest() != ENGINE_SHA:
        raise ValueError('nano engine identity mismatch')
    before = 'logger = logging.getLogger(__name__)'
    after = 'from rlm.mrcr_submission import install, record_submission, finalize_pair\ninstall()\n\n' + before
    if source.count(before) != 1:
        raise ValueError('nano startup seam mismatch')
    source = source.replace(before, after)
    before = '            self._turn = turn + 1\n'
    after = '''            if self.depth == 0 and turn >= 5:
                self._metrics.stop_reason = "no_submission_within_five_root_turns"
                break
''' + before
    if source.count(before) != 1:
        raise ValueError('nano loop seam mismatch')
    source = source.replace(before, after)
    before = '            if self._should_compact(messages, usage, content):'
    after = '''            submission = getattr(tool_result, "submission", None)
            if self.depth == 0 and submission is not None:
                record_submission(self, submission, turn)
                if submission["accepted"]:
                    final_text = await finalize_pair(self, messages, submission, turn)
                    break

''' + before
    if source.count(before) != 1:
        raise ValueError('nano finalization seam mismatch')
    source = source.replace(before, after)
    before = '"extra_headers": model_call_headers(request_id),'
    after = '''"extra_headers": {**model_call_headers(request_id),
                "x-mrcr-submit-phase": "restatement" if getattr(self, "_computed_restatement", False) else "prefix",
                "x-mrcr-submit-request": request_id,
                "x-mrcr-submit-depth": str(self.depth)},'''
    if source.count(before) != 1:
        raise ValueError('nano request metadata seam mismatch')
    source = source.replace(before, after)
    before = '''            response = await call_with_retries(
                self.client.chat.completions.create, **request
            )'''
    after = '''            response = await self.client.with_options(max_retries=0).chat.completions.create(**request)'''
    if source.count(before) != 1:
        raise ValueError('nano one-attempt transport seam mismatch')
    return source.replace(before, after)


async def install_in_runtime(runtime, byte_cap):
    replacement = patched_engine(NANO_ENGINE.read_text())
    module = (ROOT / 'submission.py').read_text()
    program = f'''import hashlib,json,pathlib
source_sha={ENGINE_SHA!r}
replacement={replacement!r}
module={module!r}
found=[]
for root in [pathlib.Path('/tmp'),pathlib.Path('/root/.local/share/uv'),pathlib.Path('/root/.cache/uv')]:
    if not root.exists(): continue
    for p in root.rglob('rlm/engine.py'):
        if p.is_symlink(): continue
        if hashlib.sha256(p.read_bytes()).hexdigest()==source_sha:
            if hashlib.sha256((p.parent/'tools/ipython.py').read_bytes()).hexdigest()!='8a150675a8b4c0642a656866db6d8f9a1de6e3263371e573e744d2cdd5cd5757': raise RuntimeError('REPL source identity mismatch')
            if (p.parent/'mrcr_submission.py').exists(): raise RuntimeError('overlay already present')
            (p.parent/'mrcr_submission.py').write_text(module)
            p.write_text(replacement)
            found.append(str(p))
if not found: raise RuntimeError('pinned nano source not found in owned container')
print(json.dumps({{'patched':found,'engine_sha256':hashlib.sha256(replacement.encode()).hexdigest(),'module_sha256':hashlib.sha256(module.encode()).hexdigest()}}))
'''
    result = await runtime.run(['python3', '-c', program], {})
    if result.exit_code:
        raise RuntimeError('owned submission overlay failed: ' + result.stderr)
    # Explicit runtime task environment; never inherited provider credentials.
    runtime.env['MRCR_SUBMISSION_BYTE_CAP'] = str(byte_cap)
    return json.loads(result.stdout)
