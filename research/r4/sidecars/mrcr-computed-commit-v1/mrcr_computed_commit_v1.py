"""MRCR task/harness plugin with owned computed-submission transport only."""
import json

import study
from overlay import install_in_runtime

__all__ = ['CommitTaskset', 'CommitHarness']
CAPTURES = {}
OVERLAYS = {}


class CommitTaskset(study.old.MRCRTaskset):
    pass


class CommitHarness(study.old.MRCRHarness):
    async def setup(self, runtime):
        await super().setup(runtime)
        cap = study.read(study.ROOT / 'inputs/PUBLIC.json')['terminal_byte_cap']
        OVERLAYS[runtime.name] = await install_in_runtime(runtime, cap)

    async def cleanup(self, trace, runtime):
        try:
            program = '''import pathlib,json
p=pathlib.Path('/app/computed-commit-pair.json')
events=pathlib.Path('/app/computed-submissions')
print(json.dumps({'pair':json.loads(p.read_text()) if p.exists() else None,
'submissions':[json.loads(x.read_text()) for x in sorted(events.glob('turn-*.json'))],
'host_project_visible':pathlib.Path('/project/alex_phd').exists(),
'host_home_visible':pathlib.Path('/home/atowell').exists()}))
'''
            result = await runtime.run(['python3', '-c', program], {})
            if result.exit_code:
                raise RuntimeError('cannot retain submission evidence: ' + result.stderr)
            value = json.loads(result.stdout)
            if value['host_project_visible'] or value['host_home_visible']:
                raise ValueError('rootless filesystem boundary changed')
            value['overlay'] = OVERLAYS.pop(runtime.name)
            value['nano_before_overlay'] = study.old.INSTALL_PROVENANCE.pop(runtime.name)
            CAPTURES[trace.id] = value
        finally:
            await super().cleanup(trace, runtime)
