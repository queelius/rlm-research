"""Exact public source contract; no gold and no helper-origin attribution."""
import hashlib
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]/'root-receipt-ablation-v1/receipt_api.py'
SOURCE_SHA='4ffaccc9ad15ee088ab1f6d50545a8d9bf269cf2481febaf5bf5d42e333706a6'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA: raise ValueError('helper changed')
spec=importlib.util.spec_from_file_location('typed_public_helper',SOURCE)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
LABELS=['human being','location','abbreviation','entity','description and abstract concept','numeric value']
PREFIX=('Answer the query for each supplied source record. Return only a JSON object mapping each supplied source id to its label string. '
        'Copy each supplied id exactly once as a key; no missing or extra ids. Each value must be one of the allowed values.\nQuery: ')

def encoded(value): return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def match_request(prompt,catalog):
    def no(reason): return {'matched':False,'reason':reason}
    if not isinstance(prompt,str) or not prompt.startswith(PREFIX): return no('not_exact_helper_prefix')
    if prompt.count('\nAllowed values: ')!=1 or prompt.count('\nRecords: ')!=1: return no('ambiguous_delimiters')
    try:
        query,tail=prompt[len(PREFIX):].split('\nAllowed values: ')
        values,records=tail.split('\nRecords: ')
        labels=json.loads(values);records=json.loads(records)
        if not isinstance(labels,list) or len(labels)!=6 or set(labels)!=set(LABELS): return no('noncanonical_vocabulary')
        if not isinstance(records,list) or not records: return no('invalid_record_list')
        ids=[r['id'] for r in records]
        rebuilt,provenance=helper.build_request(catalog,ids,query,labels)
        if rebuilt!=prompt: return no('exact_public_roundtrip_failed')
    except (ValueError,TypeError,KeyError): return no('invalid_or_unknown_source_contract')
    schema={'type':'object','properties':{i:{'type':'string','enum':list(LABELS)} for i in ids},'required':ids,'additionalProperties':False}
    ordered=encoded(schema)
    return {'matched':True,'reason':'exact_public_six_label_contract','requested_ids':ids,'query':query,
            'request_text':prompt,'request_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
            'context_sha256':catalog['context_sha256'],'selected_records':provenance['selected_records'],
            'schema':schema,'schema_sha256':digest(schema),'schema_ordered_json':ordered,
            'schema_ordered_sha256':hashlib.sha256(ordered.encode()).hexdigest()}

class Decisions:
    def __init__(self): self.values={}

    def choose(self,coordinate,arm,meta,messages,catalog):
        key=(coordinate,meta['invocation'])
        if key not in self.values:
            if meta['depth']==0: value={'matched':False,'reason':'root_unconstrained'}
            elif meta['depth']!=1 or meta['kind']!='ordinary': value={'matched':False,'reason':'nonordinary_initial_child'}
            else:
                users=[m.get('content') for m in messages if m.get('role')=='user']
                value=match_request(users[0],catalog) if len(users)==1 else {'matched':False,'reason':'ambiguous_initial_task_messages'}
            self.values[key]={**value,'apply':arm=='typed' and value['matched'],'coordinate_id':coordinate,
                'arm':arm,'invocation':meta['invocation'],'depth':meta['depth'],'decision_before_first_dispatch':True}
        return self.values[key]
