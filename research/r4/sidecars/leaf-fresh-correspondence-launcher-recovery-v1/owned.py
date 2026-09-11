"""MAIN-invoked unique recovery operation; not an automatic retry."""
import argparse
from pathlib import Path
import recovery as r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=r.ROOT/'owned/attempt-001');p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.verify:
        r.verify();print('recovery source/science/owner-root verified; GPU calls0')
    else:
        result=r.execute(a.directory);print(result);raise SystemExit(0 if result['complete'] else 1)
