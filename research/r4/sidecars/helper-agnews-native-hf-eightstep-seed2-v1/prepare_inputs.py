"""CPU-only seed replacement; every other source request field remains identical."""
import copy
import os
import core
import reuse


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (core.ROOT/"inputs").exists():
        raise ValueError("fresh CPU-only preparation required")
    prior = core.read(reuse.PRIOR/"READY_V2.json")
    for path, expected in prior["closure_sha256"].items():
        if core.sha(path) != expected:
            raise ValueError("sealed predecessor closure differs: " + path)
    inventories = []
    for step in range(1, 9):
        source = core.DATA/f"inputs/step-{step:03d}/REQUESTS.json"
        rows = copy.deepcopy(core.read(source))
        for index,row in enumerate(rows):
            seed = 20260912900000 + (step-1)*128 + index
            row["seed"] = row["body"]["sampling_params"]["seed"] = seed
        destination = core.ROOT/f"inputs/step-{step:03d}/REQUESTS.json"
        core.write_x(destination, rows)
        core.write_x(core.ROOT/f"inputs/step-{step:03d}/HOST_GOLD.json",
                     core.read(reuse.PRIOR/f"inputs/step-{step:03d}/HOST_GOLD.json"))
        inventories.append(dict(step=step, source=str(source), source_sha256=core.sha(source),
            replica=str(destination), replica_sha256=core.sha(destination),
            native_seed_min=rows[0]["seed"], native_seed_max=rows[-1]["seed"]))
    audit = core.read(reuse.PRIOR/"inputs/BUILD_AUDIT.json")
    audit.update(seed_namespace="agnews-broader8-seed2-20260912", hf_seed=20260912910000,
                 prior_seed1_heldout_results_known=True, only_request_seed_fields_changed=True,
                 schedules=inventories)
    core.write_x(core.ROOT/"inputs/BUILD_AUDIT.json", audit)
    core.write_x(core.ROOT/"RUNTIME.json", core.read(reuse.PRIOR/"RUNTIME.json"))


if __name__ == "__main__":
    main()
