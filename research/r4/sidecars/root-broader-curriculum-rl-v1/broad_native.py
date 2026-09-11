"""Actual target-conditioned native tasks; public compatibility files, no host labels."""
import functools
import json
import sys
import broad_study as s
impl=s.private('native.py',{'study':s})

@functools.lru_cache(maxsize=1)
def stack():
    st=impl.stack();st.prior.ROOT=s.ROOT;st.prior.context_window_id=lambda c:c['native_context_id']
    sys.path.insert(0,str(s.ROOT));return st

impl.stack=stack if False else impl.stack
exact_turns=impl.exact_turns;validate_typed_audit=impl.validate_typed_audit

def prompt(context,task_name):
    return (f'The file context.txt contains the original {context["size"]} public records, with Date, User, and Instance fields. '
        'records.json is a compatibility JSON list with exactly id, user, and text: positional IDs q0001 onward in original file order, the same public User string, and the exact original Instance text. '
        'These files contain no category labels. Count records, not distinct users. Any child maps are predictions, not dataset labels.\n\n'+stack().native.e.DEFINITIONS+
        '\nYou may use Python and ordinary await rlm(prompt) to ask a child for help. batch_contract.py has pure request_for(batch) and strict_map(raw, ids) helpers. Neither calls a model or selects records. You may use the helpers, inspect text yourself, select any useful subsets/batches, or use another valid computation. No child call or full label map is required.\n'
        'Optional API example for one initial batch, not the final answer:\n```python\nimport json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords = json.load(open("records.json"))\nbatch = records[:4]\nchild = await rlm(request_for(batch))\nlabels = strict_map(child.answer, [r["id"] for r in batch])\nprint(labels)\n```\n'
        'The request helper uses IDs and original text, omitting User metadata. The decoder rejects duplicate/missing/unknown IDs, non-object JSON, trailing text and noncanonical categories; it does not check semantic correctness or repair answers. '
        'query.txt contains the original question below. Return only Answer: N with a nonnegative decimal integer.\n\nQuestion: '+s.question(task_name))

def make_task(context,task_name,answer):
    task=stack().native.task(context,prompt(context,task_name),answer,task_name)
    task.plain_query=s.question(task_name)
    task.data=task.data.model_copy(update={'source_split':'broader-'+context['source_partition']+'-'+context['stratum']})
    return task

def template():return s.read(s.SIDE/'root-corrective-reduction-sft-v1/inputs/NATIVE_TEMPLATE.json')
def first_prefix(task):
    value=template();return stack().native.renderer().render([value['system'],{'role':'user','content':task.data.prompt}],tools=json.loads(value['tools_ordered_json']),add_generation_prompt=True).token_ids

def interface(output):
    wrapper,_=s.runtime();st=wrapper.adapt_stack(stack())
    with s.aliases({'interface':st.interface}):value=st.local.configure_interface(output)
    sys.path.insert(0,str(s.ROOT));return value
