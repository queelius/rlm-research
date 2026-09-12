"""Exact predecessor owner with truthful seed-replica admission and V2 alias fix."""
import reuse

reuse.execute("owner.py", globals(), [
    ('core.DATA / f"inputs/step-{step:03d}/REQUESTS.json"',
     'core.ROOT / f"inputs/step-{step:03d}/REQUESTS.json"'),
], skip_main=True)


def check_admission(path, ready):
    admission = core.read(path)
    if admission.get("cpu_fixture") and os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("synthetic CPU admission fixture is not GPU launch authority")
    expected = {
        "authority": "MAIN",
        "training_ready_sha256": core.sha(core.ROOT/"READY.json"),
        "decision": "APPROVE_TRAINING_SEED_REPLICATION",
        "endpoint": "fixed-step8-versus-c32-on-same-exposed512",
        "start": "fresh-original-c32-not-seed1-continuation",
        "prior_seed1_heldout512_consulted": True,
        "replica_checkpoint_evaluated_before_training_complete": False,
        "data_manifest_sha256": core.sha(core.DATA/"inputs/MANIFEST.json"),
        "seed_namespace": "agnews-broader8-seed2-20260912",
    }
    if any(admission.get(k) != v for k,v in expected.items()) or not admission.get("reason"):
        raise ValueError("explicit truthful MAIN seed-replication admission differs")
    evidence = admission.get("reviewed_evidence_sha256", {})
    required = [reuse.PRIOR/"READY_V2.json", reuse.PRIOR/"outputs/attempt-001/FINAL_RESULT.json",
        core.SIDE.parent/"analyses/helper-agnews-eightstep-live-audit-2026-09-12/outcomes/RAW_AUDIT-003.json"]
    if any(evidence.get(str(p)) != core.sha(p) for p in required):
        raise ValueError("reviewed seed1 recipe/result/paired outcome evidence absent")
    for raw, value in evidence.items():
        if core.sha(raw) != value:
            raise ValueError("reviewed admission evidence changed: " + raw)
    # V2's observed repair: the lazy train_ag import occurs DURING qualify().
    with core.original.aliases({"ag_study": core.original}):
        initial = core.load_bound("ag_seed2_actual_initial_qualifier", core.SOURCE/"eval_owner.py",
                                  {"ag_study": core.original})
        initial.qualify()
    if core.read(core.SOURCE/"outputs/attempt-001/RESULT.json").get("mixed_reward_groups",0) <= 0:
        raise ValueError("source pilot lacks verified mixed groups")
    prior_core = core.load_bound("ag_seed2_prior_completed_core", reuse.PRIOR/"core.py", {})
    final = core.read(reuse.PRIOR/"outputs/attempt-001/FINAL_RESULT.json")
    if final.get("status") != "UPDATED_STEP8" or final.get("endpoint") != prior_core.parent_for(9):
        raise ValueError("replicated seed1 lacks full committed c32-to-step8 trajectory")
    return dict(path=str(path),sha256=core.sha(path),receipt=admission,
        ready_identity=ready["identity"],
        initial_qualified_result_sha256=core.sha(core.SOURCE/"outputs/attempt-001/RESULT.json"),
        prior_full_chain_qualified=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify","check-admission","run","endpoint"))
    parser.add_argument("--owner-seconds",type=int,default=5000)
    parser.add_argument("--admission-json",type=Path,default=core.ROOT/"ADMISSION.json")
    parser.add_argument("--resume-after",type=int,default=0)
    args = parser.parse_args()
    ready = core.verify()
    if args.command == "verify":
        print(ready["identity"])
    elif args.command == "check-admission":
        import sys
        if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
            raise ValueError("CPU admission preflight must hide CUDA")
        before = sys.modules.get("ag_study")
        started = time.monotonic()
        receipt = check_admission(args.admission_json,ready)
        assert sys.modules.get("ag_study") is before
        print(json.dumps(dict(actual_qualification_passed=True,alias_restored=True,
            GPU_launched=False,attempt_exists=core.ATTEMPT.exists(),
            elapsed_seconds=time.monotonic()-started,receipt=receipt),sort_keys=True))
    elif args.command == "endpoint":
        final = core.read(core.ATTEMPT/"FINAL_RESULT.json")
        if final.get("status") != "UPDATED_STEP8" or not final.get("primary_endpoint_eligible"):
            raise ValueError("fixed complete step8 unavailable")
        print(json.dumps(core.parent_for(9),sort_keys=True))
    else:
        result = execute(args.owner_seconds,args.admission_json,args.resume_after)
        print(json.dumps(result,sort_keys=True))
        raise SystemExit(0 if result["primary_endpoint_eligible"] else 1)
