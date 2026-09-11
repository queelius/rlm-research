"""Use the already-qualified exact one-context read-only mount validator."""
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'mrcr-rootless-document-baseline-v2/source/boundary.py'


def main():
    helpers = runpy.run_path(str(OLD))
    args = sys.argv[1:]
    if args and args[0] == 'run':
        args = helpers['bind_context'](args, ROOT / 'inputs', Path(os.environ['MRCR_SUBMIT_CONTEXT']))
    docker = ROOT.parent / 'rootless-runtime-feasibility-v1/bin/docker'
    os.execv(str(docker), [str(docker), *args])


if __name__ == '__main__':
    main()
