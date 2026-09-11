# Query-sensitive root RL: CPU READY, pending MAIN acceptance

New immutable sidecar: `sidecars/root-query-sensitive-rl-v1`. No old/live source, GPU queue or scheduling lock changed. This is the approved Option A; the retired whole-context BROAD16 proposal remains preserved separately. Implementation is authored by runtime_port, including new scientific task/owner bindings; MAIN reviewed the complete design, plan and core modules. This is CPU qualification, not an independent scientific result audit.

## Ready identity and exact entry point

- READY SHA `23196ce210123bff13f510ce5de0beb25f83fa6cbc1f53095738f7be61481fe7`.
- Campaign identity `ea1d64fc93e7edbf8959609e2264723acb3403dd530dc90b40b3b03c7e141420`; CAMPAIGN file SHA `97bd6ecd99ef6187fd230692be888216d51181c16f68052274eea13d319a6dea`.
- CPU_TESTS SHA `d2a311a501bce8c8d69304e90eefc64e1eea3c72a4de0fd7b9b02212c02207c8`.
- DESIGN SHA `87dcb7c71bb82ee99a8ac5fecb286ce421b4549fbd11317dcbcd8673777666e3`; owner SHA `bcb3fdc0fa73321cb8268736cae1790268afe9b79d8c83fa04207f2fa74f3c8b`.
- Closure: 797 source pins + 34 input/qualification pins = 831. Actual `owner.py verify` exited 0 in 0.598 seconds after sealing. Exact output attempt did not exist at handoff.

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-query-sensitive-rl-v1/owner.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-query-sensitive-rl-v1/outputs/attempt-001
```

MAIN supplies the one owned GPU and provider credential privately in the inherited environment. The owner rejects a missing credential before creating attempt artifacts and rejects an existing/wrong output path. No service/GPU authorization is implied by READY.

## Implemented scope

`qsr_data.py` selects 448 group-disjoint records against the pinned 53-manifest receipt: 12 training contexts × 16; eight held-out contexts × 16 and four × 32. Group selection, ordering, balanced users and visible weights are independent of host gold/model outcomes. Public records contain exactly id/user/text/weight. IDs are q + 12 hex characters. All records are child-training-exposed; novelty means absence from the checked root/prepared catalogs, not globally unseen data. GROUPS SHA `99984ddb15ac2b15ccf86a2cdcfa40016ff86507b5448b1ab29695187e9765c6`; PLANS SHA `50f2e1270be45b0311463cf4eced466a74115ae7fc233522f030ad57a2c98187`. The remaining 78 group availability was handed to bridge_audit for a separate proposal; it did not change these inputs.

Count, distinct-user count and visible-weight sum cross singleton, union and all-user scopes. Six cells train; count/union, distinct/all and weight/single are held out. Twelve fixed 3 × 8 windows yield 288 attempted training slots. Forty-eight held-out inputs, unchanged/final policies and paired seeds yield 96 final slots. All 384 are written as planned NULLs before service startup. The initial native prefixes are 1,062–1,083 tokens. No copied maps, aggregation program, forced recursion, state-start mixture, refill, reward shaping or GPU validation is supplied.

`qsr_native.py` binds the actual task and writes identical public setup files for both policies. `qsr_collect.py` preserves the qualified collector with exactly three counted seams: actual new task constructor, an27 interface configuration, and 180-second endpoint timeout. The original collector source remains untouched. `qsr_export.py` retains all planned rows, separates authenticated endpoint reward from stricter whole-graph training admission, and refuses incomplete/integrity-failed windows. `qsr_metrics.py` checks final physical model/tokens/usage/sampling, actual native final-branch token identity, decoded text and matching root reply. A returned length-capped strict final may score; a tool loop with no final stays NULL. Tool actions are legitimate intermediates here, unlike the earlier no-tools partition decoder study. Returned malformed finals score zero. Paired summaries keep unknown pairs separate and report planned-denominator bounds/sensitivities.

`qsr_common.py` changes only the campaign identity/cursor binding around qualified checkpoint helpers: candidate windows 1–12 versus actual Adam 0–12. `qsr_train.py` admits only complete frozen 24-slot native exports, independently recomputes group membership/advantages and replays native evidence. Numerical TIS/PPO loss, masks, optimizer, guards, Adam/RNG persistence and atomic checkpoint serialization are unchanged. Frozen low66c is the start; frozen c32 is never loaded into the trainable model. Equal episodes do not mean equal target tokens or FLOPs.

## Exact lifecycle and stopping behavior

Outer 14,400 = work 14,100 + owned cleanup 180 + outer margin 120. Training-side time is capped at 9,000 including acquisition, source replay, loading, optimization, checkpointing and release. The final 5,100-second budget protects two 2,550-second policy blocks, including their service lifecycle. Stage deadlines are nested, not extra allowances. No new learning window starts with under 1,440 seconds of training-side allowance. The parent retains GPU/lock authority.

The owner uses the existing working suite and an27 service_wrapper_v2/lifecycle_adapter without changing them or adding driver compatibility paths. Learning failure/zero updates still reaches both final-policy attempts; a genuinely unresolved owned-service release or MAIN termination instead prevents new launches and retains planned NULLs. No automatic resume or reroll is implemented. Every complete update/noop records its consumed window; a checkpoint committed just before trainer failure also records the recovered optimizer AND consumed-window cursors in a no-second-update receipt. Any separately approved continuation must preserve original data/cursors and cumulative debit.

## Focused evidence

Final qualification: 17 focused tests, all passing: 16 native/data/task/cursor/endpoint/owner cases in 10.116 test seconds (11.243 command seconds), plus one real tiny-PyTorch Adam/checkpoint/masking/restore test in 4.00 test seconds (5.120 command seconds). Upstream SWIG deprecation warnings and the tiny PEFT fixture's missing-base-config warning are retained; they are not hidden or model-run results.

One fresh authored CPU native root → typed child → root fixture completed in 19.156 seconds, with three deterministic fake-provider requests and zero actual model/GPU calls. It verifies exact new-ID grammar, all four public fields, actual first native prefix, two credited root suffixes and one uncredited child. Synthetic likelihood admission is rejected. Its actual final also passes the new endpoint authenticator. Fixture RESULT SHA `d580f705f6496a2cb401c98b9dbd859d757f89c60a59ea8fde235b5a03960400`. The ephemeral local fake-provider listener was closed; this was not a model-service launch.

The composed owner test traverses actual owner → qualified suite → service wrapper → real inference config/descriptor, intercepting outer and inner Popen. It checks all 384 NULLs precede launch, max_model_len8192, two LoRAs, correct native Python, unchanged allocation driver path, actual wrapper hash and release handling. Printed PID999999/ready lines in CPU_TESTS are explicitly intercepted fixture metadata, not real processes.

MAIN review prompted the new-ID helper/catalog regression and recovered-window-cursor fix. A focused ownership regression also fixed the learning-release-to-final-state handoff. No broad historical outcome scan or broad test suite was run. Verification/TDD/review skills guided these narrow gates; the approved external-sidecar handoff, not a Git merge, is the integration boundary.

## Preserved limitations and host baselines

Always-zero scores 40/288 training slots and 6/48 held-out inputs. Best fixed constant is 1: 96/288 and 9/48. Thirteen of 108 same-context query pairs have equal host answers. All remain in the frozen plan; these diagnostics did not select contexts/tasks. Singleton distinct-user training is a 0/1 existence task, and 32-record transfer combines length with operator/scope transfer. Report contexts as clusters and do not claim general decomposition from an accuracy or CE change.

Joint-SFT outcome summaries were sent to this implementer during preparation. They caused no change to the frozen low66c start, inputs, objective, task cells or checkpoint rule. Actual QSR endpoint outcomes do not yet exist at handoff. Independent postrun execution/state-use analysis remains necessary; AST mentions or scalar agreement are not credited as verified mechanism by this implementation.
