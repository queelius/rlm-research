"""Actual native free task with truthful public fields and no algorithm demonstration."""
import functools
import json
import sys
import qsr_study as s
impl=s.private('native.py',{'study':s});_stack=impl.stack
@functools.lru_cache(maxsize=1)
def stack():
    st=_stack();st.prior.ROOT=s.ROOT;st.prior.context_window_id=lambda c:c['native_context_id']
    st.native.renderer=functools.lru_cache(maxsize=1)(st.native.renderer)
    sys.path.insert(0,str(s.ROOT));return st
impl.stack=stack
exact_turns=impl.exact_turns;validate_typed_audit=impl.validate_typed_audit
def prompt(context,query):
    return (f'The files records.json (a JSON list) and context.txt (one JSON object per line) contain the same {context["size"]} public records, with exactly the fields id, user, text, and weight. '
        'id identifies a record; user is its public user identity; text is the original question; weight is a visible positive integer belonging to that record. Neither file contains category labels. '
        'Any child labels are predictions, not dataset truth.\n\n'+stack().native.e.DEFINITIONS+
        '\nYou may use Python and await rlm(prompt) from rlm.api.run to ask a child for help. batch_contract.py exposes request_for(batch) and strict_map(raw, ids): the request helper includes record IDs and text, omitting user and weight; the decoder requires exactly the requested IDs and canonical categories. '
        'These helpers do not call a model, choose records, aggregate, check semantic correctness or repair responses. They are optional; no child call or full label map is required. '
        'query.txt contains the exact question below. The final response must contain only Answer: N.\n\nQuestion: '+query)
def make_task(context,query,gold,name):
    task=stack().native.task(context,prompt(context,query),gold,name);task.plain_query=query
    task.data=task.data.model_copy(update={'source_split':'scoped-root-catalog-new-child-train-exposed-'+context['stratum']})
    return task
def first_prefix(task):
    template=s.read(s.SIDE/'root-corrective-reduction-sft-v1/inputs/NATIVE_TEMPLATE.json')
    return stack().native.renderer().render([template['system'],{'role':'user','content':task.data.prompt}],tools=json.loads(template['tools_ordered_json']),add_generation_prompt=True).token_ids
def interface(output):
    wrapper,_=s.runtime();st=wrapper.adapt_stack(stack())
    with s.aliases({'interface':st.interface}):value=st.local.configure_interface(output)
    sys.path.insert(0,str(s.ROOT));return value

if __name__=='__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify-export',));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    from qsr_export import authenticate_export
    print(json.dumps(authenticate_export(a.output),sort_keys=True))
