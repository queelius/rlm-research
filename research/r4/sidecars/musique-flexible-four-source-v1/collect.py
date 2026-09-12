"""Use qualified native call persistence; change only the five-call question graph."""
from types import ModuleType
import study

with study.aliases({'study':study},study.ROOT):
    text=(study.SERVICE_ROOT/'collect.py').read_text(); assert text.count('132')==2
    source=ModuleType('flexible_four_native_collector'); source.__file__=str(study.SERVICE_ROOT/'collect.py')+':60-call-cap'
    exec(compile(text.replace('132','60'),source.__file__,'exec'),source.__dict__)


class Collector(source.Collector):
    def question(self,index,item):
        public=study.read(item['public_path']); assert study.sha(item['public_path'])==item['public_sha256']
        halves=study.partition(public,item['record_id']); assert [[p['idx'] for p in h] for h in halves]==item['partition_indices']
        calls={}; selections=[]
        for role,half in zip(study.roles()[:2],halves):
            calls[role]=self.call(item,role,study.selector_messages(public,half))
            selections.append(study.selection(calls[role],half))
        calls['plan']=self.call(item,'plan',study.plan_messages(public,selections))
        planner=study.selection(calls['plan'],[v['paragraph'] for v in study.candidates(selections)])
        if study.shared_error(selections):
            planner.update(valid=False,model_error=False,paragraph_ids=[],paragraphs=[],error='shared_selector_invalid')
        order=list(study.ARMS if index%2==0 else tuple(reversed(study.ARMS))); payloads={}
        for arm in order:
            payloads[arm]=study.branch(public,selections,planner,arm)
            calls[arm]=self.call(item,arm,study.messages(payloads[arm],study.FINAL))
        result={'record_id':item['record_id'],'question_index':index,'hop':item['hop_count'],
                'partition_indices':item['partition_indices'],'selections':selections,'planner':planner,
                'shared_selector_call_ids':[calls[r]['call_id'] for r in study.roles()[:2]],
                'shared_selector_return_sha256':study.digest({r:calls[r] for r in study.roles()[:2]}),
                'candidate_pool_sha256':study.digest(study.candidates(selections)),
                'branch_payload_sha256':{a:study.digest(p) for a,p in payloads.items()},
                'branch_selected_ids':{a:p['selected_ids'] for a,p in payloads.items()},
                'branch_order':order,'paired_final_seed':study.seed(index,'fixed'),
                'calls':{r:v['call_id'] for r,v in calls.items()},'all_planned_roles_accounted':set(calls)==set(study.roles())}
        study.write_x(self.output/'questions'/(item['record_id']+'.json'),result)
        return result


source.Collector=Collector
execute=source.execute
