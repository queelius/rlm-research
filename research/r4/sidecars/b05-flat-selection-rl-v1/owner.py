"""Unmodified finite PG subprocess lifecycle, with only this new study binding."""
import argparse
import study

def implementation():
    with study.aliases({'study':study},study.OLD):
        return study.load('selection_existing_finite_training_owner',study.OLD/'owner.py')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('verify','run'));args=parser.parse_args()
    if args.action=='verify':
        import train
        print(train.preflight()[0]['identity'])
    else:raise SystemExit(implementation().run())
