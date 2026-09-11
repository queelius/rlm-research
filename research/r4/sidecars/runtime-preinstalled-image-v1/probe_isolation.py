"""One bounded initialization probe, preserving its exact outcome without retry."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import isolation as owned


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)


started = time.time()
write(owned.ROOT / 'ATTEMPT.json', {'started_epoch': started,
      'build_deadline_epoch': started + 900, 'build_cap_seconds': 900,
      'fixtures_maximum': 2, 'fixture_cap_seconds': 180, 'cpu_affinity': [32, 33],
      'store': str(owned.STORE), 'uid': os.getuid(),
      'scope': 'One private storage initialization/build attempt, no retries'})
owned.initialize()
argv, env = owned.command(['info', '--format', 'json'])
os.sched_setaffinity(0, {32, 33})
try:
    result = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=30)
    record = {'argv': argv, 'exit_code': result.returncode, 'stdout': result.stdout,
              'stderr': result.stderr, 'elapsed_seconds': time.time() - started,
              'home_preserved': env.get('HOME') == os.environ.get('HOME'),
              'scoped_env': {k: env[k] for k in ['XDG_RUNTIME_DIR', 'XDG_CONFIG_HOME',
                            'CONTAINERS_CONF', 'CONTAINERS_REGISTRIES_CONF', 'TMPDIR']}}
except subprocess.TimeoutExpired as error:
    record = {'argv': argv, 'exit_code': None, 'error': 'TimeoutExpired',
              'stdout': str(error.stdout), 'stderr': str(error.stderr),
              'elapsed_seconds': time.time() - started}
write(owned.ROOT / 'ISOLATION.json', record)
print(json.dumps(record), flush=True)
raise SystemExit(0 if record['exit_code'] == 0 else 2)
