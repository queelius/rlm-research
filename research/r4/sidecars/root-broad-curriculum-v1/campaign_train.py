"""Same native root-only TIS/Adam update; exact24-row fresh group admission."""
import argparse
import json
import traceback
import uuid
from collections import Counter

import campaign_common as c


def validate_collection(manifest, rows, plans):
    if (len(plans) != 24 or len({r['id'] for r in plans}) != 24
            or sorted(Counter(r['task_name'] for r in plans).values()) != [8,8,8]
            or manifest['recorded'] != 24 or manifest['planned'] != 24
            or manifest['integrity_failures'] or len(rows) != 24):
        raise ValueError('complete declared24 without integrity failures required')
    expected = {r['id']:(r['task_name'],r['seed']) for r in plans}
    if len({r['episode_id'] for r in rows}) != 24 or {r['episode_id'] for r in rows} != expected.keys():
        raise ValueError('duplicate, missing, or stale coordinates')
    if any(r['split'] != 'training' or (r['task_id'],r['sample_seed']) != expected[r['episode_id']] for r in rows):
        raise ValueError('nontraining or altered task/seed coordinates')


trainer = c.adapted('broad_private_trainer',c.OLD/'campaign_train.py',[
    ('declared fresh32','declared fresh24',1),
    ('if manifest["recorded"] != 32 or manifest["planned"] != 32 or manifest["integrity_failures"]:',
     'if manifest["recorded"] != 24 or manifest["planned"] != 24 or manifest["integrity_failures"]:',1),
    ('complete32 without integrity failures required','complete24 without integrity failures required',1),
    ('if {r["episode_id"] for r in rows} != {r["id"] for r in plans} or any(r["split"] != "training" for r in rows):\n        raise ValueError("nontraining, duplicate, or stale coordinates")',
     'validate_collection(manifest, rows, plans)',1)], {'validate_collection':validate_collection})


def __getattr__(name):
    return getattr(trainer,name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group',type=c.Path,required=True)
    parser.add_argument('--generation',type=c.Path,required=True)
    parser.add_argument('--output',type=c.Path)
    parser.add_argument('--deadline',type=float,default=float('inf'))
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args()
    try:
        print(json.dumps(trainer.train(args),sort_keys=True,allow_nan=False))
    except BaseException as error:
        if args.output is not None:
            c.write_once(args.output.parent/('TRAIN_FAILURE-'+uuid.uuid4().hex+'.json'),
                {'type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc(),'checkpoint_preserved':True})
        raise


if __name__ == '__main__':
    main()
