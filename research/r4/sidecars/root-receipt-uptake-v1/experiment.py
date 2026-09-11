"""Four-arm uptake sentinel, privately reusing immutable receipt/native components."""
import ast
import copy
import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'root-receipt-ablation-v1'
DECISION=ROOT.parents[1]/'operations/2026-09-09-continuous-allocation/RECEIPT_UPTAKE_IMPLEMENTATION_DECISION.md'
DESIGN=ROOT.parents[1]/'ideas/2026-09-09-receipt-uptake-followup.md'
ARMS=('unchanged','taught_raw','restored_raw','restored_receipt')
PHASES=('originalA','step8','originalB')
PHASE_WEIGHTS={'originalA':'original','step8':'step8','originalB':'original'}
PHASE_CAPS={'originalA':600,'step8':1200,'originalB':600}
SEED_MASTER=981274300
ORDERS=((0,2,3,1),(2,1,0,3),(1,3,2,0),(3,0,1,2))


def checked_import(name,path,expected):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected:
        raise ValueError('pinned source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


receipt=checked_import('uptake_frozen_receipt',PRIOR/'experiment.py','1803aa59cfaf94edf7ac5db865cce4c721eb2302b31ab186c5b88b0fc4488690')
c,native,old,capture=receipt.c,receipt.native,receipt.old,receipt.capture
sys.path.insert(0,str(ROOT))
COLLECTOR, COLLECTOR_SHA=receipt.COLLECTOR,receipt.COLLECTOR_SHA
make_tasks,catalog_for=receipt.make_tasks,receipt.catalog_for


def procedure(task):
    prompt=old.with_prompt(task,'unchanged').data.prompt
    return next(p for p in prompt.split('\n\n') if p.startswith('Suggested procedure:'))


def example_code(prompt):
    if prompt.count('```python\n')!=1:
        raise ValueError('exactly one executable example expected')
    return prompt.split('```python\n',1)[1].split('```',1)[0]


def teaching(task,arm):
    original=old.with_prompt(task,'unchanged').data.prompt
    original_code=example_code(original)
    tree=ast.parse(original_code)
    definition=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='definitions' for t in n.targets))
    target=c.read(c.ROOT/'inputs/TRANSFER_PUBLIC.json')['tasks']
    target=next(r['label'] for r in target if r['name']==task.data.name)
    text=("Source-bound recursive API: source_records() returns the public records in context.txt with these fields only: id (source identifier), text (the original Date/User/Instance line), group_id and text_sha256 (provenance identifiers). The catalog does not contain answer_category, category, label, or any gold answer. Classification must be inferred from each question; do not try to read labels from catalog fields.\n\n"
        "The following example shows a source-ID-preserving recursive classification step. rlm_records(ids, query, allowed_values) calls the child on the selected public records. child.answer is the child's raw text; the requested format is a JSON object mapping each selected source ID to its inferred label. JSON structure does not establish semantic correctness. Ordinary rlm(prompt) remains available. You may choose any relevant subset, query, batching, recovery and computation; this example does not require a particular final strategy.\n\n"
        "Executable API example for the first four context records (a starting batch, not the final answer). You can run this in ipython:\n")
    text += ('This arm also exposes child.receipt(), an optional structural validation report.' if arm=='restored_receipt' else 'This arm exposes child.answer and native metadata; child.receipt() is not available.')+'\n'
    code=('import json\nfrom receipt_api import source_records, rlm_records\nrecords = source_records()\n'
        'ids = [record["id"] for record in records[:4]]\n'
        'allowed_labels = ["human being", "location", "abbreviation", "entity",\n'
        '                  "description and abstract concept", "numeric value"]\n'
        'definitions = '+json.dumps(definition)+'\n'
        'child = await rlm_records(ids, definitions, allowed_labels)\nprint(child.answer)\n')
    if arm=='restored_receipt':
        code+='receipt = child.receipt()\nprint(receipt)\nlabels_by_id = receipt["labels_by_id"]\n'
    else:
        code+='labels_by_id = json.loads(child.answer)\n'
    code+=('if isinstance(labels_by_id, dict):\n    target_label = '+json.dumps(target)+'\n'
        '    print({"example_batch_ids": ids,\n'
        '           "example_batch_count": sum(label == target_label\n'
        '                                      for label in labels_by_id.values())})\n')
    text+='```python\n'+code+'```\n\n'
    text+=("The printed count covers only the example batch, not the full context. Continue covering the remaining relevant records, retaining source IDs with inferred labels, then compute the requested aggregate. You may inspect and correct the child classifications, handle invalid outputs, change decomposition, or use ordinary rlm(prompt). A receipt's labels_by_id is null when its strict requested-ID/label map checks fail; validity never means the labels are semantically correct. Raw child.answer is always available. You decide whether and how to use these interfaces. Return only the requested final answer format when finished.")
    return text


def with_prompt(task,arm):
    if arm not in ARMS:
        raise ValueError('unknown uptake arm')
    baseline=old.with_prompt(task,'unchanged')
    if arm=='unchanged':
        return baseline
    prefix=baseline.data.prompt.split('Suggested procedure:')[0].rstrip()
    question='Question: '+baseline.data.prompt.split('\n\nQuestion: ',1)[1]
    blocks=[prefix]
    if arm!='taught_raw': blocks.append(procedure(task))
    blocks.extend([teaching(task,arm),question])
    result=receipt.ReceiptTask(baseline.data.model_copy(update={'prompt':'\n\n'.join(blocks)}),task.config)
    result.receipt_arm='receipt' if arm=='restored_receipt' else 'indexed_raw'
    return result


def build_plan(tasks):
    originals={r['task_name']:r for r in native.planned_rows('transfer-original') if r['repeat']==0}
    plan=[]
    for phase_index,phase in enumerate(PHASES):
        weight=PHASE_WEIGHTS[phase]
        for index,name in enumerate(sorted(tasks)):
            context_index=index//2
            cohort_a=index%2==context_index%2
            if phase=='originalA' and not cohort_a or phase=='originalB' and cohort_a:
                continue
            prior=originals[name]
            identity={'study':ROOT.name,'task_name':name,'source_id':prior['source_id'],
                'context_window_id':prior['context_window_id'],'context_sha256':prior['context_sha256'],
                'analysis_split':'exposed_root_transfer_leaf_train_supported','split':'transfer','repeat':0,
                'seed':SEED_MASTER+1+index,'temperature':.5,'client_path':'train'}
            identity['matched_id']=c.digest(identity)
            order=ORDERS[(index+(2 if weight=='step8' else 0))%4]
            for position,arm_index in enumerate(order):
                arm=ARMS[arm_index]
                row={**identity,'weight':weight,'phase':phase,'phase_index':phase_index,
                    'pair_id':c.digest([identity['matched_id'],weight]),'pair_order':position,
                    'arm':arm,'group_id':c.digest([ROOT.name,name,weight,arm]),
                    'task_hash':with_prompt(tasks[name],arm).hash,'dispatch_order':len(plan)}
                row['id']=c.digest(row)
                plan.append(row)
    return plan


def binding_for(policy):
    frozen=c.read(old.ROOT/'SPEC.json')
    weight=next((w for w,p in frozen['policies'].items() if p==policy),None)
    if weight is None: raise ValueError('policy not original or historical step8')
    binding=copy.deepcopy(frozen['bindings'][weight])
    for key in ('return_contract_study','return_contract_weight','design_sha256'):
        binding.pop(key,None)
    return {**binding,'receipt_uptake_study':ROOT.name,'decision_sha256':c.file_hash(DECISION)}


def validate_descriptor(descriptor,binding,binding_path):
    native.authenticate_binding(binding)
    if binding!=binding_for(binding['campaign_policy']): raise ValueError('binding changed')
    root=binding['models'][binding['role_map']['root']]
    if (descriptor['model_alias']!=binding['role_map']['root']
        or descriptor['adapter']!={'path':root['path'],'model_sha256':root['adapter_sha256'],'config_sha256':root['config_sha256']}
        or descriptor['role_binding_sha256']!=c.file_hash(binding_path)
        or descriptor['base_model']['manifest_sha256']!=c.pilot_recipe()['base_manifest_sha256']
        or descriptor['base_model']['path']!=c.pilot_recipe()['base_model']):
        raise ValueError('descriptor source changed')
    return {**old.planned_endpoint(binding),'url':f"http://{descriptor['host']}:{descriptor['port']}/v1",'api_key_env':descriptor['api_key_env']}


def collector_source():
    if c.file_hash(COLLECTOR)!=COLLECTOR_SHA: raise ValueError('collector changed')
    source=COLLECTOR.read_text()
    for before,after in [('range(0, len(plan), 2)','range(0, len(plan), 4)'),('plan[offset : offset + 2]','plan[offset : offset + 4]')]:
        if source.count(before)!=1: raise ValueError('collector grouping seam ambiguous')
        source=source.replace(before,after)
    return source


def collector():
    module=types.ModuleType('uptake_quadruplet_collector')
    module.__dict__.update(capture.base.__dict__)
    tree=ast.parse(collector_source())
    node=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(COLLECTOR),'exec'),module.__dict__)
    return module


def verify():
    spec=c.read(ROOT/'SPEC.json')
    c.authenticate(spec['source_file_sha256'])
    if spec['plan']!=build_plan(make_tasks()) or spec['plan_sha256']!=c.digest(spec['plan']):
        raise ValueError('plan drift')
    return spec


def phase_spec(phase,binding_path,endpoint_path,destination,cap):
    spec=copy.deepcopy(verify())
    weight=PHASE_WEIGHTS[phase]
    binding,descriptor=c.read(binding_path),c.read(endpoint_path)
    if binding!=spec['bindings'][weight]: raise ValueError('wrong phase policy')
    spec.update(phase=phase,weight=weight,endpoint=validate_descriptor(descriptor,binding,binding_path),role_binding=binding,
        binding_path=str(binding_path),endpoint_descriptor_path=str(endpoint_path),source_endpoint_descriptor=descriptor,
        plan=[r for r in spec['plan'] if r['phase']==phase],wall_time_cap_seconds=min(cap,PHASE_CAPS[phase]),
        parent_spec_sha256=c.file_hash(ROOT/'SPEC.json'),
        serving_evidence=capture.recursive.serving_evidence(Path(endpoint_path).parent/'inference.log'))
    spec['plan_sha256']=c.digest(spec['plan'])
    spec['source_file_sha256'].update({str(p):c.file_hash(p) for p in (Path(binding_path),Path(endpoint_path),ROOT/'SPEC.json',ROOT/'READY.json')})
    c.write_once(destination,spec)
    return spec


def verify_phase(path):
    parent,actual=verify(),c.read(path)
    c.authenticate(actual['source_file_sha256'])
    phase=actual['phase']
    expected=[r for r in parent['plan'] if r['phase']==phase]
    if (actual['plan']!=expected or actual['plan_sha256']!=c.digest(expected)
        or actual['parent_spec_sha256']!=c.file_hash(ROOT/'SPEC.json')
        or actual['weight']!=PHASE_WEIGHTS[phase] or not 0<actual['wall_time_cap_seconds']<=PHASE_CAPS[phase]):
        raise ValueError('phase coordinates/cap changed')
    for key in ('tasks','environment','image_id','max_concurrent_pairs','bindings'):
        if actual[key]!=parent[key]: raise ValueError('phase contract changed: '+key)
    if any(actual['source_file_sha256'].get(k)!=v for k,v in parent['source_file_sha256'].items()):
        raise ValueError('phase source closure changed')
    binding,descriptor=c.read(actual['binding_path']),c.read(actual['endpoint_descriptor_path'])
    if (binding!=parent['bindings'][actual['weight']] or actual['role_binding']!=binding
        or actual['source_endpoint_descriptor']!=descriptor
        or actual['endpoint']!=validate_descriptor(descriptor,binding,actual['binding_path'])):
        raise ValueError('phase endpoint changed')
    capture.recursive.validate_serving_evidence(actual['serving_evidence'])
    return actual
