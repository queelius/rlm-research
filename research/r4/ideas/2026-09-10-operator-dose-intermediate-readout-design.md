---
id: operator-dose-intermediate-readout-v1
date: 2026-09-10
status: prospective-design-only
implementation: not_started
gpu_launch: not_authorized
---

# Where does the SFT6-to-SFT24 behavior change occur?

## Recommendation

Run one 64-endpoint free-behavior study: exact checkpoints 6, 12, 18, and 24 on the same 16
precommitted coordinates with one new paired seed per coordinate. All four checkpoints must be
sampled now; the historical SFT6/SFT24 outputs are context, not paired controls. Repeating fixed24
also tests whether the large sealed effect survives new sampling. This is more informative than a
12/18-only bridge because the earlier run had 23/96 NULLs and a new seed could otherwise be mistaken
for a dose transition.

The panel uses all 12 existing context clusters: two coordinates from each of four source-prepared
clusters and one from each of eight exposed-repeatability clusters. It has 8/8 source strata,
operator counts 5 count / 6 distinct / 5 weight, scope counts 5 all / 5 single / 6 union, and 13
nonzero / 3 zero gold answers. Membership was chosen after the prior outcomes existed, so this is not
outcome-blind; however, the frozen algorithm used only context, operator, scope, gold-zero stratum,
coordinate ID, and a fixed hash—never prior model results. Exact IDs and the selection digest are in
the YAML companion.

## Measurements and inference

Primary metrics are planned-denominator native availability and strict `Answer: N` correctness at
each checkpoint, plus paired 6→12, 12→18, and 18→24 wins/losses on jointly available coordinates.
Preserve every missing/unrun slot as NULL with bounds; a genuine malformed or wrong final is zero.
No answer repair or sampled-code reexecution.

Mechanism metrics are equally necessary: endpoints with an actual child request, complete observed
label maps, final equality to an independent reduction of those returned labels, executed displayed
scalar, clean stopping, and root-versus-child error attribution. Multi-call traces must distinguish
real map accumulation from overwrite or literal recovery. A decreasing teacher loss is not evidence
for any of these behaviors.

- If checkpoint12 already resembles the new-seed checkpoint24 and both beat6, the transition is at
  or before 12; if 18 resembles24 while12 resembles6, it lies between 12 and18.
- A graded monotone rise supports a dose response. A nonmonotone pattern, broad pairwise ties, or a
  failed fixed24 repeat makes stochastic/panel variation the leading explanation.
- This small exposed panel locates a candidate threshold; it does not replace a genuinely new-context
  replication and must not be used to choose a “best” checkpoint retrospectively.

## Teacher-first probes

Keep all 12 fixed teacher-prefix probes at every checkpoint (48 secondary calls). They share the
already-running service stages and are cheap relative to free execution. They map syntactic
`await rlm(...)` reachability but execute nothing and cannot demonstrate acquisition or reduction.
Cap probes at 60 seconds per stage; if that cap binds, retain probe NULLs and protect the 480-second
free-behavior window. The prior 24 probes used 31,981 known input+output tokens, so doubling them is
unlikely to dominate a study whose prior full readout used about 1.89 million known tokens.

## Runtime and controls

Serve the four exact adapters serially in hash-ranked order `sft18, sft24, sft12, sft6`; rotate the
16-coordinate dispatch list by four positions per stage. This reduces simple dose/time and
coordinate/tail alignment but cannot remove the serial-service confound. Use four workers, 180
seconds per endpoint, the unchanged released base, c32 child, native role/tools, 2048 action tokens,
8192 context, temperature 0.5, and the qualified existing readout transport. Per stage reserve up to
180 seconds startup, 60 probes, 480 free collection, and 30 cleanup. Cap work at 3,150 seconds,
ownership at 3,270, and outer time at 3,300. Expected one-A100-40GB use is about 24--35 minutes at
roughly the prior 34 GB peak; the cap is 55 minutes. No partial checkpoint, reroll, or performance
selection is allowed.

The continuation lineage is the exact same 72-trajectory corpus and Adam chain. Exact adapter,
config, and state hashes are in the YAML companion. Seeds `981681101`--`981681116` are shared across
all checkpoint arms; probe seeds `981681201`--`981681212` are likewise paired. The named local
input/READY/SEED_AUDIT scan ended 2026-09-10T04:51:52Z and found no collision for those values or
master seed `981681001`. This is a named-catalog result, not a claim of global novelty.

## Ledger clarification

The interim 53-child-call figure counted only the 42 SFT24 endpoints having retained RESULT files.
The final physical ledger counts 75 calls across all 48 planned endpoints: the six missing-RESULT
directories contain 22 additional calls (1, 2, 1, 1, 2, and 15). Thus 53 + 22 = 75; neither count
was a scoring denominator.
