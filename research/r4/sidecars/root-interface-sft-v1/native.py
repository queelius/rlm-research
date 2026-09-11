"""Private free-root tasks over the pinned real native harness; no scripted operator."""
import sys
import study as s
e=s.load('interface_pinned_adaptive',s.ROOT.parent/'adaptive-filter-pilot-v1/experiment.py','ed7f94db1cb2d6b6ce30c4d78999fdc6b722f6195c39092429a029379f52e32d')
sys.path.insert(0,str(s.ROOT))

def task(context,prompt,answer,name):
    prototype=e.fixture_task('free')
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(s.BASE/'tokenizer.json'))
    cid=s.context_window_id(context)
    result=e.AdaptiveTask(prototype.data.model_copy(update={'name':name,'prompt':prompt,'context':context['text'],'answer':repr([answer]),'dataset':s.ROOT.name,'context_window_id':cid,'source_id':24000000+cid,'idx':cid,'source_split':'new-root-disjoint-leaf-train-supported-'+context['stratum'],'context_len':len(tokenizer.encode(context['text'],add_special_tokens=False).ids)}),prototype.config)
    result.public_records,result.plain_query,result.controller=context['records'],prompt,'free'
    return result

def initial_binding():
    binding=e.prior.binding_for(e.c.read(e.old.ROOT/'SPEC.json')['policies']['step8'])
    model=binding['models'][binding['role_map']['root']]
    if model['path']!=str(s.START) or model['adapter_sha256']!=s.START_SHA:raise ValueError('historical start changed')
    return binding

def renderer():
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    return create_renderer(load_tokenizer(str(s.BASE)),Qwen3RendererConfig(enable_thinking=True))

def tool_action(code):
    import json
    return '<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':code}})+'\n</tool_call>'

def wire_tools(saved):
    # Saved trace JSON sorts mappings. Restore native IPython schema construction order,
    # then use the actual native Tool->wire conversion. Qualified against physical tokens.
    from verifiers.v1.clients.train import tool_to_wire
    from verifiers.v1.types import Tool
    result=[]
    for original in saved:
        p=original['parameters']
        parameters={'type':p['type'],'properties':{k:{'type':v['type'],'description':v['description']} for k,v in p['properties'].items()},'required':p['required']}
        result.append(tool_to_wire(Tool.model_validate({**original,'parameters':parameters})))
    return result
