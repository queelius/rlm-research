"""Exact original adaptive batch contract, ordered canonical grammar."""
import importlib.util
import ast
import hashlib
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'adaptive-filter-pilot-v1/batch_contract.py'
if hashlib.sha256(p.read_bytes()).hexdigest()!='d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88':raise ValueError('batch contract changed')
s=importlib.util.spec_from_file_location('typed_adaptive_batch',p);batch=importlib.util.module_from_spec(s);s.loader.exec_module(batch)
LABELS=list(batch.LABELS)
def encoded(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def match_request(prompt,catalog):
    no={'matched':False,'reason':'not_exact_public_batch_contract'}
    if not isinstance(prompt,str) or prompt.count('\nRecords: ')!=1:return no
    try:
        rows=json.loads(prompt.split('\nRecords: ')[1]);ids=[r['id'] for r in rows]
        public={r['id']:r for r in catalog['records']}
        selected=[public[i] for i in ids]
        if len(ids)!=len(set(ids)) or batch.request_for(selected)!=prompt:return no
    except (ValueError,KeyError,TypeError):return no
    schema={'type':'object','properties':{i:{'type':'string','enum':LABELS[:]} for i in ids},'required':ids,'additionalProperties':False}
    ordered=encoded(schema)
    return {'matched':True,'reason':'exact_original_public_batch_contract','requested_ids':ids,'selected_records':selected,
        'request_text':prompt,'request_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'context_sha256':catalog['context_sha256'],
        'schema':schema,'schema_sha256':digest(schema),'schema_ordered_json':ordered,'schema_ordered_sha256':hashlib.sha256(ordered.encode()).hexdigest()}

# Same qualified invocation-bound decision implementation, compiled into this module's matcher scope.
p=Path(__file__).resolve().parents[1]/'typed-helper-child-v1/contract.py'
if hashlib.sha256(p.read_bytes()).hexdigest()!='8d65daeb671eded779c0c49ffa52586bb394f7ec44e147a33bce74cdf2863eb0':raise ValueError('typed invocation decision changed')
node=next(n for n in ast.parse(p.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='Decisions')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(p)+':batch-matcher-scope','exec'),globals())
BaseDecisions=Decisions
class Decisions(BaseDecisions):
    def choose(self,coordinate,arm,meta,messages,catalog):
        # Every operator arm uses the same typed-child treatment.
        return super().choose(coordinate,'typed',meta,messages,catalog)
