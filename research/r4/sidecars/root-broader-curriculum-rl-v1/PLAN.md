# Broader root RLVR implementation plan

> For agentic workers: execute inline with executing-plans; MAIN owns other work and all GPU authority.

Goal: CPU-qualify the approved fixed16×3×8 native root-only RLVR experiment.

Architecture: uniquely named `broad_*` modules adapt immutable bounded-RL data/collector/export/owner boundaries. The actual PPO/TIS/Adam/checkpoint source stays pinned and unmodified; only fixed-window admission and16-cursor identity bounds differ. Existing an27 service/runtime is reused.

Tech stack: native Python/verifiers, training Python/PyTorch/PEFT, existing local model/image. No installs.

Spec: `DESIGN.md` SHA831ff9d4f62bc4de948c7b8c1ca43c78a2eab7e2a826b85f55be1651860db1c9.

Constraints: low66c/c32;384 fixed training slots;80 validation+96 mandatory final; terminal reward only; endpoint availability≠strict training admission; window≠Adam;21600 outer/21180 work/21480 owned/16980 training cutoff; no live old-source edits, no GPU/lock/queue actions.

## Data/task boundary

Create `test_data.py`, `broad_study.py`, `prepare.py`, `broad_native.py`.
- [ ] Red: test public-text parsing produces exact positional IDs/users/text without host labels; compare target-specific actual native prompt/setup and unchanged public bytes after host-gold changes.
- [ ] Implement source-pinned data/plan preparation;16 three-task windows, eight unique seeds/task; separate validation/transfer and public/host maps.
- [ ] Test384/80/96 counts,24 train contexts visited twice, true128/256 transfer and no group intersections; freeze all task hashes and native first-prefix IDs.

## Fixed-window learning and endpoint exports

Create `test_windows.py`, `test_exports.py`, `broad_common.py`, `broad_windows.py`, `broad_collect.py`, `broad_export.py`, `collect.py`, `native.py`, `train.py`.
- [ ] Red: a complete homogeneous window advances only window cursor; an update advances Adam once; incomplete24 never trains; generation9..16 must validate without weakening stale checks.
- [ ] Retain actual root-only native export and PPO/TIS numerics; replace adaptive refill with complete fixed24 export. Validate exactly matched current-policy generation/source/likelihood closure before training.
- [ ] Red: authenticated malformed model final0 differs from missing/unverified NULL; earlier recovered errors retain endpoint availability while strict training admission excludes them. Partial readout accounts every planned slot but partial training cannot update.
- [ ] Reuse persistent optimizer/atomic state checkpoint; verify actual tiny CPU update, restored moments and committed-generation recovery without second step.

## Owner/clock and seal

Create `coordinator.py`, `test_owner.py`, `CPU_TESTS.json`, `CAMPAIGN.json`, `READY.json`.
- [ ] Red: actual owner plans560 NULL slots before any service; monitor stages cannot enter final reserve; cutoff/failure selects last committed policy and attempts both final policies without signal-based selection.
- [ ] Real composed owner→service wrapper→configuration/descriptor→interceptedPopen CPU check; exact collector/trainer CLI namespaces.
- [ ] Focused tests only, source/input hashes, actual owner verify and MAIN handoff. No automatic resume, run, broad suite or Git changes.
