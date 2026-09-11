"""Freeze inputs, run focused CPU qualification, and seal without launching science."""
import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import time
import native as n
import protocol as p
import study as s


def inputs():
    worlds = p.worlds(); plan = p.plan(worlds); acq = p.acquisition_plan(worlds)
    proof = s.read(s.ROOT / 'qualification-005/RESULT.json')
    if not proof['passed'] or proof['native_calls'] != 5: raise ValueError('actual native qualification required')
    audits = [s.read(path) for path in (s.ROOT / 'qualification-005/role-audit').glob('*-result.json')]
    tools = {r['native_tools_ordered_json'] for r in audits if r['coordinate']['python']}
    if len(tools) != 1: raise ValueError('actual native inventory must be unique')
    values = {'WORLDS.json': worlds, 'PLAN.json': plan, 'ACQUISITION_PLAN.json': acq,
        'HOST_GOLD.json': {w['id']: p.oracle(w['records'], w['query_products']) for w in worlds},
        'NATIVE_TOOLS.json': dict(ordered_json=next(iter(tools)), actual_cpu_source=str(s.ROOT / 'qualification-005')),
        'ACQUISITION_REQUESTS.json': {r['id']: n.acquisition_request(next(w for w in worlds if w['id'] == r['world_id']), r) for r in acq}}
    for name, value in values.items(): s.write(s.ROOT / name, value)
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from collect import first_prefix
    renderer = create_renderer(load_tokenizer(s.MODEL['path']), Qwen3RendererConfig(enable_thinking=True))
    tokenizer = s.tokenizer(); checks = []
    # Trusted source serialization is CPU rendering qualification only, never a substitute for live reports.
    fixtures = [dict(coordinate=r, content=p.serialize(r['records']), extraction=p.extraction(p.serialize(r['records']), r['records'])) for r in acq]
    for row in plan:
        world = next(w for w in worlds if w['id'] == row['world_id'])
        package = p.evidence(world, row['representation'], fixtures)
        prefix = first_prefix(world, package, row, json.loads(next(iter(tools))), renderer)
        checks.append(dict(id=row['id'], prefix_tokens=len(prefix['token_ids']), output_allowance=2560,
                           first_prefix_sha256=p.digest(prefix['token_ids']), cpu_report_fixture_not_science=True))
    extraction_checks = []
    for row in acq:
        body = values['ACQUISITION_REQUESTS.json'][row['id']]
        ids = tokenizer.apply_chat_template(body['messages'], tokenize=True, add_generation_prompt=True, enable_thinking=False, return_dict=False)
        if len(ids) + 768 > 8192: raise ValueError('extraction context overflow')
        extraction_checks.append(dict(id=row['id'], native_prompt_token_ids=ids, prompt_tokens=len(ids), output_allowance=768))
    s.write(s.ROOT / 'NATIVE_PREPARATION.json', dict(root_checks=checks, extraction_checks=extraction_checks,
        actual_reports_rendered_and_pinned_after_immutable_acquisition=True, root_initial_context_max=max(r['prefix_tokens']+2560 for r in checks)))
    s.write(s.ROOT / 'SEED_AUDIT.json', dict(master=p.MASTER, world_seeds=[w['generator_seed'] for w in worlds],
        root_seeds=sorted({r['seed'] for r in plan}), acquisition_seeds=[r['seed'] for r in acq],
        prior_namespace_search='Before source creation, rg981391 over prior PLAN/SPEC/READY/SEED/protocol/study found no matches',
        balanced_order='eight six-condition blocks; cyclic six-cell order with final two reversals; world/repeat block order shuffled before outcomes',
        prior_generator_family_exposed=True, fresh_world_clusters=4, root_endpoints=48))
    print(dict(inputs_ready=True, planned=48, acquisitions=24))


def qualify():
    command = [str(s.NATIVE), '-m', 'unittest', '-v', 'test_protocol', 'test_native', 'test_owner', 'test_collect']
    result = subprocess.run(command, cwd=s.ROOT, capture_output=True, text=True, timeout=90,
        env={**os.environ, 'CUDA_VISIBLE_DEVICES': '', 'PYTHONDONTWRITEBYTECODE': '1', 'OMP_NUM_THREADS': '2'})
    for path in s.ROOT.glob('*.py'): ast.parse(path.read_text(), filename=str(path))
    data = dict(command=command, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr,
                passed=result.returncode == 0, gpu_calls=0, model_service_calls=0,
                source_sha256={str(path): s.sha(path) for path in s.ROOT.glob('*.py')})
    s.write(s.ROOT / 'CPU_TESTS_FINAL_V2.json', data)
    if result.returncode: raise ValueError('focused CPU tests failed; artifact retained')
    print(dict(passed=True, sha256=s.sha(s.ROOT / 'CPU_TESTS_FINAL_V2.json')))


def seal():
    tests = s.read(s.ROOT / 'CPU_TESTS_FINAL_V2.json')
    if not tests['passed'] or any(s.sha(path) != pin for path, pin in tests['source_sha256'].items()):
        raise ValueError('fresh matching focused tests required')
    proof = s.read(s.ROOT / 'qualification-007/RESULT.json')
    if not proof['passed'] or any(s.sha(path) != pin for path, pin in proof['qualified_source_sha256'].items()):
        raise ValueError('fresh actual native full-branch qualification required')
    import owner
    suite = owner.suite()
    if suite.SERVE != s.ROOT / 'service_wrapper.py': raise ValueError('owner actual service wrapper differs')
    source = dict(s.read(s.SIDE / 'root-partition-final-interface-v1/READY_V2.json')['source_sha256'])
    source.update(s.read(s.RUNTIME / 'CPU_READY.json')['source_and_artifact_sha256'])
    source.update(s.read(s.RUNTIME / 'LIFECYCLE_READY_V2.json')['source_sha256'])
    source[str(s.role().NANO_SOURCE)] = s.role().NANO_SHA
    paths = [path for path in s.ROOT.rglob('*') if path.is_file() and '__pycache__' not in path.parts and 'outputs' not in path.parts]
    paths += [s.SIDE / 'root-example-map-visibility-v1/metrics.py', s.RUNTIME / 'OWNER.json',
              s.RUNTIME / 'credential_preflight.py', s.FREE / 'service_wrapper_v3.py',
              s.SIDE / 'leaf-post-sft-suite-v1/suite.py', s.SIDE / 'leaf-role-routing-v1/source/routing.py']
    source.update({str(path): s.sha(path) for path in paths})
    for path, pin in source.items():
        if s.sha(path) != pin: raise ValueError('source changed before seal: ' + path)
    native_sources = Path('/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1')
    for path in [native_sources / name for name in ('task.py', 'taskset.py', 'env.py', 'clients/train.py', 'harnesses/rlm/harness.py', 'acp/__init__.py')]:
        source[str(path)] = s.sha(path)
    ready = dict(status='CPU_READY_FOR_MAIN_ACCEPTANCE', source_sha256=source, planned_root_endpoints=48,
        planned_acquisitions=24, world_clusters=4, model=s.MODEL, adapter=None, seed_master=p.MASTER,
        work_seconds=1650, owned_seconds=1770, outer_seconds=1800, workers=4, episode_seconds=120,
        acquisition_seconds=210, startup_seconds=180, cleanup_seconds=120,
        argv=[str(s.NATIVE), str(s.ROOT / 'owner.py'), 'run', '--output', str(s.ATTEMPT)],
        actual_service_wrapper=str(suite.SERVE), native_fixture=str(s.ROOT / 'qualification-007/RESULT.json'),
        source_gate='all three extractions exact or report coordinate NULL; direct independent',
        private_in_memory_tool_override=True, no_algorithm_in_prompt=True,
        gpu_calls=0, model_service_calls=0, real_science_outputs_pending=True, prepared_epoch=time.time())
    ready['identity'] = s.digest(ready); s.write(s.READY_PATH, ready)
    s.verify(); print(dict(ready_sha256=s.sha(s.READY_PATH), identity=ready['identity'], source_files=len(source)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=('inputs', 'qualify', 'seal'))
    globals()[parser.parse_args().command]()
