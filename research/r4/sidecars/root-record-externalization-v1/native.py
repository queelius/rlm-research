"""Explicit pinned reuse of qualified native tool/root/child transport."""
import protocol as p
import study as s

with s.aliases({'study': s, 'protocol': p}):
    _base = s.load('record_interface_native_source', p.SOURCE / 'native.py',
                   '42abf3a447266797c1c67b590ee5f69c7af4c6ec946840c4c74944e52f191628')

HEADER = _base.HEADER
patched_engine, bootstrap, task = _base.patched_engine, _base.bootstrap, _base.task
environment_config, context, installed = _base.environment_config, _base.context, _base.installed

