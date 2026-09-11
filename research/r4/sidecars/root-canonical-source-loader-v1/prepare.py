"""CPU pin actual reused sources, complete new paired requests and source modules."""
import json
import cl_study as s
import cl_protocol as p
import cl_native as n
import cl_collect as c

def main():
    values=p.build();values['BINDING.json']=s.binding();contexts={x['id']:x for x in values['PUBLIC.json']}
    maps={};source_checks=[];tokenizer=s.qnative().stack().native.renderer()._tokenizer
    for entry in values['REUSED_SOURCES.json']:
        record=entry['record'];context=contexts[entry['coordinate']['context_id']]
        verified=c.verify_source(record['raw_response'],record['request'],tokenizer)
        state=p.map_state(verified['content'],[r['id'] for r in context['records']])
        if not state['available'] or state!=record['map']:raise ValueError('actual source native/structural validation')
        if record['request']['model']!=values['BINDING.json']['fixed_child']:raise ValueError('child source identity')
        maps[context['id']]=state['raw']
        source_checks.append(dict(context_id=context['id'],source_path=entry['path'],source_sha256=entry['sha256'],
            raw_map_sha256=__import__('hashlib').sha256(state['raw'].encode()).hexdigest(),native_verified=True,semantic_gate=False))
    expected=[];modules={}
    for row in values['PLAN.json']:
        context=contexts[row['context_id']];raw=maps[context['id']];query=values['QUERIES.json'][row['task_name']]['question']
        task=n.task(context,query,row,raw);request=n.expected(task,row)
        expected.append(dict(coordinate=row,expected=request,task_hash=task.hash,root_action_tokens=2048,context_tokens=8192))
        modules[context['id']]=p.module_source(json.dumps(context['records'],ensure_ascii=False),raw)
    values['NATIVE_PREPARATION.json']=dict(roots=expected,source_checks=source_checks,actual_maps_not_fixtures=True,
        max_prefix=max(len(x['expected']['token_ids']) for x in expected),all_first_requests_frozen=True)
    values['SOURCE_MODULES.json']=modules
    for name,value in values.items():s.write(s.ROOT/'inputs'/name,value)
    print(dict(inputs=len(values),roots=len(expected),new_sources=0,reused_sources=len(source_checks),max_prefix=values['NATIVE_PREPARATION.json']['max_prefix']))

if __name__=='__main__':main()
