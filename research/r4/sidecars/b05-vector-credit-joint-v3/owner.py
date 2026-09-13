import argparse,study
owner_core=study.load("vector_joint_v3_owner",study.SHARED/"owner_core.py")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("action",choices=("verify","run"));a=p.parse_args()
 if a.action=="verify":
  import train;print(train.preflight()[0]["identity"])
 else:raise SystemExit(owner_core.run(study))
