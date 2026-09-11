"""CPU immutable sources/plans and worst-canonical-label native prefix budget."""
import json
import sm_study as s
import sm_protocol as p
import sm_native as n
import sm_collect as c

def main():
    values=p.build();binding=s.binding();values['BINDING.json']=binding;contexts={v['id']:v for v in values['PUBLIC.json']}
    values['ACQUISITION_REQUESTS.json']={r['id']:c.extraction_request(contexts[r['context_id']],r,binding) for r in values['ACQUISITION_PLAN.json']}
    checks=[];tokenizer=s.qnative().stack().native.renderer()._tokenizer
    for row in values['PLAN.json']:
        context=contexts[row['context_id']];query=values['QUERIES.json'][row['task_name']]['question'];raw=json.dumps({r['id']:'description and abstract concept' for r in context['records']},indent=2)
        task=n.task(context,query,row,raw);expected=n.expected(task,row)
        checks.append(dict(id=row['id'],representation=row['representation'],prefix_length=len(expected['token_ids']),prefix_token_sha256=s.digest(expected['token_ids']),cpu_map_fixture_only=True,root_max_tokens=2048,plain_query=query))
    source_checks=[]
    for identifier,body in values['ACQUISITION_REQUESTS.json'].items():
        ids=tokenizer.apply_chat_template(body['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False,return_dict=False)
        if len(ids)+1536>8192:raise ValueError('source budget')
        source_checks.append(dict(id=identifier,prompt_token_ids=ids,max_tokens=1536,typed_schema=body['structured_outputs']))
    values['NATIVE_PREPARATION.json']=dict(root_checks=checks,source_checks=source_checks,actual_map_prompts_frozen_after_acquisition=True,root_tools_and_optional_children_unchanged=True,common_query_file=True)
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    print(dict(inputs=len(values),roots=48,sources=8,max_fixture_prefix=max(r['prefix_length'] for r in checks)))
if __name__=='__main__':main()
