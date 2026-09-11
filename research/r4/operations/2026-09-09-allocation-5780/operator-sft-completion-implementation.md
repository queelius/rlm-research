# Operator72×6 additive completion — CPU READY

READY: `/project/alex_phd/runs/rlm-research-r4/sidecars/root-operator-diverse-sft-completion-v1/READY.json`

- SHA256 `feff648da34b026d2e8e1c68945bb9d9d611f2d418cf61dc5d6ce4c9928e255e`
- Identity `19aa88f7b23339940c05c28709470db45f7bf43d62ecc73707638474ffd98f34`
-1185 source and4136 input pins; SOURCE_RECEIPT SHA `b0afd79f0c7c9687a0bc9b3b7094c540ea38765fb2e9c23aba0d51f0888a4c8f`.
- CPU_REPORT SHA `f648c487668f02f20f95b87207e3b8ed46449385e87a38b1e635e54e35aff421`: five focused tests passed in6.58s. Subsequent actual `recovery.py verify` exited0 with the identity above. No GPU/service/lock/queue action occurred.

## Exact defect and bounded fix

I authored the failed operator owner and common runtime plumbing; this is engineering diagnosis, not an independent scientific audit. Original `od_owner.py` routed training through installed `leaf-post-sft-suite-v1/suite.py:189–213`. That command is explicitly evaluation-only: it records `gpu_visible_to_command:false` and unconditionally empties `CUDA_VISIBLE_DEVICES` at line194. The installed an27 lifecycle adapter changes service identity checks, not this function. The actual original trainer COMMAND and traceback establish the same path. Failure occurred after5.56854s before model load audit, gate or optimizer checkpoint. The prior interpreter fix supplied PEFT but did not test this execution boundary.

`operator-sft-gpu-env-diagnosis.py` in this operations directory (SHA `39b506260f889b09aa4d47b15d5a5a0dbfd969013fa9a12dabc15731b75d277f`) traversed the accepted original owner→installed command→intercepted training Popen. A nonempty assigned CPU sentinel reached the owner; the intercepted trainer environment had an empty GPU variable. No process was created. No hardware or GPU-model inference was required.

The new owner uses the qualified joint owner's separate GPU-process pattern: unchanged inherited GPU/MIG identifier, owned process observation, bounded wait and owned stop. The stage cap is3600 instead of the earlier joint helper's600. The actual composed regression verifies the MIG-shaped value at training Popen and, separately, an empty GPU value at the installed collector Popen. Readout service lifecycle/config generation remains the existing accepted an27 path.

## Preserved science and exact adaptations

The actual training argv invokes the **original unmodified** `root-operator-diverse-sft-v1/od_train.py` with the qualified bootstrap TRAIN Python, original mode train, a fresh completion output and absolute deadline. Thus original72 capture closure, native prefixes/masks, wrong child predictions/scalars, six gate members, seed981451003, fresh Adam1e-4, six complete passes and .45/.50/.05 objective remain unchanged. No model/corpus copying, numerical rewrite, capture rerun, baseline rerun, optimizer resume, checkpoint selection or partial6 substitution occurs.

Only the original binding selector's `directory=s.ATTEMPT/'training';` is adapted once to the completion training directory. Original corpus path and original scientific identity remain in checkpoint validation. The new READY/owner identity records recovery provenance separately. The root alias/task/seed stays the original fixed-SFT6 specification; its adapter path/hash is the new fixed6 checkpoint. Exact-path imports and scoped aliases are used for original owner, protocol, binding and collector. A CPU test caught a deferred protocol import outside its alias scope; initializing that qualified dependency inside its scope fixed it before READY.

The collector wrapper exposes only original free-plan coordinates0:24, the new fixed-SFT6 service descriptor/binding and new output. Its actual composed entry point and deferred `od_binding` import were tested. A six-checkpoint authored fixture authenticates new directory selection, preserved original corpus ancestry, fixed c32 and rejection of changed ancestry. It is a namespace/receipt test, not a real optimizer or model-load test. Existing original numerical/native qualification is reused, not relabeled as a new full4B test.

## Original accounting and time separation

The frozen original owner has24 planned baseline coordinates, **23 recorded RESULT files**, zero recorded SFT6 endpoints and no active service. Baseline coordinate `74658bc6ce3fa781d193d0fccd2c3256a05f81d985b92429e0f30e5106354889` is absent and remains NULL; recorded native-unavailable rows also remain NULL. The initial24-recorded summary was corrected during source admission. All original artifacts are hash-pinned; none are rewritten. New fixed6 endpoints pair to all24 original planned coordinates, not24 complete observed pairs. The original48 inventory and original SFT24 NULLs remain historical evidence; the comparison is explicitly a time-separated additive completion.

The new ledger counts actual new root/optional-child physical attempts and links the original complete capture/baseline ledger, charged once as shared physical work. Standalone recipe accounting includes original capture/baseline plus new training/readout; no equal-token/FLOP or provider-billing claim. Missing6 leaves all24 new planned endpoints unavailable.

## Owner CLI and caps

`/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-operator-diverse-sft-completion-v1/recovery.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-operator-diverse-sft-completion-v1/outputs/attempt-001`

MAIN-only acceptance/launch.5400 outer,5220 work,5370 owned;150 cleanup and30 outer margin. Training≤3600; only the fixed6 readout≤1200 inclusive startup/release;300 finalization and120 slack. Training also respects the final-stage reserve. Caps advance early rather than waiting. All24 NULLs are written before training. Missing fixed6, timeout, returned malformed finals and native unavailability retain their original distinctions. No present attempt existed at seal.
