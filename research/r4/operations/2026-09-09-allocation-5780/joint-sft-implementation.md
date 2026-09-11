# Joint live-state SFT: CPU handoff

2026-09-09. New sidecar `sidecars/root-joint-state-reduction-sft-v1` is sealed for MAIN acceptance. MAIN reviewed the complete design/source/tests and reported no material blocker. No GPU, service, container, download, lock, live-queue edit or old-artifact mutation occurred. I authored the runtime/training plumbing; outcome mechanisms will require an independent actual-trace audit.

READY SHA256 `668200f5ebbdaa3d8fb96e1df654a65224a80bf1e1d2a7a2658e8bd938bff75d`; identity `dccf1455749087be0a60bff1dd761f442e77d61ccab331539e9bf7bf440b56a1`. CPU_TESTS SHA256 `b1c1dfbe5d69ec0f6873fc3c266d2661ecbbf6bfb1ee1cd4a3bac23abd01c22d`. Frozen DESIGN SHA256 `b03d3a8b9014c6fad3ddffb535ff06a0ff5af740e60a8ff4aa0ace8be9c8338c`.

Exact invocation (MAIN supplies its private credential/GPU environment and lock, outer5400s):

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-joint-state-reduction-sft-v1/owner.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-joint-state-reduction-sft-v1/outputs/attempt-001
```

The actual native `owner.py verify` returned the identity above, exit0. All2,885 unique inherited/new source/input paths were hashed and verified. The exact attempt did not exist at handoff. No credentials were read into logs or arguments. A scoped `rg` check of other sidecars' Python sources and `*PLAN*.json`, excluding outputs/owned state and this new sidecar, found no `981361xxx` match (exit1/no matches); no outcome scan.

## Changes and scientific contract

- `joint_protocol.py` authors actual same-REPL initialization, real c32 calls, cumulative updates, live-variable user-scoped count, and authentic scalar final. Width4 never resets prior labels. There is no map literal in the reduction target. Actual wrong labels/counts remain; incomplete source capture fails rather than selecting replacements.
- `prepare.py` freezes same eight training contexts/128 groups,16 trajectories,40 acquisition calls/72 authored root turns; first4 cover all width×scope cells. Four training aliases vary, with two unseen aliases in eight controlled sources (20 actual acquisitions). Forty native prompts are1102–1107 tokens. All policies receive the same accurate id/user/text and prediction-visibility contract.
- `joint_learning.py`/`train.py` implement per-trajectory joint .45 acquisition/.50 reduction/.05 final versus .95 reduction/.05 final; history masks remain exact native prefixes. Four full16-example updates from unchanged low66c/fresh AdamW and frozen c32; original qualified per-update adapter/optimizer/RNG checkpoint chain and fixed4 selection retained. No RL likelihood or gradient-share claim. Fixed4 code-span gate excludes Python string literals and requires3/4 NLL>.1 plus measured cost limits.
- Local `collect.py` reuses actual native capture and final-branch authentication. Controlled and training-state continuations reproduce exact source requests/prefixes. Returned malformed final is0; mismatched/unreturned endpoint is NULL. Static code markers and scalar agreement are not labeled executed reduction.
- `joint_binding.py` validates true starting/selected adapter closure and c32. `joint_study.py` and other uniquely named local modules avoid ambiguous service/config-provider imports. Old native/runtime sources are pinned and unchanged.
- `owner.py` writes all84 planned NULL rows before the first launch: three policies × (16 free heldout +8 controlled heldout +4 training-state diagnostics). Training diagnostics are not heldout or training feedback. Orchestrator completion is separate from authenticated final availability.

Exact lifecycle: work starts at owner entry and ends at+5100s; owned alarm+5280s; MAIN outer+5400s. Reserve180s for owned cleanup after work and120s outer margin. All stage caps intersect work; releases consume the same shared clock. One teacher-service phase captures all16 train+8 controlled sources, then fixed first4 forward gate before any gradient. Capture-all-before-gate is a disclosed prospective startup-saving choice, not a claim of early capture savings. Capture collectors share900s; gate180s; two training stages≤600s each within1200s; service readiness≤180s each; each policy free480/controlled240/diagnostic120s. These stage ceilings are not promises that their maxima fit additively. No retry, alternate checkpoint or overwrite. Existing an27 lifecycle handles owned release in each service `finally`.

## Focused verification

**15 tests passed**:13 native/protocol/owner tests (process wall10.073s) and2 tiny CPU tensor/actual Adam tests (2.886s),12.959s total. Native tokenizer emits three existing SWIG deprecation warnings; no test failures. `collect.py --help` in native Python and `train.py --help` in training Python both exited0. Python AST parse covers all new source files.

The material integration test runs **actual owner.execute → qualified suite.start_service → actual service_wrapper_v2 → real InferenceConfig validation/config writes → real descriptor writes**. It intercepts both Popen boundaries and external readiness/adapter-network calls, never launching a process/service. It verifies all84 planned rows preexist, exact service/interpreter argv, original low66c model bytes, c32 dual binding, endpoint descriptor validation,8192 context, current driver library and actual-wrapper launcher hash. Intentional intercepted startup termination reaches the owner's cleanup boundary and leaves all84 rows NULL. Cleanup itself is the unchanged qualified lifecycle; this CPU test does not claim to test live process teardown.

Other tests cover real authored batch execution in a CPU namespace, wrong-label retention, native mechanism-versus-literal offsets, exact scientific source-replay fields, width/scope counts and data separation, equal trajectory/role loss mass, shifted token CE and one complete Adam step, deadline refusal to advance a partial update, actual owner→collector argv parsing, wrong output namespace, and observed-invalid0 versus identity-mismatchNULL. The planning/TDD skills guided the local contract tests and the composed integration; no broad suite or repository refactor was used.

## Limitations retained for launch/audit

Real corpus capture, NLL headroom, GPU load/optimizer cost and policy outcomes remain unqualified until the accepted run. Equal updates/examples/objective mass are not equal tokens/FLOPs, and joint reduces the control's reduction coefficient. Final-copy CE may already be saturated; its small weight anchors a boundary rather than proving new headroom.

**Controlled alias and width are tied by `(ci+qi)%2`; alias-versus-width effects are not separable.** Policy contrasts remain paired at each identical state. Four-context heldout data have prior research exposure; only user-set compositions/seeds are fresh, and operators are familiar. Training-state success is memorization evidence, controlled success is conditional skill, and free actual reduction+finishing is the intended reachability evidence. No learning claim follows from teacher CE or map/scalar agreement alone.

Source costs are60 physical child calls before sampled readout, plus failures and authored execution. Controlled standalone accounting adds60 hypothetical acquisition calls across24 heldout controlled endpoints. The first4 training sources contain10 already-physical acquisitions;12 training diagnostics add30 hypothetical standalone calls, not30 additional physical calls. Per-call records retain actual versus replayed origin. MAIN may defer this job if restart/interface evidence removes the proposed training bottleneck.
