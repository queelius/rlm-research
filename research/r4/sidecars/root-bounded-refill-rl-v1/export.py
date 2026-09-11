"""Exact consumed-prefix union; unchanged per-episode native admission and rewards."""
from collections import Counter
from pathlib import Path
import native as n
import study as s
import windows

impl=s.private('export.py',{'study':s,'native':n})
export_attempt=impl.export_attempt;outcome=impl.outcome;rebuild=impl.rebuild

def validate_consumed(generation,manifests,rows,groups):
    if len(groups)!=4 or any(len(g)!=8 for g in groups):raise ValueError('not frozen four-by-eight window')
    if generation['coordinate_plan_sha256']!=s.digest(sum(groups,[])):raise ValueError('window hash changed')
    flags=[]
    for index,m in enumerate(manifests):
        if (index>=4 or m['generation']!=generation or m['planned']!=8 or m['recorded']!=8
            or not m['complete'] or m['integrity_failures']
            or m['coordinate_plan_sha256']!=s.digest(groups[index])):
            raise ValueError('incomplete, reordered, foreign-policy or integrity-failed group')
        flags.append(m['training_group_episodes']>0)
    windows.validate_prefix(flags)
    expected={r['id']:r for group in groups[:len(manifests)] for r in group}
    if len(rows)!=len(expected) or len({r['episode_id'] for r in rows})!=len(rows):raise ValueError('missing or duplicate consumed coordinates')
    for row in rows:
        if (row['coordinate']!=expected.get(row['episode_id']) or row['split']!='training'
            or row.get('qualification_only') is not False or row.get('generation_id')!=generation['generation_id']):
            raise ValueError('nontraining, qualification or stale likelihood')
    return flags

def union_rebuild(sources,generation,authenticate=True):
    rows=[];manifests=[];closure=[]
    for source in sources:
        path=Path(source['path']);s.check(path/'MANIFEST.json',source['manifest_sha256'])
        if authenticate:impl.authenticate_export(path)
        m=s.read(path/'MANIFEST.json')
        for name,want in m['artifact_sha256'].items():s.check(path/name,want)
        rows.extend(s.read(path/'EPISODES.json'));manifests.append(m)
        closure.append({'path':str(path.resolve()),'manifest_sha256':s.sha(path/'MANIFEST.json')})
    groups=s.read(s.ROOT/'inputs/PLANS.json')['windows'][str(generation['candidate_window'])]
    flags=validate_consumed(generation,manifests,rows,groups)
    binding=manifests[0]['role_binding']
    if any(m['role_binding']!=binding for m in manifests):raise ValueError('window changed root/child service binding')
    provenance={'schema':'refill-window-union-v1','source_exports':closure,'generation':generation,
                'candidate_window':generation['candidate_window'],'full_candidate_plan_sha256':s.digest(sum(groups,[])),
                'coordinate_plan_sha256':s.digest(sum(groups[:len(sources)],[])),
                'role_binding':binding,'mixed_group_flags':flags,'consumed_groups':len(sources)}
    dataset_id=s.digest(provenance);group=impl.mixed_group(rows,generation,binding,dataset_id)
    if bool(group)!=any(flags):raise ValueError('union mixed selection differs from group support')
    manifest={**provenance,'dataset_id':dataset_id,'planned':len(rows),'recorded':len(rows),'complete':True,
              'integrity_failures':[],'decision':windows.validate_prefix(flags),
              'training_group_episodes':len(group['episodes']) if group else 0,
              'admitted_outcomes':sum(r['reward'] is not None for r in rows),
              'strict_successes':sum(r['reward']==1 for r in rows),
              'exclusion_reasons':dict(Counter(str(r['invalid_reason']) for r in rows if r.get('invalid_reason'))),
              'root_action_tokens':sum(r.get('action_tokens',0) for r in rows),
              'child_evidence_action_tokens':sum(r.get('child_action_tokens',0) for r in rows)}
    return rows,group,manifest

def export_union(paths,generation,output):
    sources=[{'path':str(Path(p).resolve()),'manifest_sha256':s.sha(Path(p)/'MANIFEST.json')} for p in paths]
    rows,group,manifest=union_rebuild(sources,generation)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    s.write(output/'EPISODES.json',rows)
    if group:s.write(output/'GROUP.json',group)
    manifest['artifact_sha256']={p.name:s.sha(p) for p in output.iterdir()}
    s.write(output/'MANIFEST.json',manifest)
    return manifest

def authenticate_export(output):
    output=Path(output);m=s.read(output/'MANIFEST.json')
    if m.get('schema')!='refill-window-union-v1':return impl.authenticate_export(output)
    for name,want in m['artifact_sha256'].items():s.check(output/name,want)
    rows,group,rebuilt=union_rebuild(m['source_exports'],m['generation'])
    if (rows!=s.read(output/'EPISODES.json') or rebuilt!={k:v for k,v in m.items() if k!='artifact_sha256'}
        or (group is None)!=(not (output/'GROUP.json').exists()) or group is not None and group!=s.read(output/'GROUP.json')):
        raise ValueError('union differs from authenticated raw consumed prefix')
    return {'manifest_sha256':s.sha(output/'MANIFEST.json'),'group_sha256':s.sha(output/'GROUP.json') if group else None,
            'replayed':len(rows),'selected':len(group['episodes']) if group else 0,'consumed_groups':m['consumed_groups']}
