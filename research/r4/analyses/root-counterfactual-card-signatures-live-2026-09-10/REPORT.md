# Counterfactual-card96: process uptake survives, practical promotion does not

The card produced genuine requested computations in **5/48 planned P endpoints versus 0/48 U**,
including two correct computations on the altered counterfactual tasks. But it did not improve the
original strict score (5/24 in both U and P), improved the counterfactual strict score only from
1/24 to2/24, and sharply reduced counterfactual native availability from18/24 to10/24. The frozen
promotion gate fails: counterfactual P availability is below U, only two rather than four added
faithful computations occur, and both are in one rather than three contexts. This supports limited
prompted procedural headroom, not robust counterfactual composition or card efficacy.

The experiment author froze METHOD `a5ad9a67…` before generation. This independent reviewer adopted
it after launch but before reading outcomes (`REVIEWER_ADOPTION.md`), having previously reviewed the
implementation and contributed to reused project audit conventions. MAIN's terminal relay preceded
outcome reading. All96 available/wrong/NULL endpoints are retained; all61 available traces were
semantically reviewed. No sampled code was reexecuted and no missing answer was repaired.

## Native primary result

| Cell | Correct/planned | Native available | Observed wrong | NULL | Missing-answer bounds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original U |5/24|19|14|5|[5,10]/24|
| Original P |5/24|14|9|10|[5,15]/24|
| Counterfactual U |1/24|18|17|6|[1,7]/24|
| Counterfactual P |2/24|10|8|14|[2,16]/24|

The observed planned P−U difference is0 on original and+1 on counterfactual. Treating every NULL as
operational non-success, original has3 P wins,3 U wins and18 ties; counterfactual has2 P wins,1 U
win and21 ties. These are **not** 24 fully observed pair comparisons: only10 original and8
counterfactual pairs are jointly available. Native missingness is neither random nor ignorable.

Original context effects improve in3/8 parents, decline in2 and tie in3. Counterfactual improves in
only context02, declines in context05 and ties in six. Both counterfactual faithful successes occur
in context02. Only six of24 four-cell signatures are fully available. Among same-arm signatures
where both variants return, both variants are strict-correct for1/16 U and0/8 P; the U signature is
not faithful operator evidence.

Zero support remains sparse: original has four and counterfactual six zero-gold blocks. Strict
zero/nonzero counts are U2/3 versusP1/4 on original and U1/0 versusP1/1 on counterfactual. The
counterfactual +1 is therefore not robust evidence of a broad accuracy change.

## What actually executed

`EVIDENCE.json` retains every available sampled program/observation, raw path, requested parameters,
classification, and the last code fragments supporting review. Host scalar agreement did not assign
faithfulness. Five endpoints form an authenticated full child map, execute the requested operation
with the actual scope/category/threshold, print the observed scalar, and return that scalar:

- original P context00 counts per-user human-being weight totals greater than5 and returns3;
- original P context03 groups numeric-value weights by user, takes the maximum and returns10;
- original P context01 counts per-user entity totals greater than5 and returns1;
- counterfactual P context02 groups location weights by user, takes the maximum and returns7;
- counterfactual P context02 counts per-user location totals strictly greater than the **actual
  changed threshold7** and returns0.

All five are dataset-correct; none is a faithful-wrong leaf-semantics case. P therefore has three
faithful original and two faithful counterfactual computations, while U has none. There is no
faithful completed conditional-weight computation. The counterfactual tasks use their actual frozen
changed category/threshold/weights; threshold5 was not inherited into the threshold7 row.

The other eight strict successes are coincidences or alternative computations: two pooled-category
sums happen to equal maximum/conditional golds, two unconditioned B sums happen to equal conditional
golds, one wrong-scope two-stage conditional happens to equal gold, one literal reconstructed map
counts individual records above5 rather than users whose totals exceed5, and two unsupported/pooled
zeros match zero gold. A P maximum row samples the correct grouping form after four overwritten
width4 maps, then hard-codes five record texts; this is literal observation recovery, not live-map
binding. It returns4 rather than gold8 and is not counted faithful.

Every other available final uses a pooled target/B weight, Boolean pooled threshold, wrong scope or
category, same-record intersection for mutually exclusive labels, incomplete map, or unsupported
manual zero. Three unavailable P traces contain a recognizable requested operator form but never a
valid requested computation: context records are treated as labels (threshold), an incomplete map
loops during maximum, and invalid child parsing loops during maximum. They remain NULL diagnostics,
not salvaged successes. Thus the card changes some procedures, but not reliably enough to support
the practical gate.

## Availability and physical work

The35 NULLs are17 retained episodes that exhaust the bounded tool route without a native final,
17 endpoint timeouts after a final root request is rejected at8241–8633 prompt tokens (>8192), and
one timeout with no HTTP400 after18 returned root calls and8 child calls. The HTTP400 split is
original U2/P3 and counterfactual U4/P8. Recorded-no-final split is original U3/P7 and
counterfactual U2/P5. P therefore has12 capped/no-final traces versus5 U, and11 over-context terminal
requests versus6 U. These are policy-loop outcomes. The card's extra initial context and changed
trajectory can contribute, but this audit does not identify a single cause for the paired
availability difference.

| Cell | Root / child / all physical | Choice completions | Known input / output / cached tokens | Unknown usage calls |
| --- | ---: | ---: | ---: | ---: |
| Original U |214 /62 /276|274|804854 /28678 /770080|2|
| Original P |198 /58 /256|253|646878 /25663 /601952|3|
| Counterfactual U |195 /33 /228|224|699213 /22143 /661856|4|
| Counterfactual P |301 /105 /406|398|1221135 /41432 /1159264|8|
| **Total** |908 /258 /1166|1149|3372080 /117916 /3193152|17|

All1166 physical attempts have HTTP receipts;17 are HTTP400 without choice completions. All1149
choice completions pass token/native rendering checks. All61 claimed native finals match typed and
physical provider identity, exact returned tokens/logprobs, final branch and reply; there are no
native-auth errors or physical records outside planned endpoint directories. Unknown usage is not
zero. HTTP400 attempts are not established GPU generations, and provider billing/FLOPs are unknown.

The actual fixed24 adapter and c32 child bindings match the frozen study. Full first prefixes,
model/tool contract, prompts/files and actual source IDs are pinned in `NATIVE_AUDIT.json` and the
frozen input receipts. Counterfactual records/query parameters differ by the preselected GATE; they
are not a weights-only intervention. All eight parent contexts are research-exposed.

Owner completed and released in1495.977267s; `OWNER_TERMINAL.json` SHA-256 is
`876894e90a3b9893d06dbfa07ab203b94a6298f59684cedf74fe77064906b874`. Parent exit0 at
1789037650.6044195 after1496.469301s; the next job launched3.242s later. No rerun or service remains.

## Decision

Do not promote this card under its frozen practical gate, and do not treat counterfactual2-versus1
as persuasive learning evidence. Retain the narrower result: on an exposed targeted panel, the same
short procedure can induce five authentic requested reductions—including two with altered
parameters—where U induces none. The availability loss and absence of conditional success are
strong counterevidence.

This does not condition or invalidate the independently motivated SFT72 curriculum. The next useful
analysis is whether that broader curriculum improves faithful operator/scope execution and
availability, not another post-hoc card wording. Any future card replication needs a context/loop
control and genuinely new context clusters.
