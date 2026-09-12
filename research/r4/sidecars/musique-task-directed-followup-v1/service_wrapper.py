"""Exact eager released-base launcher plus a prospective in-worker dispatch receipt."""
import argparse
from pathlib import Path

import study


def build(run_dir):
    source = study.load('report_followup_base_launch_source', study.BASE / 'service_base_batch_v2.py')
    # This binds both SERVER_START and actual pre-exec attestation to this wrapper.
    source.__file__ = str(Path(__file__).resolve())
    module = source.build_module()
    runtime = module.study.base.runtime_study().service
    old_config = runtime.config

    def config(*args, **kwargs):
        value = old_config(*args, **kwargs)
        assert value['vllm']['enforce_eager'] is True
        assert value['vllm']['enable_lora'] is False
        value['vllm']['worker_extension_cls'] = 'report_worker.ReportWorker'
        return value

    runtime.config = config
    old_environment = module.adapt_environment

    def environment(value):
        value = old_environment(value)
        value['REPORT_DISPATCH_RECEIPT'] = str(Path(run_dir) / 'ACTUAL_DISPATCH.json')
        value['PYTHONPATH'] = str(study.ROOT) + (':' + value['PYTHONPATH'] if value.get('PYTHONPATH') else '')
        return value

    module.adapt_environment = environment
    return module


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--binding', type=Path, required=True)
    args = parser.parse_args()
    build(args.run_dir).main()
