"""Prospective eager CUDA dispatch receipt; no kernel/math implementation changes."""
import functools
import hashlib
import json
import os
from pathlib import Path


def install(batch, envs, receipt_path):
    original = batch.matmul_persistent
    wrote = False

    @functools.wraps(original)
    def measured(*args, **kwargs):
        nonlocal wrote
        result = original(*args, **kwargs)
        if not wrote:
            first = args[0]
            if not (first.device.type == 'cuda' and result.device.type == 'cuda'
                    and envs.VLLM_BATCH_INVARIANT and batch._batch_invariant_MODE
                    and os.environ.get('VLLM_BATCH_INVARIANT') == '1'):
                raise RuntimeError('actual first dispatch lacks batch-invariant CUDA state')
            value = {'schema': 'first-real-eager-batch-invariant-dispatch-v1', 'pid': os.getpid(),
                'environment_flag': os.environ['VLLM_BATCH_INVARIANT'], 'resolved_flag': True,
                'installed_batch_invariant_mode': True, 'device_type': first.device.type,
                'dtype': str(first.dtype), 'input_shape': list(first.shape), 'output_shape': list(result.shape),
                'function': original.__qualname__, 'kernel_source': batch.__file__,
                'kernel_source_sha256': hashlib.sha256(Path(batch.__file__).read_bytes()).hexdigest(),
                'instrumentation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'original_function_returned': True, 'tensor_values_or_credentials_persisted': False,
                'scope': 'first real dispatch including warmup; not per-call bitwise invariance proof'}
            with Path(receipt_path).open('x') as stream:
                json.dump(value, stream, sort_keys=True); stream.write('\n')
            wrote = True
        return result

    batch.matmul_persistent = measured


# vLLM resolves this module inside EngineCore before its worker initialization.
# The extension keeps the exact original filesystem methods. CPU fixtures import
# only install() with this environment key absent; no vLLM/CUDA import then occurs.
if os.environ.get('REPORT_DISPATCH_RECEIPT'):
    from prime_rl.inference.vllm.worker.filesystem import FileSystemWeightUpdateWorker
    from vllm.model_executor.layers import batch_invariant
    import vllm.envs as envs
    install(batch_invariant, envs, os.environ['REPORT_DISPATCH_RECEIPT'])

    class ReportWorker(FileSystemWeightUpdateWorker):
        pass
