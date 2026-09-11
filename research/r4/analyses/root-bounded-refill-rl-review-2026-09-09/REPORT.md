# Bounded refill preserves the declared training decision

Final independent CPU source review, September 9, 2026. **No material blocker found within the reviewed scientific scope.** Bound to READY `c5b1247d021a9d6f1c53a4f3aee7caa8352887bc009e57866b617c946e6d3ce7`, CAMPAIGN `21a515ca1a099fb96fe1c02174e60d2c88466dd5c4738f584155b9367b1e4dec`, and coordinator `0e166d2eaea3ac19e36ee573c9b644fa1628e72090946a97aa0c0fb5d6236c89`. This is not launch authorization or a successful-run claim.

The [prospective METHOD](METHOD.md) remains unchanged. I did not author this new campaign; shared earlier root/SFT/native-harness authorship and knowledge of prior experiments are disclosed. I inspected no new campaign outcomes, ran no GPU/service/model calls, executed no generated code, and changed no study source. High-LR outcomes were known when finishing this review, but the approved low-LR starting policy, candidates, method and READY were already fixed.

## Material checks

| Boundary | Finding and exact implementation |
|---|---|
| Frozen candidates and start | [study.py](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/study.py:50") fixes four windows, four groups of eight each, two sizes and two query families. Both readouts retain the same24 fresh-seed coordinates. `fixed_start` authenticates successful low-LR SFT8 `66cce400…`, then exposes RL step0 with no optimizer/RNG restoration from SFT. |
| Consumed-prefix admission | [export.py](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/export.py:10") binds each complete eight-row subgroup to the same full-window generation and exact planned position. A2/3/4-group prefix must obey the stopping rule. Raw manifests and rows are reconstructed before union membership/advantages are recomputed. NULLs are not negative labels or mixed-support evidence. All admitted members of every mixed group are used; a lone mixed group at the four-group bound remains eligible. |
| One current policy | [collect.py](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/collect.py:28") validates full32-candidate generation separately from each eight-row collection spec. The same bound service remains active across the consumed groups; no optimizer is invoked until collection and union authentication finish. A skipped suffix is not reused next window. |
| Native root likelihood | [train.py](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/train.py:19") checks exact consumed rows, rederives membership/advantages, rejects constrained root actions and credited child actions, checks actual audit hashes, and invokes the native union-replay subprocess. [Inherited native reconstruction](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-adaptive-rlvr-v1/native.py:54") checks role/model/body/typed-schema evidence and rejects known CPU fixture likelihood. Prior actions, child actions and observations remain masked; no scripted operator trajectory becomes root RL data. |
| Actual update and recovery | The pinned [campaign trainer](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-rlvr-campaign-v1/campaign_train.py:61") is unchanged numerically: equal episode, then root turn, then current-action token reduction; native processed behavior likelihood supplies capped correction; current-detached proximal likelihood applies to exactly one full-batch step. Distribution guards precede the optimizer. Actual Adam state/RNG restoration, loaded adapter tensor audit, saved INPUTS/correction/commit authentication, and same-generation recovery remain in place. |
| True no-op | [windows.transition](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/windows.py:13") returns the old policy object on zero support. [Coordinator](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/coordinator.py:92") never starts training on that branch. Candidate-window cursor advances while actual Adam step and saved checkpoint/optimizer/RNG remain unchanged. The warm inference service is reused. |
| Final endpoint and budget | Coordinator uses one start clock: training cutoff2820, work3480, inclusive3600, external3630. Final service/readout reserve is660; collection/update bounds are clipped with save/release allowance. Between completed windows, insufficient time selects the last committed policy0–4. Failure inside a sampled window stops rather than training on a partial window. No automatic resume or reroll; original raw failures and later unrun readout coordinates remain distinct. |

## Verification actually performed

[FINAL_CHECKS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_CHECKS.json"), produced by [final_check.py](../../../../ARTIFACTS.md#unpublished-files "Not published: final_check.py"), freshly verifies42 relevant new/input/inherited-adapter hashes against READY. Its model-free generic-selector checks passed in2.45seconds:

| Raw consumed rows | Mixed flags | Selected admitted rows | Decision |
|---:|---|---:|---|
|16|true, true|4|update|
|24|true, false, true|4|update|
|32|false, false, false, true|2|update|
|32|false, false, false, false|0|no-op|

These deliberately sparse fixtures confirm that no hidden four/eight-admitted-row threshold was introduced. Their probabilities are explicitly synthetic and never enter a scientific export. The earlier independent [pure-window proof](../../../../ARTIFACTS.md#unpublished-files "Not published: PURE_WINDOW_PROOF.json") enumerates31 Boolean prefixes and11 legal stopping prefixes, including no-op identity preservation.

I read all final author test sources and the pinned [CPU_TESTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/CPU_TESTS.json"):11 native/window/dispatch/coordinator checks and2 actual tiny-PEFT/Adam checks were recorded passing. The latter exercise saved Adam1, unchanged Python/Torch RNG and moments through no-op window2, then Adam2 in window3, recovery without double step, and child/observation-mask rejection. The native fixture reconstructs two real fixture root turns plus one typed uncredited child, and rejects qualification probabilities for scientific admission. I did not rerun these author tests or claim their execution as independent evidence. The independent variable-cardinality fixtures do not replace a full native scientific union replay; that replay remains a mandatory actual trainer admission check.

## Interpretation and boundaries

- This tests a bounded sampling/training package, not a learned refill policy. Support yield from the first pair versus the consumed prefix is descriptive, not a randomized causal comparison. Equal episode weighting is not equal prompt-group weighting.
- Completed observable strict failures—including empty/malformed answers—remain zero if native-admissible. The inherited exporter can separately exclude a terminally observable episode for provider/runtime/graph availability. Its `strict_successes` field counts admitted reward successes; use `endpoint_successes_including_excluded` or raw strict endpoints when reporting task performance. Recovered errors must not be silently equated with unavailable endpoints.
- Fixed low-LR SFT8 start was approved before the newly audited high-LR result. This review does not switch it. The48 readout slots concern exposed development compositions with fresh seeds, not new-source or deterministic-replay generalization.
- The numerical and native helpers are reused, not independently re-proven at every token. Existing native transient-retry capability and runtime availability limitations are unchanged. No new study-level retries are introduced.
- A real stage failure may prevent the final readout despite its normal-path reserve; preserve all planned denominators and pending/unrun NULLs. Parent outer timeout includes process imports; the internal clock starts on entry to `execute`. No runtime success or exact completion time is predicted here.

No scientific source change is requested by this review. MAIN retains acceptance, launch, cleanup and any separately approved recovery decision.
