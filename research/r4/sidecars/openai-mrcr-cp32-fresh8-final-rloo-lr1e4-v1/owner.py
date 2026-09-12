"""Same finite process owner; MAIN admission only, no automatic follow-ons."""
import argparse
import study
implementation=study.bound('fresh8_lr10_owner',study.SOURCE_TRAIN/'owner.py',study=study)
run=implementation.run
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['verify','run']);a=p.parse_args()
    if a.action=='verify':
        import train
        print(train.preflight()[0]['identity'])
    else:raise SystemExit(run())
