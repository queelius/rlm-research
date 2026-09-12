"""CLI for the unchanged bound128call/512record owner; MAIN alone launches."""
import argparse
import json
import bundle as b

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=("verify","qualify","run"))
    parser.add_argument("--arm",choices=(b.ARM,),default=b.ARM)
    parser.add_argument("--outer-seconds",type=int,default=900)
    args=parser.parse_args()
    if args.command == "verify":
        print(b.study.verify(args.arm)["identity"])
    elif args.command == "qualify":
        print(json.dumps(b.qualify(args.arm),sort_keys=True))
    else:
        terminal=b.owner.execute(args.arm,args.outer_seconds)
        print(json.dumps(terminal,sort_keys=True))
        raise SystemExit(0 if terminal["complete"] else 1)
