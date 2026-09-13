import argparse
from pathlib import Path
import study
trainer=study.load("vector_joint_v3_trainer",study.SHARED/"trainer.py");preflight=lambda:trainer.preflight(study)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--seconds",type=int,required=True);a=p.parse_args();trainer.run(study,a.output,a.seconds)
