"""Freeze the complete CPU-prepared package and transitive qualified closure."""
from datetime import datetime, timezone
from pathlib import Path
import rep_study as s


def main():
    root = s.ROOT
    source_names = ["rep_study.py", "rep_prepare.py", "rep_binding.py", "rep_collect.py",
                    "rep_train.py", "rep_readout_study.py", "rep_readout.py", "rep_owner.py",
                    "test_replication.py", "DESIGN.md", "PLAN.md", "seal.py"]
    sources = {str(root / name): s.sha(root / name) for name in source_names}
    inputs = {str(path): s.sha(path) for path in sorted((root / "inputs").glob("*.json"))}
    for ready_path in (s.ORIGINAL / "READY.json", s.METADATA / "READY.json"):
        ready = s.read(ready_path); inputs[str(ready_path)] = s.sha(ready_path)
        inputs.update(ready["source_sha256"]); inputs.update(ready["input_sha256"])
    start = s.starting_policy()
    for name, pin in (("adapter_model.safetensors", start["adapter_sha256"]),
                      ("adapter_config.json", start["config_sha256"]),
                      ("state.json", start["state_sha256"])):
        path = Path(start["checkpoint"]) / name
        if s.sha(path) != pin: raise ValueError("fixed24 changed " + name)
        inputs[str(path)] = pin
    value = {"created_utc": datetime.now(timezone.utc).isoformat(), "status": "READY_CPU_ONLY",
             "namespace": s.NAMESPACE, "attempt": str(s.ATTEMPT), "source_sha256": sources,
             "input_sha256": inputs, "planned_capture": 72, "planned_readout": 72,
             "selected_groups": 128, "updates": 6, "outer_seconds": 4500,
             "no_gpu_launched": True, "author_owns_no_gpu_or_queue": True}
    value["identity"] = s.digest(value); s.write(root / "READY.json", value)
    print(value["identity"], len(sources), len(inputs))


if __name__ == "__main__": main()
