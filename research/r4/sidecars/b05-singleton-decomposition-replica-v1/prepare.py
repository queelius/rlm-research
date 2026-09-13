"""Narrow source-bound reuse of public-first singleton176 freeze, changed cells/counts only."""
import itertools
import types
import study as s


def revisions(study):
    rows=[]
    for task in study.read(study.INPUTS)['tasks']:
        groups={}
        for r in task['raw_public_view']['stage']['tables']['checks']:
            groups.setdefault((r['implementation_id'],r['check_name']),[]).append(r)
        flips=[]
        for (identifier,name),values in groups.items():
            values=sorted(values,key=lambda r:r['revision'])
            if len({r['passed'] for r in values})>1:flips.append({'implementation_id':identifier,'check_name':name,'revisions':[[r['revision'],r['passed']] for r in values]})
        rows.append({'root_id':task['root_id'],'history_depth':task['history_depth'],'check_revisions':task['check_revisions'],'flip_groups':flips})
    study.write_x(study.ROOT/'CHECK_REVISION_PROVENANCE.json',{'rows':rows,'no_selection_by_flips':True,'model_receives_only_resolved_latest_checks':True})


def implementation():
    path=s.PRIOR/'prepare.py';assert s.sha(path)=='99540f86c96585c064b8c9332a15b8dd4965a6dc38339ffd487fe2ce98332733'
    text=path.read_text()
    changes=[
        ("vector=s.load('singleton_unchanged_vector_contract',s.PRIOR/'interface.py')","vector=s.load('singleton_unchanged_vector_contract',s.ROOT.parent/'b05-decision-vector-v1/interface.py')",1),
        ("dimensions=[(6,0),(6,1),(12,2),(12,0),(20,1),(20,2)]","dimensions=[(w,h,c,i%3) for i,(w,h,c) in enumerate(itertools.product((6,12,20),(1,3),(1,3)))]",1),
        ('for index,(width,stage_index) in enumerate(dimensions):','for index,(width,history,checks,stage_index) in enumerate(dimensions):',1),
        ('api.StructuralConfig(width,1,1,3,1,','api.StructuralConfig(width,history,checks,3,1,',1),
        ('202609420000','202609490000',3),('202609420005','202609490011',2),
        ('202609430000','202609500000',2),('202609430011','202609500023',1),
        ('history_depth=1,check_revisions=1,selected_stage=','history_depth=history,check_revisions=checks,selected_stage=',1),
        ('history_depth=1,repeat=','history_depth=history,check_revisions=checks,repeat=',1),
        ("arms=['list','vector','singleton'];rotation=(index+repeat)%3","arms=['vector','singleton'];rotation=(index+repeat)%2",1),
        ('len(calls)==176 and len(tasks)==6 and sum(t[\'width\'] for t in tasks)==76','len(calls)==328 and len(tasks)==12 and sum(t[\'width\'] for t in tasks)==152',1),
        ("{'singleton':152,'list':12,'vector':12}","{'singleton':304,'vector':24}",1),
        ('singleton176','singleton328',1),('    host=[]','    revisions(s)\n    host=[]',1),
        ("'test_singleton.py'","'test_replica.py'",1),
        ("'First parser/union test failed before interface.py existed; then passed after implementation.'","'Actual replica schedule test failed before public inputs existed; then passed after the new freeze.'",1),
        ('decomposition176-ready','decomposition328-ready',1),
        ("context_units=6,paired_seed_units=12,stage_arm_outputs=36,planned_physical_calls=176,physical_by_arm={'list':12,'vector':12,'singleton':152}","context_units=12,paired_seed_units=24,stage_arm_outputs=48,planned_physical_calls=328,physical_by_arm={'vector':24,'singleton':304}",1),
        ("arms=['list','vector','singleton'],all_new_cases=True,dimensions=dimensions,history_depth=1,check_revisions=1,","arms=['vector','singleton'],all_new_cases=True,dimensions=dimensions,width32_unsupported_deferred=True,",1),
        ("max_tokens={'list':384,'vector':384,'singleton':16}","max_tokens={'vector':384,'singleton':16}",1),
        ("('list','vector','singleton')","('vector','singleton')",2),
        ('all12 tasks/arm','all24 tasks/arm',1)]
    for before,after,count in changes:
        assert text.count(before)==count,(before,text.count(before));text=text.replace(before,after)
    module=types.ModuleType('replica_public_first_preparation');module.__file__=str(path);module.itertools=itertools;module.revisions=revisions
    with s.aliases({'study':s},s.ROOT):exec(compile(text,str(path),'exec'),module.__dict__)
    return module


if __name__=='__main__':implementation().main()
