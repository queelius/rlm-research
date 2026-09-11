"""Real native prompts, task files and composed collector argv, without GPU/services."""
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
import protocol as p
import study as s

class FilesRuntime:
    def __init__(self,name):self.name=name;self.files={}
    async def write(self,path,payload):self.files[path]=payload
    async def read(self,path,max_bytes):return self.files[path]
    async def run(self,argv,environment):
        assert argv==["mkdir","-p","state"] and environment=={}
        return SimpleNamespace(exit_code=0)

def test_actual_native_prompts_and_all_four_canonical_file_views(tmp_path):
    template=s.read(s.ROOT/"inputs/NATIVE_TEMPLATE.json")
    renderer=s.stack().native.renderer();tools=json.loads(template["tools_ordered_json"])
    rows=s.read(s.ROOT/"inputs/PLAN.json");assert len(rows)==64
    prompts={r["id"]:r for r in s.read(s.ROOT/"inputs/PROMPTS.json")}
    states={r["source_id"]:r for r in s.read(s.ROOT/"inputs/STATES.json")}
    public={r["id"]:r for r in s.read(s.ROOT/"inputs/PUBLIC.json")}
    packages=s.read(s.ROOT/"inputs/PACKAGES.json")
    for row in rows:
        text=prompts[row["id"]]["prompt"];ids=renderer.render([template["system"],dict(role="user",content=text)],tools=tools,add_generation_prompt=True).token_ids
        assert ids==prompts[row["id"]]["token_ids"] and len(ids)+2048<=8192
    for width in (4,16):
        source=next(v for v in states.values() if v["width"]==width);views=[]
        for row in [r for r in rows if r["source_id"]==source["source_id"]]:
            task=s.task(public[row["context_id"]],prompts[row["id"]]["prompt"],source["goal"],row,packages[row["source_id"]],tmp_path)
            runtime=FilesRuntime(row["id"]);asyncio.run(task.setup(None,runtime))
            assert task.hash==prompts[row["id"]]["task_hash"] and task.data.dataset==s.ROOT.name
            assert runtime.files["query.txt"]==source["goal"].encode();views.append(runtime.files)
        assert len(views)==4 and all(v==views[0] for v in views)

def test_owner_and_collector_exact_namespace_and_null_slots(tmp_path):
    import owner
    import collect
    import pytest
    args=collect.parse_args(owner.collector_argv(tmp_path/"service",s.ATTEMPT/"rollout",1234)[2:])
    assert args.output==s.ATTEMPT/"rollout" and args.deadline==1234
    with pytest.raises(ValueError):owner.check_output(tmp_path/"wrong")
    rows=[{"id":f"row{i}"} for i in range(64)]
    missing=collect.planned_results(rows,{})
    assert len(missing)==64 and all(r["reward"] is None for r in missing)
