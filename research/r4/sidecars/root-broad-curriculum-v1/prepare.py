"""Freeze only the approved broader16 tasks/seed streams; no model outcomes read."""
import argparse
import copy
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import campaign_common as c

BRIEF = c.ROOT.parent.parent/'operations/2026-09-09-continuous-allocation/BROAD16_IMPLEMENTATION_BRIEF.md'
TRAIN_LABELS=['human being','numeric value','entity','location']


def prior_seeds():
    paths=[c.OLD/'inputs/PLANS.json',c.ROOT.parent/'root-rlvr-independent-seed-v1/inputs/PLANS.json',
        c.PILOT/'inputs/PLAN.json',c.ROOT.parent/'root-credit-validation-replay-v1/SPEC_ORIGINAL.json']
    found=set()
    def walk(value):
        if isinstance(value,dict):
            if type(value.get('seed')) is int: found.add(value['seed'])
            for v in value.values(): walk(v)
        elif isinstance(value,list):
            for v in value: walk(v)
    for path in paths: walk(c.read(path))
    return found


def build_inputs():
    c.authenticate({c.DATA/'MANIFEST.json':c.PINS[c.DATA/'MANIFEST.json']})
    manifest=c.read(c.DATA/'MANIFEST.json')
    c.authenticate(manifest['files_sha256']);c.authenticate(manifest['source_sha256'])
    public=c.read(c.DATA/'PUBLIC.json');host=c.read(c.DATA/'HOST_GOLD.json')
    groups=c.read(c.DATA/'GROUPS.json');schedule=c.read(c.DATA/'CANDIDATE_SCHEDULE.json')
    candidates={t['id']:t for t in public['tasks']}
    wanted=[]
    for row in schedule: wanted.extend(row['tasks'])
    validation=[];transfer=[]
    def tid(context,label): return context['id']+':'+label.replace(' ','_')
    vals=[g for g in groups if g['split']=='validation']
    for i,g in enumerate(vals): validation.append(tid(g,TRAIN_LABELS[i%4]))
    for split in ['transfer-composition','transfer-size','transfer-leaf-test-exposed']:
        for i,g in enumerate(g for g in groups if g['split']==split):
            labels=([TRAIN_LABELS[i%2],['description and abstract concept','abbreviation'][i%2]]
                if split=='transfer-composition' else [TRAIN_LABELS[i%4]]
                if split=='transfer-size' else TRAIN_LABELS[:2])
            transfer.extend(tid(g,label) for label in labels)
    wanted.extend(validation);wanted.extend(transfer)
    if len(wanted)!=len(set(wanted)) or len(wanted)!=80: raise ValueError('wrong declared task registry')
    group_index={g['id']:i for i,g in enumerate(groups)}
    groups_by_id={g['id']:g for g in groups}
    tasks=[]
    for i,name in enumerate(wanted):
        task=candidates[name];group=groups_by_id[task['context_id']]
        tasks.append({**task,'name':name,'source_id':31000000+i,'context_window_id':2100+group_index[group['id']],
            'analysis_split':group['split'],'context_sha256':group['context_sha256'],
            'split':'training' if group['split']=='training' else 'validation' if group['split']=='validation' else 'transfer'})
    by_name={t['name']:t for t in tasks}
    def coords(names,phase,repeats,seed_phase=None):
        rows=[]
        for name in names:
            t=by_name[name]
            for repeat in range(repeats):
                row={'study':c.ROOT.name,'task_name':name,'source_id':t['source_id'],
                    'context_window_id':t['context_window_id'],'context_sha256':t['context_sha256'],
                    'split':t['split'],'analysis_split':t['analysis_split'],'repeat':repeat,
                    'seed':c.sample_seed(phase if seed_phase is None else seed_phase,name,repeat),
                    'temperature':.5,'client_path':'train','arm':'sft_child','campaign_phase':phase,
                    'group_id':c.digest([c.ROOT.name,phase,name,.5]),'pair_order':0}
                row['id']=c.digest(row)
                row['pair_id']=c.digest([c.ROOT.name,'transfer' if t['split']=='transfer' else phase,name,repeat])
                rows.append(row)
        rows.sort(key=lambda r:c.digest([c.SEED,phase if seed_phase is None else seed_phase,r['task_name'],r['repeat'],'dispatch']))
        return [{**r,'dispatch_order':i} for i,r in enumerate(rows)]
    plans={'training':{str(row['candidate_update']):coords(row['tasks'],row['candidate_update'],8) for row in schedule},
        'validation':coords(validation,'validation',2),'transfer_original':coords(transfer,'transfer-original',2,'transfer'),
        'transfer_final':coords(transfer,'transfer-final',2,'transfer')}
    fresh=[r for rs in plans['training'].values() for r in rs]+plans['validation']+plans['transfer_original']
    seeds=[r['seed'] for r in fresh]
    if len(seeds)!=448 or len(set(seeds))!=448 or set(seeds)&prior_seeds(): raise ValueError('seed collision')
    included={t['context_id'] for t in tasks}
    selected_groups=[g for g in groups if g['id'] in included]
    provenance={'source_split_sha256':'3f5f648488d512d2052b9f3d57c02e030af8e939ca363998c07a556a47d7f457',
        'candidate_manifest_sha256':c.PINS[c.DATA/'MANIFEST.json'],'candidate_identity':manifest['identity'],
        'data_provenance_path':str(c.DATA/'PROVENANCE.json'),'data_provenance_sha256':c.file_hash(c.DATA/'PROVENANCE.json'),
        'groups':selected_groups,'seed':c.SEED,'unique_training_seed_coordinates':384,'validation_coordinates':16,
        'validation_steps':[0,4,8,12,16],'transfer_pairs':48,'initial_optimizer_steps':0,
        'known_prior_seed_collisions':0,'prior_seed_scope':'original and independent campaign plans, root pilot, original validation replay',
        'public_runtime_allowlist':['context text','rendered task question with qualified public TREC definitions/example'],
        'runtime_excluded':['gold answers','per-record labels','group/split membership','host provenance'],
        'query_target_transfer':'DESC/ABBR requested targets absent from root training; semantic labels and class records not novel',
        'training_zero_count_tasks':sum(host[t]['answer_integer']==0 for row in schedule for t in row['tasks']),
        'heldout_zero_count_tasks':{split:sum(host[t['name']]['answer_integer']==0 for t in tasks if t['analysis_split']==split)
                                 for split in sorted({t['analysis_split'] for t in tasks if t['split']!='training'})}}
    return {'PUBLIC.json':{'contexts':[x for x in public['contexts'] if x['id'] in included],'tasks':tasks},
        'HOST_GOLD.json':{name:host[name] for name in wanted},'PLANS.json':plans,'PROVENANCE.json':provenance}


def make_recipe():
    recipe=copy.deepcopy(c.read(c.OLD/'RECIPE.json'))
    recipe.update(schema='sixteen-generation-broad-root-only-persistent-adam-v1',training_seed=c.SEED,
        optimizer_steps=16,declared_at_utc=datetime.now(timezone.utc).isoformat(),
        primary_policy='fixed-final16; validation maximum descriptive only',
        limitations='broader documents/targets plus more updates/rollouts; not breadth-only attribution; named-root disjoint, historical leaf exposures retained',
        concurrency_amendment='approved8 workers;24 fresh rollouts per round; service limits unchanged')
    recipe['caps'].update({'global':18000,'collection':1800,'training':600,'service_ready':180,'validation':900,'transfer':3600})
    return recipe


def inputs():
    if (c.ROOT/'inputs').exists(): raise ValueError('inputs already prepared; no overwrite')
    for name,value in build_inputs().items(): c.write_once(c.ROOT/'inputs'/name,value)
    c.write_once(c.ROOT/'RECIPE.json',make_recipe())
    import campaign_native as native
    identities=native.task_identity(native.make_tasks())
    c.write_once(c.ROOT/'inputs/TASK_IDENTITIES.json',identities)
    return {'tasks':len(identities),'gpu_calls':0}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['inputs'])
    args=parser.parse_args();print(json.dumps(inputs()))
