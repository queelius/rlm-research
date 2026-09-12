"""One new final/context; exact cached raw4, no helper/gold/cached-answer inputs."""
from types import ModuleType
import study

with study.aliases({'study':study},study.ROOT):
    text=(study.SERVICE_ROOT/'collect.py').read_text();assert text.count('132')==2
    source=ModuleType('answer_contract_native_collector');source.__file__=str(study.SERVICE_ROOT/'collect.py')+':12-call-cap'
    exec(compile(text.replace('132','12'),source.__file__,'exec'),source.__dict__)


class Collector(source.Collector):
    def question(self,index,item):
        payload=study.read(item['source_payload_path']);assert study.sha(item['source_payload_path'])==item['source_payload_sha256']
        assert len(payload['evidence'])==4 and payload['selected_ids']==sorted(p['idx'] for p in payload['evidence'])
        final=self.call(item,'concise',study.final_messages(payload))
        row={'record_id':item['record_id'],'question_index':index,'source_payload_sha256':item['source_payload_sha256'],
             'source_ids':payload['selected_ids'],'final_call_id':final['call_id'],'paired_final_seed':study.seed(index,'concise'),
             'instruction_sha256_canonical':study.digest(study.CONCISE_FINAL),'all_planned_roles_accounted':True}
        study.write_x(self.output/'questions'/(item['record_id']+'.json'),row);return row


source.Collector=Collector
execute=source.execute
