"""V2 binding to the tested 192-slot collector implementation."""
import argparse,asyncio
from pathlib import Path
import owner,protocol as p,scoring,study as s
module=s.load('tag_match_v2_collect',s.V1/'collect.py','21fcdb167488d6f470a67d950f626368016befc8c531d88ec747863a35a59ffd',{'study':s,'protocol':p,'scoring':scoring,'owner':owner})
run=module.run;summarize=module.summarize
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('command',choices=('run',));a.add_argument('--endpoint',required=True,type=Path);a.add_argument('--output',required=True,type=Path);a.add_argument('--deadline',required=True,type=float);x=a.parse_args();owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',str(x.endpoint),'--output',str(x.output),'--deadline',str(x.deadline)]);print(asyncio.run(run(x.endpoint,x.output,x.deadline)))
