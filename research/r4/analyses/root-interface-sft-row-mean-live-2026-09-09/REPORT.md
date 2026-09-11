# Equal-row loss did not improve this four-update root SFT comparison

Final independent outcome audit, September 9, 2026. **Both checkpoints solve the same 2/24 coordinates.** Equal-row training produces fewer valid final answers and less complete helper coverage, while consuming fewer calls overall. The two jointly successful coordinates cost almost the same in both arms. This does not establish a successful-task efficiency improvement.

The narrow result is negative for this exact loss-normalization intervention. It does not show that all equal-row training is ineffective, nor identify loss weighting as the main remaining bottleneck. In fact, the short terminal examples already have almost zero training loss; increased coefficient weight does not demonstrate a substantial new terminal learning signal.

## What actually ran

R is the new equal-row fixed final checkpoint4, model `b6a30a29687081dd7dc1b2f9a74ff7a7ccd70722c0fd5abd8c96380196e15b6a`. T is the previously trained global-target-token fixed checkpoint4, `efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64`. Both started from historical root `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd` with fresh Adam, not from one another. Both readouts use the same fixed typed child `c32de129…`.

The auditor verified the original 32 authored rows, shifted action masks, EOS, four effective batches, order and seed981284002, 64 row exposures and 3,206 target-token exposures. Inputs and previous actions/observations are masked; neither model trains on sampled operator likelihoods. The only declared numerical training intervention is the loss denominator: global target-token mean versus mean of 16 per-row token means. BF16 base, FP32 adapter and unchanged child are recorded. Saved load audits report all504 original adapter tensors exactly equal with no missing/unexpected keys; this audit authenticated those records rather than repeating a model load.

All four R checkpoint states and member hashes authenticate; final Adam state has cursor4, and fixed-final selection agrees with RESULT/SELECTION. T's existing final checkpoint/Adam/member closure and recorded same-order steps also authenticate. R trained31.477s versus T's historical31.650s. Final adapter delta from the common start is1.175706 for R versus1.169540 for T; all gradients/deltas are finite and nonzero. R's recorded peak allocated GPU memory is11,027,322,880 bytes. These checks do not substitute a new independent tensor-forward qualification.

The new readout contains48 completed trajectories on24 fresh-seed coordinates nested within eight **already exposed** contexts: eight validation, eight query-transfer and eight length-transfer coordinates per arm. R ran before T in separate service phases, each with four workers. Both have the same local runtime/image/typed matcher, root sampling and exact frozen first physical prompt IDs. All24 paired first inputs and sampling settings match; later adaptive trajectories are not assumed identical.

Primary sources: [training RESULT](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-interface-sft-row-mean-v1/outputs/attempt-001/training/RESULT.json"), [SELECTION](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-interface-sft-row-mean-v1/outputs/attempt-001/training/SELECTION.json"), [scientific TERMINAL](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-interface-sft-row-mean-v1/outputs/attempt-001/TERMINAL.json"), and [full independent reconstruction](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json").

## Outcomes and coverage

| Metric | Existing token mean T | New equal row R |
|---|---:|---:|
| Strict correct /24 | 2 | 2 |
| Strict final syntax /24 | 9 | 7 |
| Completed protocol failures | 15 | 17 |
| Valid syntax, wrong number | 7 | 5 |
| Null / empty / unrun | 0 /0 /0 | 0 /0 /0 |
| Exact first HELPER code /24 AST-valid first actions | 22 | 21 |
| Actual first helper requests exactly first4 IDs | 22 | 21 |
| Uses helper /24 | 24 | 24 |
| Requests beyond first4 /24 | 16 | 12 |
| Full relevant valid-map coverage /24 | 16 | 12 |
| Valid requested-ID maps / helper calls | 75/75 | 47/47 |
| Correct label occurrences / classified occurrences | 1017/1092 | 779/844 |

R−T has zero wins, zero losses and24 ties: the same query-transfer seed981300207 and length-transfer seed981300302 are correct. Both score0/8 validation,1/8 query transfer and1/8 length transfer. Syntax varies by stratum: T→R is2→0 validation,5→3 query,2→4 length. Exact per-coordinate outcomes and paths are retained in [AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json"); no old readout is pooled into these counts.

All48 raw endpoints are observable, completed and agree with the frozen collector. There are no episode/trace errors, request-only tails or native graph failures. All285 physical attempts return HTTP200, and physical sampled IDs/logprobs reconcile with native role/graph evidence. Root calls have no child grammar; all122 typed child maps meet duplicate-free exact requested-ID and canonical-label rules. Thus these observed failures are not explained by missing child JSON structure or an availability-null gate. Map validity does not guarantee semantic labels or correct root aggregation.

Coverage is source-authenticated native helper coverage, not a claim based on generated prose. Label-occurrence denominators include repeated classifications and are not independent question groups. The one-row reduction in exact copying is not evidence of better planning; the more direct coverage measure moves downward.

## Two distinct remaining failures are visible

The conservative map diagnostic looks only for standalone literal maps on the actual final physical root branch, supported by native child values. It finds complete unambiguous relevant maps in4 R episodes and6 T episodes. Other cases remain partial (R19/T17) or conflicting (one each); these are **diagnostic unavailability**, not endpoint nulls. A model may use other non-map observations, so this is not an exhaustive consumption metric.

Two examples separate failure mechanisms:

1. In query seed981300208, both roots see a complete supported map whose relevant count is6, matching gold, but answer `Answer: 7`. This is a root map-to-count failure, not missing helper coverage. [R raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-interface-sft-row-mean-v1/outputs/attempt-001/equal_row/rollout/episodes/73454366c25e7fb6d0f6b8822d397e6f562341905b3b4b97b29c3f8baa9613e0.json").
2. In length seed981300303, the supported map implies17 versus gold18; both final replies also fail whole-reply syntax. Here a semantic map error and root output failure coexist. Neither can be repaired away in the primary score. [R raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-interface-sft-row-mean-v1/outputs/attempt-001/equal_row/rollout/episodes/9f9995a445c3c42e5e4058ba1e01b0b41848ec0d904c9e88882499ea042facb1.json").

A clean format example is T validation seed981300101: the supported map count is2, matching gold, but the reply is bare `2`, hence strict failure. Its paired R instead stops with a prose/code-block plan after classifying only first4 records, none query-relevant. [T raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-interface-sft-row-mean-v1/outputs/attempt-001/global_target_token/rollout/episodes/62c755dc6451a393eb54b019b6cc630df0e190e098a0b273c1cf0075835c997d.json"). No model-generated code was executed by this audit. Full conservative diagnostics: [DETAILS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: DETAILS.json").

## The coefficient intervention was real; its learning signal was not demonstrated

R's nominal terminal coefficient mass across batches is56.25%,43.75%,50%,50%; T's is6.73%,3.93%,5.12%,5.24%. Executed FP32 coefficients and objective sums match the intended formula. These numbers are **not gradient shares**.

R's observed terminal summed CE is only3.10e−6,2.50e−6,2.26e−6,2.15e−6 across updates. Helper CE is236.06,186.48,60.02,10.12. Terminal weighted objective contribution remains approximately2.6e−8–3.7e−8 per batch. The terminal microtasks were already extremely easy under teacher forcing. This supports investigating the gap between these authored terminal contexts and real child-observation contexts; it does not prove a gradient mechanism or that different examples will work. Row-mean NLL and global-token NLL are different objectives and must not be read as directly comparable learning curves.

## Cost and clocks

| Provider-reported quantity | T | R |
|---|---:|---:|
| Root / child attempts | 96 /75 | 67 /47 |
| Root input / output tokens | 156678 /13439 | 91041 /8431 |
| Child input / output tokens | 83366 /10026 | 55904 /7708 |
| Total cached / uncached input | 209488 /30556 | 126736 /20209 |
| Collection phase seconds | 296.629 | 263.793 |

All cache/input/output usage fields are known. R uses66.7% of T's calls,61.2% of input tokens and68.8% of output tokens across all24 pairs. But on the two jointly correct pairs, both use10 calls, input13274R versus13263T and output1158R versus1147T. The aggregate savings largely occur among failed trajectories and coincide with reduced coverage. Do not advertise them as better successful-task efficiency.

The scientific launcher reports complete/no error and718.578 seconds overall, including load/train/service/readout work. Summed per-episode wall time (R1012.57/T1072.12 seconds) overlaps four workers and is not total job wall time. Cache usage is provider accounting, not independently measured GPU work; inherited retry capability is not a claim of zero API retries. Lifecycle/GPU release is parent-owned; this audit did not query or control GPU processes.

## Decision and limits

Do not promote equal-row normalization alone from this result. Retain the source/checkpoint as a completed controlled negative comparison. The most informative next distinction is whether final-answer competence improves when training includes challenging, faithful native child-observation→aggregation→strict-answer contexts, with adequate semantic coverage checked separately. That is a new data/task intervention, not a conclusion that weighting was wrong or a license to turn these evaluation episodes into training examples.

Only one training seed, four updates, 32 authored examples, eight exposed context clusters and sequential service phases were tested. A reused T checkpoint is not a simultaneous replicated training run. This is a paired training-recipe comparison; it does not isolate an objective-only mechanism beyond that intervention, prove broad RLM improvement or establish a general cost-aware policy.

The method was sealed before new outcomes. The auditor did not author the new weighting intervention but did author shared original SFT/native components: independent outcome reconstruction, not independent framework authorship. The sole execution correction was an auditor filename/internal-request-ID join, preserved in [PARSER_CORRECTION.md](PARSER_CORRECTION.md); the original method/parser remain unchanged. Five focused pre-outcome fixtures passed, and the additive terminal audit and details reconstruction both exited0. [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") records exact consumed artifact hashes; [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") is the compact machine readout, and FINAL_MANIFEST seals this publication.
