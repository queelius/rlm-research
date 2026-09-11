"""Real task/setup/tokenizer with filesystem-only runtime double; no containers/services."""
import asyncio
import hashlib
import json
from types import SimpleNamespace
import study as s

class FilesRuntime:
    def __init__(self,name):self.name=name;self.files={};self.commands=[]
    async def write(self,path,payload):self.files[path]=payload
    async def read(self,path,max_bytes):return self.files[path]
    async def run(self,argv,environment):
        assert argv==['mkdir','-p','state'] and environment=={}
        self.commands.append(argv);return SimpleNamespace(exit_code=0)

def test_actual_setup_has_byte_equal_goal_and_all_evidence_across_three_prompts(tmp_path):
    public={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')}
    plan=s.read(s.ROOT/'inputs/PLAN.json');states={v['source_id']:v for v in s.read(s.ROOT/'inputs/STATES.json')}
    packages=s.read(s.ROOT/'inputs/PACKAGES.json');prompts={r['id']:r for r in s.read(s.ROOT/'inputs/PROMPTS.json')}
    # One of each width exercises whole-map and overwritten-last-batch source representations.
    for width in (4,16):
        source=next(v for v in states.values() if v['width']==width);views=[];texts=[]
        for row in [r for r in plan if r['source_id']==source['source_id']]:
            task=s.task(public[row['context_id']],prompts[row['id']]['prompt'],source['goal'],row,packages[row['source_id']],tmp_path)
            runtime=FilesRuntime(row['id']);asyncio.run(task.setup(None,runtime))
            assert task.data.prompt==prompts[row['id']]['prompt'] and task.plain_query==source['goal']
            assert task.data.dataset=='root-artifact-restart-v1' and task.hash==prompts[row['id']]['task_hash']
            assert runtime.files['query.txt']==source['goal'].encode()
            assert 'operator_program.py' not in runtime.files and len(runtime.commands)==1
            report=s.read(tmp_path/(row['id']+'.json'))
            assert report['file_sha256']=={k:hashlib.sha256(v).hexdigest() for k,v in runtime.files.items()}
            views.append(runtime.files);texts.append(task.data.prompt)
        assert views[0]==views[1]==views[2] and len(set(texts))==3

def test_all_real_source_cuts_and_new_user_prompts_are_native_token_exact():
    renderer=s.stack().native.renderer();template=s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json');tools=json.loads(template['tools_ordered_json'])
    cuts=s.read(s.ROOT/'inputs/SOURCE_CUTS.json')
    assert len(cuts)==16
    for cut in cuts.values():
        assert renderer.render(cut['messages'],tools=tools,add_generation_prompt=True).token_ids==cut['prefix_token_ids']
    prompts=s.read(s.ROOT/'inputs/PROMPTS.json');assert len(prompts)==48
    for prompt in prompts:
        assert renderer.render([template['system'],dict(role='user',content=prompt['prompt'])],tools=tools,add_generation_prompt=True).token_ids==prompt['token_ids']
        assert len(prompt['token_ids'])+2048<=8192
