"""Six physical calls per context. Summary requests see only validated selections."""
import ast
from types import ModuleType
import study

with study.aliases({'study':study},study.ROOT):
    text=(study.SERVICE_ROOT/'collect.py').read_text()
    assert text.count('132')==2
    source=ModuleType('evidence_authenticated_native_collector')
    source.__file__=str(study.SERVICE_ROOT/'collect.py')+':72-call-cap'
    exec(compile(text.replace('132','72'),source.__file__,'exec'),source.__dict__)


class Collector(source.Collector):
    def question(self,index,item):
        public=study.read(item['public_path']);assert study.sha(item['public_path'])==item['public_sha256']
        halves=study.partition(public,item['record_id'])
        assert [[p['idx'] for p in h] for h in halves]==item['partition_indices']
        calls={};selections=[]
        for side,label in enumerate(('left','right')):
            role='select_'+label
            calls[role]=self.call(item,role,study.selector_messages(public,halves[side]))
            selections.append(study.selection(calls[role],halves[side]))
        summaries=[]
        for side,label in enumerate(('left','right')):
            role='summary_'+label
            calls[role]=self.call(item,role,study.summary_messages(public,selections[side]))
            summaries.append(calls[role]['text'] if calls[role]['transport_valid'] else 'SUMMARY_TRANSPORT_UNAVAILABLE')
        order=list(study.ARMS if index%2==0 else tuple(reversed(study.ARMS)))
        for arm in order:
            calls[arm]=self.call(item,arm,study.final_messages(public,selections,summaries,arm))
        value={'record_id':item['record_id'],'question_index':index,'hop':item['hop_count'],
               'partition_indices':item['partition_indices'],'selections':selections,
               'shared_helper_call_ids':[calls[r]['call_id'] for r in study.roles()[:4]],
               'shared_helper_return_sha256':study.digest({r:calls[r] for r in study.roles()[:4]}),
               'selected_source_sha256':study.digest([s['paragraphs'] for s in selections]),
               'both_final_evidence_empty_on_selector_error':not all(s['valid'] for s in selections),
               'branch_order':order,'paired_final_seed':study.seed(index,'summary'),
               'calls':{r:v['call_id'] for r,v in calls.items()},'all_planned_roles_accounted':set(calls)==set(study.roles())}
        study.write_x(self.output/'questions'/(item['record_id']+'.json'),value)
        return value


source.Collector=Collector
execute=source.execute
