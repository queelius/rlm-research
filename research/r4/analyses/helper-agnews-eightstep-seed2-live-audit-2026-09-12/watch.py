"""Bounded CUDA-hidden replica watcher; reuse the already-reviewed training reporter."""
import argparse
import ast
import csv
import io
import json
import os
import sys
import time
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
EVAL=ROOT.parent.parent/"sidecars/helper-agnews-eightstep-seed2-eval-v1"
sys.path.insert(0,str(EVAL))
import bundle as b

study=b.study
actual_step_gate=b.actual_step_gate
SOURCE=ROOT.parent/"helper-agnews-eightstep-live-audit-2026-09-12/audit.py"
SOURCE_SHA="1e9bc38192127db6d2d8a13082445bcc1fe9facc1c0531dd09c64f65391cf917"
if study.sha(SOURCE)!=SOURCE_SHA:
    raise ValueError("qualified training reporter source changed")
names={"group_summary","step_report","write_text_x","snapshot","training_terminal_path","watch_training"}
tree=ast.parse(SOURCE.read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
if len(nodes)!=len(names):raise ValueError("exact reporter function inventory differs")
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),"exec"),globals())


def watch_outcomes(deadline,poll):
    import compare
    while time.monotonic()<deadline:
        terminal=study.attempt(b.ARM)/"OWNER_TERMINAL.json"
        if terminal.exists():
            report=compare.execute()
            study.write_x(ROOT/"outcomes/RAW_AUDIT.json",report)
            lines=["# Same512 seed2 raw audit","",
                   "Fixed training-seed replication on the same exposed panel; no seed selection.",""]
            for arm,value in report["arms"].items():
                m=value["metrics"]
                lines.append(f"{arm}: {m['correct']} correct /512 planned; "
                    f"{m['available_predictions']} available, {m['unavailable_predictions']} unavailable; "
                    f"complete={value['complete']}.")
            lines += ["","Paired later-arm gains/losses:"]
            for name,pair in report["comparisons"].items():
                lines.append(name+": "+(f"{pair['wins']}/{pair['losses']}, net {pair['net_correct_change']}; "
                    f"primary complete={pair['complete_primary_comparison']}" if pair["available"] else pair["reason"]))
            lines += ["","All128call clusters and512 planned records retained. Missing is not wrong.",
                      "Source-to-raw audit, not independent trainer implementation; class/cost details in JSON."]
            write_text_x(ROOT/"outcomes/READOUT.md","\n".join(lines)+"\n")
            return dict(status="REPLICA_EVAL_TERMINAL_RAW_AUDITED",report_sha256=study.sha(ROOT/"outcomes/RAW_AUDIT.json"))
        final_path=training_terminal_path()
        if final_path is not None and not study.read(final_path).get("primary_endpoint_eligible"):
            return dict(status="REPLICA_TRAINING_ABORTED_NOT_SCORED",training_terminal_sha256=study.sha(final_path))
        time.sleep(min(poll,max(0,deadline-time.monotonic())))
    return dict(status="CPU_WATCH_CAP",replica_endpoint_available=False)


def verify():
    ready=study.read(ROOT/"WATCH_READY.json")
    if study.digest({k:v for k,v in ready.items() if k!="identity"})!=ready["identity"]:
        raise ValueError("watcher identity differs")
    for path,expected in ready["closure_sha256"].items():
        if study.sha(path)!=expected:raise ValueError("watcher/source closure differs: "+path)
    return ready


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("training","outcomes","verify"))
    parser.add_argument("--seconds",type=int,default=14400)
    parser.add_argument("--poll",type=int,default=30)
    args=parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="" or args.seconds!=14400 or args.poll!=30:
        raise ValueError("CUDA-hidden bounded4h/poll30 only")
    ready=verify()
    if args.mode=="verify":
        print(ready["identity"]);raise SystemExit(0)
    started=time.monotonic()
    study.write_x(ROOT/args.mode/"WATCHER_START.json",dict(pid=os.getpid(),started_epoch=time.time(),
        cap_seconds=14400,poll_seconds=30,GPU_visible=False,ready_identity=ready["identity"]))
    try:
        result=(watch_training if args.mode=="training" else watch_outcomes)(started+14400,30)
    except BaseException as error:
        result=dict(status="AUDIT_FAILED",error=dict(type=type(error).__name__,message=str(error)))
        raise
    finally:
        study.write_x(ROOT/args.mode/"WATCHER_TERMINAL.json",result)
    print(json.dumps(result,sort_keys=True),flush=True)
