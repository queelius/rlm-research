import asyncio
import json
from types import SimpleNamespace

def test_root_only_role_condition_executes_actual_engine_method():
    import native as n
    original,modified=n.engine_sources()
    import ast
    tree=ast.parse(modified)
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and any(isinstance(v,ast.FunctionDef) and v.name=='_load_system_prompt' for v in x.body))
    method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_load_system_prompt')
    method.decorator_list=[]
    module=ast.Module(body=[method],type_ignores=[]);ast.fix_missing_locations(module)
    import os
    env={'os':os,'BuiltinTool':object,'build_system_prompt':lambda **kw:'original-'+str(kw['allow_recursion'])}
    exec(compile(module,'authored-native-method-test','exec'),env)
    from unittest.mock import patch
    fake=SimpleNamespace(depth=0,system_prompt_path=None,max_depth=1,mcp_servers=[],skills=[],append_to_system_prompt=None)
    # Compact root early return must precede any native default-prompt dependencies.
    with patch.dict(os.environ,{'QSR_DIAG_ROOT_ROLE':'compact'}):
        assert env['_load_system_prompt'](fake,[])=="Solve the user's task. Tools are optional. When finished, return only Answer: N with a nonnegative integer."
    assert modified.count('QSR_DIAG_ROOT_ROLE')==1

def test_task_writes_exact_public_files_no_gold(tmp_path):
    import native as n
    import study as s
    import protocol as p
    value=p.build();c=value['PUBLIC.json'][0];row=value['PLAN.json'][0];q=value['QUERIES.json'][row['task_name']]['question']
    task=n.task(c,q,row,None)
    assert task.data.prompt==p.prompt(c,q)
    assert task.plain_query==q and task.public_records==c['records']
