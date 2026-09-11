"""Actual embedded role-wire accounting; original and new work kept distinct."""
from pathlib import Path
import warm_study as study

SOURCE=study.ROOT.parents[1]/'analyses/root-sft24-terminal-rlvr-live-2026-09-10/wire_ledger.py'
SOURCE_SHA='d2715fdb2b91904efb94482f42064162046956cebced4ce2d81723d5fd3ad737'
implementation=study.load('warm_v3_embedded_wire_ledger',SOURCE,SOURCE_SHA)
ledger=implementation.ledger

def combined(original,current):
    old=ledger(original);new=ledger(current);a,b=old['summary'],new['summary']
    scalar=('routed_identity_count','confirmed_http_attempts','returned_native_completions','unresolved_dispatch_intents')
    total={key:a[key]+b[key] for key in scalar}
    for key in ('roles','http_status','usage_known','usage_unknown'):
        total[key]={name:a[key].get(name,0)+b[key].get(name,0) for name in a[key].keys()|b[key].keys()}
    total['integrity_errors']=a['integrity_errors']+b['integrity_errors']
    return dict(original=old,new=new,combined=total,original_group_not_reacquired=True,
                mirrored_audits_not_additional_calls=True,billing=None)
