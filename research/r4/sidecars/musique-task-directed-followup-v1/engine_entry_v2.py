"""Select the telemetry subclass at Prime's actual worker-registry boundary."""
import importlib

EXPECTED = 'prime_rl.inference.vllm.worker.filesystem.FileSystemWeightUpdateWorker'
TARGET = 'report_worker.ReportWorker'


def install_registry():
    server = importlib.import_module('prime_rl.inference.vllm.server')
    if server.WORKER_EXTENSION_CLS.get('filesystem') != EXPECTED:
        raise ValueError('actual Prime filesystem registry changed')
    server.WORKER_EXTENSION_CLS['filesystem'] = TARGET


def main():
    # Retain default env processing and setup BEFORE importing vLLM, exactly as
    # the original CLI. The registry edit is local to this owned API process.
    setup = importlib.import_module('prime_rl.inference.server')
    original = setup.setup_vllm_env
    def configured(config):
        original(config)
        install_registry()
    setup.setup_vllm_env = configured
    from prime_rl.entrypoints.inference import main as original_main
    return original_main()


if __name__ == '__main__': main()
