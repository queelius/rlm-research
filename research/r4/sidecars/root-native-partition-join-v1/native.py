"""Native ACP/IPython task and process-local tool inventory; no installed source edits."""
import contextlib
import contextvars
import hashlib
import json
import os
import time
import uuid
from pathlib import Path
import protocol as p
import study as s

HEADER = 'x-native-join-coordinate'


def patched_engine():
    role = s.role()
    source = role.patch_engine(role.NANO_SOURCE.read_text())
    changes = {
        '            self._active_tools = get_active_builtin_tools(self.exec_timeout)\n':
            '            self._join_python = os.environ.get("JOIN_TOOL_PRESENT") == "1"\n'
            '            self._active_tools = get_active_builtin_tools(self.exec_timeout) if self._join_python else []\n',
        '            system_prompt = self._load_system_prompt(self._active_tools)\n':
            '            system_prompt = ' + repr(p.SYSTEM) + '\n',
        '            self.session.log_assistant(turn, tool_calls_log, msg.content)\n':
            '            self.session.log_assistant(turn, tool_calls_log, msg.content)\n'
            '            if msg.tool_calls and not self._join_python:\n'
            '                self.session.write_meta(join_disabled_tool_attempt={"request_id": call_id, "turn": turn})\n'
            '                raise RuntimeError("JOIN_DISABLED_TOOL_ATTEMPT: observed policy action; execution prohibited")\n',
    }
    for before, after in changes.items():
        if source.count(before) != 1: raise ValueError('native engine seam changed: ' + before)
        source = source.replace(before, after)
    compile(source, '<owned-native-join-engine>', 'exec')
    return source


def bootstrap():
    # Loaded only by the native ACP process via its process-local PYTHONPATH.
    # Executable package files remain unchanged. A failure must not fall through.
    return ('import hashlib,os,sys\n'
            'try:\n'
            ' import rlm.engine as engine\n'
            ' from pathlib import Path\n'
            f' expected={s.role().NANO_SHA!r}\n'
            ' if hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest()!=expected:\n'
            '  raise RuntimeError("join native engine source identity changed")\n'
            f' source={patched_engine()!r}\n'
            ' exec(compile(source,engine.__file__+":private-join", "exec"),engine.__dict__)\n'
            'except BaseException as error:\n'
            ' print("JOIN_BOOTSTRAP_FAILED:"+type(error).__name__+":"+str(error),file=sys.stderr,flush=True)\n'
            ' os._exit(70)\n')


def task(world, package, row):
    from verifiers.v1.task import Task, TaskData
    from verifiers.v1.state import State
    class JoinTask(Task[TaskData, State]):
        NEEDS_CONTAINER = True
        def runtime_env(self): return {'JOIN_TOOL_PRESENT': '1' if row['python'] else '0'}
        async def setup(self, trace, runtime):
            files = {**package['files'], 'query.txt': p.query(world), 'context.txt': package['text'],
                     'sitecustomize.py': bootstrap()}
            checks = {}
            for name, text in files.items():
                await runtime.write(name, text.encode())
                actual = await runtime.read(name, max_bytes=2 * 1024 * 1024)
                if actual != text.encode(): raise ValueError('native setup byte mismatch: ' + name)
                checks[name] = hashlib.sha256(actual).hexdigest()
            trace.info['join_setup'] = dict(file_sha256=checks, runtime=runtime.name,
                                           actual_python_inventory=row['python'], fresh_runtime=True)
    return JoinTask(TaskData(name=row['id'], prompt=p.prompt(world, package), workdir='/app'))


def environment_config():
    return dict(agent=dict(harness=dict(id='rlm', max_depth=1, version='4ef3438'),
                    retries=dict(max_retries=0), runtime=dict(image=s.IMAGE, type='docker', workdir='/app'),
                    timeout=dict(setup=45., rollout=120., finalize=15., scoring=15.)),
                interception=dict(type='server'), retries=dict(max_retries=0),
                taskset=dict(id='join-taskset'),
                timeout=dict(episode=150., finalize=15.))


def context(endpoint, row):
    from renderers import Qwen3RendererConfig
    from verifiers.v1.clients import ModelContext
    from verifiers.v1.configs.client import TrainClientConfig
    from verifiers.v1.types import SamplingConfig
    return ModelContext(model=s.MODEL['alias'], client=TrainClientConfig(
        base_url=f'http://{endpoint["host"]}:{endpoint["port"]}/v1', api_key_var=endpoint['api_key_env'],
        renderer=Qwen3RendererConfig(enable_thinking=True), renderer_model_name=s.MODEL['path'],
        multiplex=256, headers={HEADER: row['id']}), sampling=SamplingConfig.model_validate(dict(
            temperature=.6, top_p=.95, seed=row['seed'], max_tokens=2560,
            extra_body=dict(top_k=-1, min_p=0., return_token_ids=True, cache_salt=s.ROOT.name))))


def acquisition_request(world, row):
    return dict(model=s.MODEL['alias'], messages=p.extraction_messages(world, row['records']),
                temperature=.6, top_p=.95, top_k=-1, min_p=0., seed=row['seed'], max_tokens=768,
                repetition_penalty=1., presence_penalty=0., frequency_penalty=0.,
                return_token_ids=True, cache_salt=s.ROOT.name,
                chat_template_kwargs={'enable_thinking': False})


@contextlib.contextmanager
def installed(output, plan, *, configure_runtime=True):
    from verifiers.v1.clients.train import TrainClient
    from verifiers.v1.harnesses.rlm.harness import RLMHarness
    rows = {row['id']: row for row in plan}
    original_get, original_prepare = TrainClient.get_response, RLMHarness.prepare_acp
    active = contextvars.ContextVar('join_native_call', default=None)
    clients = []
    old_path, old_cache = os.environ.get('PATH'), os.environ.get('VERIFIERS_CACHE_DIR')
    if configure_runtime:
        # The accepted an27 wrapper owns the isolated image/store and runtime processes.
        owner = s.read(s.RUNTIME / 'OWNER.json')
        os.environ['PATH'] = str(s.RUNTIME / 'bin') + os.pathsep + (old_path or '')
        os.environ['VERIFIERS_CACHE_DIR'] = str(Path(owner['store']) / ('join-cache-' + s.digest(str(output))[:20]))
    async def prepare(self, ctx, trace, runtime, endpoint, secret, mcp_urls, data):
        value = await original_prepare(self, ctx, trace, runtime, endpoint, secret, mcp_urls, data)
        coordinate = rows[data.name]
        # Scope PYTHONPATH to the RLM child command, not the ACP bridge's UV interpreter.
        # Inheritance into any RLM-owned descendants is checked by the native fixture.
        value.command = ['env', 'PYTHONPATH=/app',
                         'JOIN_TOOL_PRESENT=' + ('1' if coordinate['python'] else '0'), *value.command]
        return value
    async def request_hook(request):
        record = active.get()
        if record is None or request.url.path != '/inference/v1/generate': return
        if 'native_wire_request' in record: raise ValueError('unexpected physical request retry')
        body = json.loads(request.content)
        expected = dict(temperature=.6, top_p=.95, top_k=-1, min_p=0., max_tokens=2560)
        if body['model'] != s.MODEL['alias'] or any(body['sampling_params'].get(k) != v for k, v in expected.items()):
            raise ValueError('native alias/sampling mismatch')
        record['native_wire_request'] = dict(url=str(request.url), body=body)
        s.write(output / 'physical-requests' / (record['request_id'] + '.json'), record)
    async def response_hook(response):
        record = active.get()
        if record is None or response.request.url.path != '/inference/v1/generate': return
        await response.aread()
        record['native_wire_response'] = dict(http_status=response.status_code, body=response.text)
    async def get(self, dialect, body, sampling, session_id=None, turn=None, headers=None):
        row = rows[self.config.headers[HEADER]]
        incoming = {k.lower(): v for k, v in (headers or {}).items()}
        role = s.role().route(body, incoming, s.MODEL['alias'], dict(root=s.MODEL['alias'], children=[s.MODEL['alias']]))
        expected_tools = row['python']
        if bool(body.get('tools')) != expected_tools: raise ValueError('actual native tool inventory mismatch')
        record = dict(coordinate=row, session_id=session_id, started_epoch=time.time(), status='requested',
                      **role, native_request=json.loads(json.dumps(body)), model_manifest_sha256=s.MODEL['manifest_sha256'],
                      adapter=None, expected_python=expected_tools,
                      native_tools_ordered_json=p.serialize(body.get('tools') or []))
        token = active.set(record); client = self.client._client
        if client not in clients:
            client.event_hooks['request'].append(request_hook); client.event_hooks['response'].append(response_hook); clients.append(client)
        s.write(output / 'role-audit' / (record['request_id'] + '-request.json'), record)
        try:
            response = await original_get(self, dialect, body, sampling, session_id=session_id, turn=turn, headers=headers)
            record.update(native_response=response.model_dump(mode='json'), status='returned')
            if response.model != s.MODEL['alias'] or not record.get('native_wire_response'):
                raise ValueError('missing native model/wire evidence')
            return response
        except BaseException as error:
            record.update(status='error', error_type=type(error).__name__, error=str(error)); raise
        finally:
            record['ended_epoch'] = time.time()
            s.write(output / 'role-audit' / (record['request_id'] + '-result.json'), record)
            active.reset(token)
    RLMHarness.prepare_acp, TrainClient.get_response = prepare, get
    try: yield
    finally:
        RLMHarness.prepare_acp, TrainClient.get_response = original_prepare, original_get
        for client in clients:
            client.event_hooks['request'].remove(request_hook); client.event_hooks['response'].remove(response_hook)
        for name, value in (('PATH', old_path), ('VERIFIERS_CACHE_DIR', old_cache)):
            if value is None: os.environ.pop(name, None)
            else: os.environ[name] = value
