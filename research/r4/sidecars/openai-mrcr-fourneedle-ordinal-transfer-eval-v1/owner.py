"""Separate bounded owners for base and checkpoint32 ordinal-transfer arms."""
import importlib.util,sys
import checkpoint,study
text=(study.PARENT/"owner.py").read_text();_old={n:sys.modules.get(n) for n in ("study","checkpoint")};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    _spec=importlib.util.spec_from_loader("mrcr_fourneedle_owner_source",loader=None);source=importlib.util.module_from_spec(_spec);source.__file__=str(study.PARENT/"owner.py")+":fourneedle";exec(compile(text,source.__file__,"exec"),source.__dict__)
finally:
    for _n,_v in _old.items():
        if _v is None:sys.modules.pop(_n,None)
        else:sys.modules[_n]=_v
STAGES=source.STAGES;verify=source.verify;execute=source.execute
if __name__=="__main__":
    import argparse,json
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument("command",choices=["verify","run"]);p.add_argument("--stage",choices=tuple(STAGES),required=True);p.add_argument("--output",type=Path);p.add_argument("--outer-seconds",type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=="verify":print(verify(a.stage)["identity"])
    else:
        v=execute(a.stage,a.output or STAGES[a.stage]["output"],a.outer_seconds);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if v["complete"] else 1)
