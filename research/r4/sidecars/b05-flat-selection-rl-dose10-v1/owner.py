"""Same finite one-step subprocess owner; no GPU admission implied by readiness."""
import argparse
import study as s

def implementation():
    with s.aliases({'study':s},s.ORIGINAL):return s.load('BA18_dose_original_owner',s.ORIGINAL/'owner.py').implementation()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('verify','run'));a=p.parse_args()
    if a.action=='verify':
        import train
        print(train.preflight()[0]['identity'])
    else:raise SystemExit(implementation().run())
