"""Record focused CPU test output without running a model or native container."""
import os
import subprocess
import time

import study as s


if __name__ == '__main__':
    command = [str(s.NATIVE), '-m', 'pytest', '-q', str(s.ROOT / 'test_diagnostic.py'),
               str(s.ROOT / 'test_native_boundary.py')]
    started = time.time()
    result = subprocess.run(command, cwd=s.ROOT, text=True, capture_output=True, timeout=180,
                            env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1'})
    evidence = dict(command=command, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr,
                    elapsed_seconds=time.time() - started, gpu_calls=0, native_container_calls=0,
                    earlier_red='5 missing implementation failures, then 2 native-flat-tool/usage regression failures; corrected before readiness')
    s.write(s.ROOT / ('CPU_TESTS.json' if result.returncode == 0 else 'CPU_FAILURE.json'), evidence)
    print(result.stdout)
    print(result.stderr)
    raise SystemExit(result.returncode)
