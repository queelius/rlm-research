"""Materialize immutable receipts for the approved CPU-only candidate."""
import datetime
import json
from pathlib import Path

import warm_study as study


def pins(paths):
    return {str(path): study.sha(path) for path in sorted(set(map(Path, paths)))}


def source_paths():
    local = list(study.ROOT.glob("*.py")) + [study.ROOT / "PLAN.md", study.ROOT / "DESIGN.md",
                                              study.ROOT / "DIAGNOSTIC_PROTOCOL.md"]
    qualified = [study.QSR / name for name in (
        "qsr_study.py", "qsr_common.py", "qsr_native.py", "qsr_metrics.py",
        "qsr_collect.py", "qsr_export.py", "qsr_train.py", "owner.py", "RECIPE.json",
        "CAMPAIGN.json", "READY.json")]
    protocol = study.SIDE / "root-operator-diverse-sft-v1/od_protocol.py"
    evidence = [study.ROOT.parents[1] / "analyses/root-operator-composition-transfer-live-2026-09-10/REPORT.md",
                study.ROOT.parents[1] / "analyses/root-operator-dose-semantic-retrospective-2026-09-10/REPORT.md"]
    start = [study.SFT24 / name for name in ("adapter_model.safetensors", "adapter_config.json", "state.json")]
    inherited = [Path(path) for path in study.read(study.QSR / "CAMPAIGN.json")["source_sha256"]]
    return local + qualified + [protocol] + evidence + start + inherited


def scan_seeds(candidates):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    paths = []
    for side in study.SIDE.iterdir():
        if not side.is_dir() or side == study.ROOT:
            continue
        paths += list((side / "inputs").glob("*.json")) if (side / "inputs").is_dir() else []
        paths += list(side.glob("*PLAN*.json")) + list(side.glob("*RESERV*.json")) + list(side.glob("*SEED*.json"))
    found = []
    for path in sorted(set(paths)):
        try:
            value = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        collisions = __import__("warm_prepare").seed_collisions(candidates, value)
        if collisions:
            found.append({"path": str(path), "seeds": collisions, "sha256": study.sha(path)})
    return {"started_utc": started, "ended_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scope": "named sidecar inputs plus PLAN/RESERV/SEED JSON; outputs excluded",
            "files_scanned": len(set(paths)), "candidate_count": len(candidates),
            "collisions": found, "collision_count": sum(len(x["seeds"]) for x in found)}


def main():
    if any((study.ROOT / name).exists() for name in ("START.json", "RECIPE.json", "CAMPAIGN.json")):
        raise FileExistsError("candidate receipts are write-once")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = {"kind": "exact_operator_sft24", "fresh_rl_adam": True,
             "policy": study.fixed_start(),
             "selection": "fixed exact SFT24 before new RL outcomes; no SFT optimizer loaded"}
    recipe = study.read(study.QSR / "RECIPE.json")
    recipe.update({
        "schema": "root-sft24-terminal-rlvr-v1", "declared_at_utc": now,
        "outcomes_consulted_for_recipe": True,
        "outcome_scope": "sealed dose retrospective and composition audit informed this adaptive pilot; no new-campaign outcomes exist",
        "root_adapter": str(study.SFT24), "root_adapter_sha256": start["policy"]["adapter_sha256"],
        "start": "exact operator SFT24, fresh RL Adam0; no SFT optimizer state",
        "scheduled_windows": 8, "maximum_actual_updates": 8, "optimizer_steps": 8,
        "training_seed": study.SEED, "refill": "none; fixed24/window",
        "limitations": "exposed training families and composition readout; correctness need not imply requested computation; clustered small panel; equal episodes not equal tokens/FLOPs",
        "caps": {"outer": 10800, "owned": 10680, "work": 10500, "margin": 120,
                 "cleanup": 30, "training_side": 5400, "training_collection": 600,
                 "training_forward_backward": 240, "training_process": 480,
                 "training_save_release": 60, "service_ready": 180, "endpoint": 180,
                 "final_policy_block": 2550, "final_total": 5100},
    })
    study.write(study.ROOT / "START.json", start)
    study.write(study.ROOT / "RECIPE.json", recipe)
    candidates = set(range(981731101, 981731293)) | set(range(981732101, 981732149)) | {study.SEED}
    seed_audit = scan_seeds(candidates)
    study.write(study.ROOT / "SEED_SCAN.json", seed_audit)
    evidence = {
        "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "timing": "post-design and pre-new-campaign output",
        "composition_report": {"path": str(study.ROOT.parents[1] / "analyses/root-operator-composition-transfer-live-2026-09-10/REPORT.md"), "sha256": "80a955add6e0964ba1ef1ccd4308bad1a37ab267458e693b1fa466dbc64bdb90"},
        "dose_retrospective": {"path": str(study.ROOT.parents[1] / "analyses/root-operator-dose-semantic-retrospective-2026-09-10/REPORT.md"), "sha256": "61a9742c38adb10a219f1358c3a4a749b5a6664ee262557fa3694d900d6f08fd"},
        "interpretation": "29 dose24 strict answers include 26 requested computations; composition SFT24/SFT6 exact 9/48 vs6/48 but faithful primitive 2/0 and faithful composed 0/0",
        "science_unchanged": ["coordinates", "seeds", "terminal reward", "training contexts", "readout", "optimizer numerics"],
    }
    study.write(study.ROOT / "POST_DESIGN_EVIDENCE.json", evidence)
    inputs = list((study.ROOT / "inputs").glob("*.json"))
    receipt_inputs = inputs + [study.ROOT / name for name in ("START.json", "RECIPE.json", "SEED_SCAN.json", "POST_DESIGN_EVIDENCE.json")]
    campaign = {"schema": "root-sft24-terminal-rlvr-v1", "campaign_id": study.CAMPAIGN_ID,
                "namespace": study.ROOT.name, "seed_master": study.SEED,
                "scheduled_windows": 8, "maximum_actual_optimizer_updates": 8,
                "training_attempts": 192, "readout_attempts": 96,
                "child_sha256": study.CHILD_SHA, "root_sha256": start["policy"]["adapter_sha256"],
                "outer_seconds": 10800, "gpu_calls_in_preparation": 0,
                "source_sha256": pins(source_paths()), "input_sha256": pins(receipt_inputs)}
    study.write(study.ROOT / "CAMPAIGN.json", campaign)
    print(study.CAMPAIGN_ID)


if __name__ == "__main__":
    main()
