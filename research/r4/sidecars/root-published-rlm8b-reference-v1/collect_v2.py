"""Authenticate historical current-block FINAL_VAR before standalone parsing."""
import argparse,re,types
from pathlib import Path
import rv_study as s
import owner_v2
original=s.load('rv8b_collector_v1_for_v2',s.ROOT/'collect.py','95c8e4b2f1810516ea8b0652628f86f600df70a0a479a9f39b380a67b5475b3d')
def final_capture(result,calls,active):
    terminal=result.get('terminal') or {};final=terminal.get('final');events=result.get('events',[])
    if not isinstance(final,str) or terminal.get('error') or active:return False
    roots=[c for c in calls if c['role']=='root'];positions=[i for i,e in enumerate(events) if e['kind']=='iteration']
    if not roots or not positions or not roots[-1].get('native_verified'):return False
    text=roots[-1]['content'];current=events[positions[-1]]['value']
    if current['response']!=text or current['final']!=final:return False
    begin=positions[-2]+1 if len(positions)>1 else 0
    observations=[e['value'] for e in events[begin:positions[-1]] if e['kind']=='observation']
    blocks=[block.strip() for block in re.findall(r'```repl\s*\n(.*?)\n```',text,re.S)]
    if 'code' in current and current['code']!=blocks:return False
    # Historical core selects the first truthy executed block final before regex parsing.
    for observation in observations:
        if observation['code'] in blocks and observation.get('final_answer'):
            return observation['final_answer']==final
    var=re.search(r'^\s*FINAL_VAR\((.*?)\)',text,re.M|re.S)
    if var:
        name=var[1].strip().strip('"').strip("'");code=f'print(FINAL_VAR({name!r}))'
        return bool(observations and observations[-1]['code']==code and observations[-1]['stdout'].strip()==final and not observations[-1]['stderr'])
    literal=re.search(r'^\s*FINAL\((.*)\)\s*$',text,re.M|re.S)
    return bool(literal and literal[1].strip()==final)
original.final_capture=final_capture
def run(policy,endpoint,output,deadline):
    original.s=types.SimpleNamespace(**{**vars(s),'verify':owner_v2.verify});return original.run(policy,endpoint,output,deadline)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--policy',required=True,choices=('base','rlm'));ap.add_argument('--endpoint',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--deadline',required=True,type=float);a=ap.parse_args()
    owner_v2.validate_argv([str(s.NATIVE),str(s.ROOT/'collect_v2.py'),'--policy',a.policy,'--endpoint',str(a.endpoint),'--output',str(a.output),'--deadline',str(a.deadline)])
    print(run(a.policy,a.endpoint,a.output,a.deadline))
