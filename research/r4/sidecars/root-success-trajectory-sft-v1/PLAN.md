# Complete-success trajectory SFT Implementation Plan

> For agentic workers: use superpowers:executing-plans inline. No subagents or GPU authority.

Goal: prepare the exact approved eight-update,27-trajectory imitation comparison and48 paired readouts.

Architecture: a small independent study/export/trainer plus private adapters around the already qualified native readout and owned lifecycle. No accepted source edits. Spec: DESIGN.md in this directory. Tech stack: existing native Prime Python and existing Torch/PEFT training Python; no installs.

## Global constraints

Exactly27 confirmed/114 root turns/15,256 targets; all recovery turns retained; source-native physical suffixes only; fresh efab Adam;8 full-corpus updates; LR2e-5; equal episode→turn→token mean;1200/3180/3300/3330s caps; fixed final8; fresh seeds981308…; fixedc32 child. MAIN approval is recorded in DESIGN.md, with launch authority explicitly absent here.

## Tasks and verification

- [ ] Freeze source/data identities and bounded seed audit in study.py/prepare.py. Authenticate the candidate seal, each selected committed round/raw/role/typed source once, reconstruct actual native turns and compare the old export. Export only27 selected episodes. Tests reject a provisional/evaluation coordinate, a child turn, shifted length/mask mismatch and artificial stop insertion. Literal fixture: prompt[1,2],action[3,4] becomes labels[-100,-100,3,4], never an extra EOS.
- [ ] Implement train.py's equal episode/turn/token update and immutable checkpoint/resume. First failing fixtures use two episodes with1 and2 turns and unequal token counts: each episode has mass1/2; turns have1/2,1/4,1/4. Altering prompt logits must produce zero prompt-position gradient. Run a tiny real CPU LoRA model through update/save/resume and reject changed identity/duplicate update before claiming qualification.
- [ ] Reuse the qualified row-mean private study/native/local-runtime seams for readout.py/launch.py. Replace only authentic root binding/final8 selection and frozen plan crosswalk. CPU tests assert old and fresh prompts match, only seeds/IDs differ; wrong adapter/prefix/binding is rejected. Use no API/model calls in tests.
- [ ] prepare.py produces exact export/coefficient/length/provenance and24 fresh-prompt audit, then runs focused native and tiny-training CPU tests. RUNBOOK.md documents exact MAIN argv, output/checkpoints/resume and failure boundaries. Publish READY.json last, source/input/test hashes frozen, launch_authorized=false. Run fresh verify commands and hand source closure to MAIN for review.

Each task follows test-first RED→GREEN. Outputs are generated once in this owned sidecar; failed qualification records remain. No Git commit/worktree is applicable to the external research store. Completed checkpoint recovery may be called only by MAIN after a failed launch; the scientific recipe, data and cumulative training cap cannot change.
