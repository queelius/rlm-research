# FinQA demonstrations: usable syntax improves; operand selection remains weak

The independent audit has **zero discrepancies** across all32 native requests, checkpoint/template prefixes, decoded replies, canonical/raw hashes, provided-target grades and costs. All32 calls returned normally, all usage is known, and the owner completed/released in60.037s. Scores remain unchanged: direct **1/16**, DSL **3/16**, with3 DSL wins,1 loss and12 both-wrong pairs. These are16 context units, not32 or64 independent questions.

Relative to the same16 zero-shot controls, DSL validity rose0→7/16 and literal `#i` placeholders fell13→0. Direct validity stayed16/16. This is **in-context demonstration**, not weight learning. Five programs still contain self/forward references; table-access errors and one boolean-as-number error remain. The original static taxonomy does not enumerate those latter dependencies, so the [all16 inert case review](MECHANISM_REVIEW.json) records them separately without changing any evaluator or score.

## All four primary-score disagreements

| Case | Direct | DSL | Mechanism |
|---|---|---|---|
| IP2005 debt change | Wrong: returns308 | Exact2022 | Faithful2330−308 using requested years. |
| LMT2012 profit growth | Wrong:0 | Exact.01881 | Faithful(1083−1063)/1063 with usable `#0`. |
| ABMD2007 lease share |54.4%, below exact precision | Exact.54429 | Sums both totals and breakdowns:15338/28180. Both rows double, so cancellation preserves the correct ratio. Correct answer, but not clean operand selection. |
| PM2014 dollar-note issuance | Exact2000 | Invalid row lookup | Direct answer matches500+750+750; its internal arithmetic is unobserved. DSL still cannot address repeated face-value rows by its chosen whole-row operation. |

The first two DSL wins are genuine requested arithmetic, not noisy-label or scale fixes. The third is target-correct through a shared duplication factor; do not count it as evidence that whole-row aggregation is generally faithful. The direct win is source-supported and not annotation-driven.

The other12 pairs were also inspected, not discarded. Valid-but-wrong programs mix years/components, choose2006 rather than2005, or combine the wrong expense quantities. A source-value-presence diagnostic can mislead:2200 and2000 are valid conversions from public2.2/2.0billion, despite a false literal-presence flag; their sum is wrong because the requested casualty addend was omitted. Numeric presence is neither source identity nor faithfulness.

Annotation limitations persist unchanged. Direct16.61% still matches the December2005 S&P value, while the official target uses January2005. Gas versus crude-oil target mismatch, revenue-percent versus level mismatch, and net-income versus operating-expense ambiguity remain. None becomes a repaired target or excluded case. Every primary label remains in the16-case denominator.

## Cost and one next question

Natural cost is one call per answer in either arm, not token-matched. Direct used20032 input/139 output tokens; DSL24768/636, totaling45575 tokens. Compared with zero-shot42046 total tokens, the larger demonstration inputs outweighed shorter completions. Summed call times are not elapsed wall time.

**One worthwhile next run, if GPU budget remains:** a fresh16-page replication of this exact two-example direct-versus-DSL condition, using the next16 distinct page filenames in the existing revision+ID hash ranking after excluding the original pages. Freeze that rule before outputs; retain all annotation flags with no gold/outcome filter. Reuse the same demonstrations, interpreter, paired seed slots, base checkpoint,T=.5,384 output,8192 context and service. This is32 calls, roughly one minute at the observed runtime—not another prompt variant or training job.

The question is whether usable grammar and the two faithful arithmetic wins recur on unseen-by-this-campaign page contexts, rather than whether another repair can raise scores on the exposed16. Report strict accuracy, valid DSL, source-grounded arithmetic and all failures together. With only four discordant pairs here, neither general superiority nor a novel decomposition method is established. No follow-up was implemented or launched by this analysis.

Artifacts: [independent native proof](../../../../../ARTIFACTS.md), [unchanged-label comparison](COMPARISON.json), [all16 adjudications](MECHANISM_REVIEW.json). Comparison SHA `a0983659d9d7622b9aed65a61ffee057a3b780bc33754a74d58016cc0376026f`; native proof SHA `daf449499a172d4528f7d22f2ac741df1eb6e930df7ed8b911e09d6ed2ff9103`; original RESULT SHA `f9bd927aa2899b969e619d742d758980872b97886406787723d6e567f54439e2`.
