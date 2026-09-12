# Fixed512 endpoint handoff

MAIN is the sole launcher. Run each arm once under the shared GPU flock and an external1000-second timeout, with the inherited private credential and one assigned CUDA device:

`/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run --arm c32 --outer-seconds 900`

Replace `c32` with `rl_step8` or `sft_step8`; the separate READY files pin these exact argv. Outputs are `outputs/c32-001`, `outputs/rl_step8-001`, `outputs/sft_step8-001`. All128 calls must be valid, all512 predictions available and the service released with the actual batch-invariant kernel marker before a primary readout or baseline reuse. Never overwrite an attempt or retry a failed call.

Before any arm, MAIN writes a new write-once `ENDPOINTS_FIXED.json` after the compared trained endpoints have completed. Fields:

- `authority`: `MAIN`
- `fixed_step`:8
- `data_manifest_sha256`: `b5e9cc22161959fc09f5e1f15afd03e722a32818bca692a01f9e265fd6c81c2d`
- `heldout512_consulted_before_fix`:false
- `trained_endpoints`: mapping with `rl_step8` and/or `sft_step8`; each value contains exact `checkpoint`, `state_sha256`, `step_commit_sha256`, `binding_sha256` from `owner.py qualify --arm NAME`.

To compare both trained arms with one baseline, fix both in the same receipt before the first query. This file is a runtime authorization/endpoint receipt, not an output-selection mechanism or sealed source. The owner recomputes full eligibility and checks these hashes; `verify` alone intentionally does not assert that an untrained endpoint exists. The SFT arm uses READY_V2 and the RL arm authenticates the V2 admission-only launch receipt as well as its original scientific training closure.

After each endpoint finishes, run CPU-hidden `python compare.py` and capture stdout to a new analysis artifact. It redecodes every valid native envelope, authenticates exact saved request bytes, all record IDs, ordered schemas, tokens, usage, endpoint/state/optimizer lineage, runtime configuration and release. All three comparisons are predeclared: c32→RL8, c32→SFT8, RL8→SFT8. Incomplete endpoints remain descriptive and cannot promote a primary paired comparison; runtime mismatch forbids baseline reuse. Missing response usage is unknown rather than zero. Do not pool older AG256 or flag-off runs.

Training costs and data/objective differences are separate from endpoint128-call usage. This is an exploratory fixed-dose RL-versus-SFT package comparison on heldout public AG train rows after verified local-exposure exclusions, not a base-pretraining exclusion claim, checkpoint-selection study, or512-independent-item significance test.
