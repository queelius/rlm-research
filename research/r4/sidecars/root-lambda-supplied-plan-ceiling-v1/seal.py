"""Seal the CPU-qualified supplied-plan ceiling."""
import time

import study as s


def main():
    sources = [s.ROOT / name for name in (
        "DESIGN.md", "PLAN.md", "IMPLEMENTATION_REPORT.md", "study.py", "protocol.py", "prepare.py", "collect.py",
        "owner.py", "test_protocol.py", "test_inputs.py", "test_runtime.py", "seal.py")]
    sources += [s.PRIOR / "READY.json", s.PRIOR / "study.py",
                s.SIDE / "leaf-adapter-by-granularity-v1/bg_collect.py",
                s.QUERY / "READY.json",
                s.SIDE / "runtime-an27-5780-v1/service_wrapper_v2.py"]
    binding = s.binding(); child = binding["models"][binding["fixed_child"]]
    child_path = __import__("pathlib").Path(child["path"])
    sources += [child_path / "adapter_config.json", child_path / "adapter_model.safetensors"]
    inputs = sorted((s.ROOT / "inputs").glob("*.json")) + [s.ROOT / "CPU_INPUT_NATIVE.json"]
    ready = {
        "schema": "root-lambda-supplied-plan-ceiling-ready-v1",
        "created_epoch": time.time(), "question": "Does supplied exact acquisition and J1 reduction suffice with fixed c32 at scale?",
        "planned_episodes": 8, "planned_child_calls": 40, "root_model_calls": 0,
        "sizes": [64, 256], "clusters": 4, "batch_size": 32, "workers": 4,
        "request_seconds": 90, "max_output_tokens": 2048, "context_tokens": 8192,
        "outer_seconds": 1800, "work_seconds": 1650, "owned_seconds": 1770,
        "no_retry": True, "no_repair": True, "adapter": child,
        "source_sha256": {str(path): s.sha(path) for path in sources},
        "input_sha256": {str(path): s.sha(path) for path in inputs},
        "no_gpu_launch": True,
    }
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__": main()
