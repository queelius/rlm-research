# Adaptive root-only RLVR, eight fresh updates

CPU preparation only. MAIN controls the starting-weight decision, acceptance and sole-GPU launch. This is a small adaptive follow-on to the interface SFT experiment, not a continuation of either historical optimizer.

## Question and fixed comparison

Can root-only outcome learning improve metadata-sensitive record selection and aggregation using the ordinary public `await rlm(...)` API, with the compatible typed child fixed at c32de? Compare the separately MAIN-frozen start with campaign checkpoint 8 on identical validation/transfer coordinates and seeds. Fixed final 8 is primary; validation never chooses a checkpoint or extra rollout.

Use the exact root-interface-sft-v1 prepared-v2 896 normalized-question allocation: 384 training, 192 validation, 64 query transfer and 256 length transfer. These are newly composed/root-history-excluded but leaf-training-supported TREC questions; source-test novelty and absence of base pretraining exposure are not claimed. Keep every record, public prompt, category definition and host-only answer unchanged. No operator program, forced recursion, answer repair, cost reward or complete-map requirement.

Eight rounds each sample two prompts eight times (128 trajectories). Rounds 1–4 pair 32-record context i with 64-record context i+4; the small context uses single-user on even i, global on odd i, and the large context the opposite. Rounds 5–8 use the other scope for the same pairs. Thus all sixteen training prompts receive eight fresh samples exactly once. Task order is round-robin within a round and all sampling seeds are frozen before inference. Post-allocation gold/skew summaries are descriptive, never a filter.

Validation is four contexts × two scopes (8 coordinates) at steps 0, 4, 8. Query and length transfer are 8 coordinates each at steps 0 and 8, for 184 total planned trajectories. Repeated seeds are deliberate only within a paired readout; training seeds are all unique and disjoint from readout. Analyze query and length separately, paired by task/seed with source-context clustering; 184 is not an independent-sample count. Nulls and the planned denominator remain visible.

## Start, objective and admission

Preparation permits only two exact warm-start families: root-interface SFT fixed final4, or historical recovered-root checkpoint8 `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`. A later immutable MAIN binding authenticates the chosen adapter/config and result/state/selection lineage after SFT readout. No automatic fallback or best-validation choice. Both enter this campaign as generation0 with empty Adam moments and fresh RNG; historical step number is provenance, not optimizer cursor. If SFT fails, the historical checkpoint is the first explicit alternate; if neither demonstrates usable model behavior, a no-learning interface probe is preferable to manufacturing a gradient.

Reuse the qualified root-only TIS/PPO loss, exact FP32 LoRA loading, BF16 base, equal-episode/equal-root-turn/action-token weighting, finite-gradient/delta and distribution guards. Root temperature .5/top_p1/top_k-1/min_p0 with native processed log-probabilities. No retokenization, fabricated behavior likelihood, child/observation targets, grammar-constrained root or synthetic fixture training. The child's grammar changes its own conditional sampling only; all child actions remain evidence, never root credit.

Completed observable empty, malformed or incorrect final answers receive binary zero only when the actual native root graph is admissible. An exact correct `Answer: N` receives one. Setup/provider/unavailable/incomplete capture is null; malformed or mismatched identity/mask/physical-token evidence is an integrity stop, not a guessed negative. All planned attempts are retained. Training uses only fresh within-task mixed admitted groups; a round with no mixed group stops without rerolls. No additional minimum-success or arbitrary recursion-shape gate.

## Critical adaptations, not a new framework

1. Bind the exact frozen SFT data/tasks and typed native interface. Reuse the actual rootless setup and renderer; authenticate the accepted runtime amendment separately if MAIN replaces setup-only code. Export physical root causal turns through the existing native graph seam, with typed child decisions/logs retained and no weaker token or weight checks.
2. Reuse campaign checkpoint/optimizer/RNG machinery in a private module namespace, overriding only explicit start identity and sixteen-row/two-task admission. Preserve per-generation group/input/correction hashes, stale-generation and repeated-step rejection.
3. A small serial coordinator alternates an owned two-alias service, collection, release, and one optimizer step. Existing title-change/process-absence ownership handling is reused. No analysis may hold GPU ownership after the final service releases.

Budget proposal: 7080 seconds work plus 120 seconds owned cleanup, 7200 inclusive, 7230 outer. Per collection/validation/transfer stage caps, service readiness and optimizer cap remain bounded by the one shared work clock. Four collectors and the existing native episode budgets are the default; any changed runtime budget must be explicitly frozen, not silently inherited. Every committed update saves adapter, Adam, RNG, correction capture and cursor. A cap/terminal stop preserves completed outcomes and all prior checkpoints; no implicit retry.

## Qualification and limitations

Focused CPU tests cover the 16-prompt/184-coordinate allocation, split/seed isolation, binary/null admission, warm-start cursor reset, real three-call native graph/root-only export, typed-child no-credit, and tiny two-generation persistence/stale/double-step rejection where practical. Authored fake-provider log-probabilities qualify plumbing only and are permanently excluded from scientific exports. No generated code executes on the host; any authored REPL fixture runs in the existing rootless runtime.

The first small round may have homogeneous rewards and stop. Eight updates are exploratory and insufficient for broad planning claims. Service order and native numerical scheduling mean paired seeds are not deterministic counterfactual trajectories. Endpoint success does not validate every intermediate semantic label. Full physical/logical/cached token costs, actual calls, exclusions and setup time must be reported separately.
