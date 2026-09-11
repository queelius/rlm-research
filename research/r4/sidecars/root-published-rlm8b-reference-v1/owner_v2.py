"""Additive physical-ledger reconciliation; frozen endpoint judgments remain exact."""
import argparse,copy,json,re,types
from pathlib import Path
import rv_study as s
OLD_READY='be084ff6109ed23ab4e78c0236382aadda9a89f1a15073e1350c97de04824b2f'
original=s.load('rv8b_owner_v1_for_v2',s.ROOT/'owner.py','f1f11bcea6b707f81379493e2e227458df7d8c177261372648fbe186fc4c4741')
original_harvest=original.harvest
def verify():
    if s.sha(s.ROOT/'READY.json')!=OLD_READY:raise ValueError('original READY changed')
    ready=s.read(s.ROOT/'READY_v2.json')
    if s.digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('V2 READY identity')
    for path,pin in ready['source_sha256'].items():
        if s.sha(path)!=pin:raise ValueError('V2 source changed: '+path)
    return ready
def usage(value):
    return value if isinstance(value,dict) and all(type(value.get(k)) is int and value[k]>=0 for k in ('prompt_tokens','completion_tokens')) else None
def identity(value,directory=None):
    role,index=value.get('role'),value.get('index')
    if role in ('root','child') and type(index) is int and index>=0:return role,index
    path=directory or (Path(value['request_path']).parent if value.get('request_path') else None)
    match=re.fullmatch(r'(root|child)-(\d+)',path.name) if path is not None else None
    if not match:raise ValueError('call lacks recorded role/index/path identity')
    return match[1],int(match[2])
def reconcile(directory,embedded):
    records={};duplicates=0;conflicts=[]
    for value in embedded:
        key=identity(value)
        if key in records:
            duplicates+=1
            if records[key]!=value:conflicts.append(dict(identity=list(key),embedded_versions=[records[key],value]))
            physical=bool(records[key].get('physical_attempt') or value.get('physical_attempt'))
            if usage(records[key].get('usage')) is None and usage(value.get('usage')) is not None:records[key]=copy.deepcopy(value)
            records[key]['physical_attempt']=physical
        else:records[key]=copy.deepcopy(value)
    disk_count=0
    for path in sorted((directory/'calls').glob('*')):
        if not path.is_dir():continue
        result_path,request_path,response_path=(path/name for name in ('RESULT.json','REQUEST.json','RESPONSE.json'))
        if not any(p.exists() for p in (result_path,request_path,response_path)):continue
        key=identity({},path);prior=records.get(key,{});disk=s.read(result_path) if result_path.exists() else {}
        if disk and identity(disk,path)!=key:raise ValueError('on-disk call identity/path mismatch')
        result={**prior,**disk};observed=None
        if response_path.exists():
            raw=s.read(response_path)
            try:body=json.loads(raw['body']);observed=usage(body.get('usage')) if isinstance(body,dict) else None
            except (ValueError,KeyError,TypeError):pass
        selected=observed or usage(disk.get('usage')) or usage(prior.get('usage'))
        if observed and usage(prior.get('usage')) and observed!=prior['usage']:conflicts.append(dict(identity=list(key),embedded_usage=prior['usage'],response_usage=observed))
        result.update(role=key[0],index=key[1],usage=selected,physical_attempt=bool(prior.get('physical_attempt') or disk.get('physical_attempt') or request_path.exists() or response_path.exists()),native_verified=bool(disk.get('native_verified',prior.get('native_verified',False))),ledger_path=str(path),request_path=str(request_path) if request_path.exists() else None,response_path=str(response_path) if response_path.exists() else None,result_path=str(result_path) if result_path.exists() else None,usage_source='raw_response' if observed else 'retained_result' if selected else 'unknown')
        records[key]=result;disk_count+=1
    values=[]
    for key,value in sorted(records.items()):
        value.update(role=key[0],index=key[1],ledger_path=str(directory/'calls'/f'{key[0]}-{key[1]:03d}'))
        values.append(value)
    return values,dict(embedded_records=len(embedded),duplicate_embedded_identities=duplicates,on_disk_identities=disk_count,reconciled_identities=len(values),conflicts=conflicts,endpoint_judgment_unchanged=True)
def harvest(output,policy):
    rows=original_harvest(output,policy)
    for row in rows:
        directory=output/policy/'rollout/episodes'/row['coordinate']['id']
        row['calls'],row['call_reconciliation']=reconcile(directory,row.get('calls',[]))
    return rows
def validate_argv(argv):
    if len(argv)!=10 or argv[:3]!=[str(s.NATIVE),str(s.ROOT/'collect_v2.py'),'--policy']:raise ValueError('exact V2 collector CLI')
    old=list(argv);old[1]=str(s.ROOT/'collect.py');return original_validate(old)
original_validate=original.validate_argv
def collector_argv(policy,deadline):
    root=s.ATTEMPT/policy;argv=[str(s.NATIVE),str(s.ROOT/'collect_v2.py'),'--policy',policy,'--endpoint',str(root/'service/endpoint-original.json'),'--output',str(root/'rollout'),'--deadline',str(deadline)];validate_argv(argv);return argv
original.harvest=harvest;original.collector_argv=collector_argv
def execute(output):
    original.s=types.SimpleNamespace(**{**vars(s),'verify':verify});return original.execute(output)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);a=ap.parse_args()
    if a.command=='verify':print(verify()['identity'])
    else:r=execute(a.output);print(r);raise SystemExit(0 if r['complete'] else 1)
