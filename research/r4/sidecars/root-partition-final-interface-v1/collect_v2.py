"""Original sealed collector with authenticated wrong-route scoring and amended argv only."""
import argparse
import asyncio
from pathlib import Path
from types import ModuleType
import study as s
import scoring_v2
import owner_v2

SOURCE=s.ROOT/'collect.py'
if s.sha(SOURCE)!='d653713de528181fd197bc76ed2d70716cc254a61f07d1cf187641e2a6416c5b':raise ValueError('original sealed collector changed')
text=SOURCE.read_text()
for before,after,count in [('    import owner\n','    import owner_v2 as owner\n',1),("s.ROOT/'collect.py'","s.ROOT/'collect_v2.py'",1),('native_verified=True,content=content,usage=usage','native_verified=True,wrong_route=bool(raw["choices"][0]["message"].get("tool_calls")) or finish=="tool_calls",content=content,usage=usage',1)]:
    if text.count(before)!=count:raise ValueError('collector amendment seam changed: '+before)
    text=text.replace(before,after)
module=ModuleType('partition_collector_scoring_v2');module.__file__=str(Path(__file__).resolve())
exec(compile(text,str(SOURCE)+':scoring-amendment-v2','exec'),module.__dict__)
module.verified_response=scoring_v2.verified_response

async def run(args):
    owner_v2.verify_ready();return await module.run(args)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('run',));ap.add_argument('--endpoint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);args=ap.parse_args()
    status=asyncio.run(run(args));print(status);raise SystemExit(0 if status['complete'] else 2)
