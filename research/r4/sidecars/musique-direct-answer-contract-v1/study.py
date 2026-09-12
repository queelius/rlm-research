"""One universal final-answer instruction; all12 cached MuSiQue base4B source sets."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parent;PREVIOUS=ROOT.parent/'musique-source-quoted-relations-v1'
spec=importlib.util.spec_from_file_location('answer_contract_previous_study',PREVIOUS/'study.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
for name in ('read','sha','digest','write_x','load','aliases','base_owner','official','MODEL','MODEL_ALIAS','NATIVE','SYSTEM','FINAL','messages','decode','score_final','check_context','SERVICE_ROOT','PRIOR','FLEX'):
    globals()[name]=getattr(original,name)
INPUTS=ROOT/'inputs';READY=ROOT/'CPU_READY.json';ATTEMPT=ROOT/'outputs/attempt-001'
OWNER_SECONDS,SCIENCE_SECONDS,EXTERNAL_SECONDS=950,700,1050
NAMESPACE='musique-direct-answer-contract-v1-20260912'
ANSWER_RULE='In answer, write only the shortest standalone answer phrase, not an explanatory sentence or a restatement of the question. Retain necessary quantity qualifiers and include units when the question asks for a measurement. Do not change the entity or relation supported by the evidence, invent an absent bridge, or use outside information. If the supplied evidence is insufficient, say so concisely instead of guessing. Keep support_idxs as the original integer paragraph indices supporting the answer.'
CONCISE_FINAL=FINAL+' '+ANSWER_RULE


def roles():return ['concise']
def selected():return read(INPUTS/'MANIFEST.json')['selected']
def output_cap(role):return 1024
def seed(index,role):return 202609230003+16*index
def schedule():
    result=[]
    for index,item in enumerate(selected()):
        row={'record_id':item['record_id'],'question_index':index,'role':'concise','seed':seed(index,'concise'),'max_tokens':1024,'temperature':.5}
        result.append({**row,'call_id':digest([NAMESPACE,row])})
    return result


def baseline_messages(payload):
    # Frozen JSON files are key-sorted; restore the actual cached prompt's wire order.
    keys=('original_question','selected_ids','selection_error','evidence');assert set(payload)==set(keys)
    return messages({k:payload[k] for k in keys},FINAL)
def final_messages(payload):
    prompt=baseline_messages(payload)
    return [prompt[0],{'role':'user','content':prompt[1]['content']+' '+ANSWER_RULE}]
def request(prompt,role,sample_seed,n_paragraphs,tokenizer):
    assert role=='concise'
    return original.request(prompt,'relations',sample_seed,n_paragraphs,tokenizer)
def check_binding(binding):assert digest(binding)==read(INPUTS/'MANIFEST.json')['baseline_binding_sha256_canonical']
def verify():
    value=read(READY);assert value['identity']==digest({k:v for k,v in value.items() if k!='identity'})
    assert len(selected())==len(schedule())==12 and digest(schedule())==value['schedule_sha256']
    for path,want in value['closure_sha256'].items():assert sha(path)==want,path
    return value
