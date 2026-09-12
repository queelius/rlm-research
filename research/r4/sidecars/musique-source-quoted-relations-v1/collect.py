"""Two new physical calls/question; never load gold or cached final answers."""
from types import ModuleType
import study

with study.aliases({'study':study},study.ROOT):
    text=(study.SERVICE_ROOT/'collect.py').read_text();assert text.count('132')==2
    source=ModuleType('source_quoted_native_collector');source.__file__=str(study.SERVICE_ROOT/'collect.py')+':24-call-cap'
    exec(compile(text.replace('132','24'),source.__file__,'exec'),source.__dict__)


class Collector(source.Collector):
    def question(self,index,item):
        payload=study.read(item['source_payload_path']);assert study.sha(item['source_payload_path'])==item['source_payload_sha256']
        assert len(payload['evidence'])==4 and payload['selected_ids']==sorted(p['idx'] for p in payload['evidence'])
        extract=self.call(item,'extract',study.extract_messages(payload));value=study.report(extract,payload['evidence'])
        final=self.call(item,'relations',study.final_messages(payload,value))
        row={'record_id':item['record_id'],'question_index':index,'source_payload_sha256':item['source_payload_sha256'],
             'source_ids':payload['selected_ids'],'extract_call_id':extract['call_id'],'report':value,
             'final_call_id':final['call_id'],'paired_final_seed':study.seed(index,'relations'),
             'raw_sources_preserved_even_report_invalid':True,'all_planned_roles_accounted':True}
        study.write_x(self.output/'questions'/(item['record_id']+'.json'),row);return row


source.Collector=Collector
execute=source.execute
