# Literal-inspection instruction: the proposed behavior did not appear

The fixed paired comparison gives **7/32 →4/32 raw exact**, zero wins and three losses; all32 pairs are available. Both owners completed/released, and the sealed CPU audit rederived the cached and new raw finals, native decoding, scorer, checkpoint/source bindings and each arm's own frozen prefix. The root prefix intentionally changes by the approved instruction; it is not supposed to match the old prefix. Requested seed integers and all eight source contexts remain paired.

All32 new trajectories were manually adjudicated from their saved programs, observation order and native actions. **None shows request-list inspection before exact matching followed by use of the observed request.** This is an observable-behavior finding, not a claim about hidden cognition. No ambiguous positive inspection candidate remains: the only two observations containing actual request strings were generated after filtering on a preassigned literal and were never used for another selection.

| Context | Old G4 | Instruction G4 | Observed mechanism across all four draws |
|---|---|---|---|
| `fa62…` | 0000 | 0000 | Two clean assistant retrievals; two programs instead return the matched user request. No later inspection/use step. |
| `83e8…` | 0100 | 0000 | Three clean retrievals and copying errors; one unclosed first action executes no tool. |
| `4e5f…` | 0000 | 0000 | All four still use nonmatching request literals; each repeats or modifies failed bookkeeping, without inspecting requests. |
| `969a…` | 0000 | 0000 | All four retain the nonmatching literal; three then emit length-limited malformed retries, one repeats the failed tool. |
| `3bdc…` | 1111 | 1111 | All four retain direct correct retrieval and exact copying. No added inspection. |
| `6426…` | 0001 | 0000 | All four retrieve cleanly, then delete two genuine final spaces. |
| `0e42…` | 0010 | 0000 | Two clean retrievals with extra final LF; one new nonmatching literal, one unclosed first action. |
| `ff6b…` | 0000 | 0000 | Three clean retrievals with deleted final spaces; one first action stops without closing its tool block. |

Full record IDs, all32 coordinates/seeds, per-episode rationale and raw evidence hashes are in [MECHANISM_REVIEW.json](MECHANISM_REVIEW.json). Four draws per context are not32 independent context units. The new vectors contain one all-correct group and seven all-wrong groups: no mixed G4 reward group remains.

## Inspection, retrieval and copying are separate

The executed programs fall into four manually checked classes:18 preassigned-literal successor retrievals with clean stdout; nine nonmatching-literal failures; two wrong-role selections of the user request itself; and three trajectories with no executed tool.21/32 first programs and first action-token arrays remain exactly the same as their cached counterparts, despite the changed prompt. The remaining changes do not implement the proposed inspect-then-use sequence.

The two wrong-role programs append the matched user message's content instead of its following assistant response. Their stdout is the marker plus that already-selected user request; the final returns the request without the marker. Merely finding a request substring in such an observation would falsely credit inspection. These are not broad context dumps, and not successful evidence acquisition before selection.

Clean target stdout declines24→18. All six lost-clean trajectories were already raw-wrong in the control: two wrong-role outputs, one new bad literal and three unexecuted first actions. Separately, all three exact-score losses still have clean target stdout: one adds a final LF in `83e8…`/1, one deletes two final spaces in `6426…`/3, and one adds a final LF in `0e42…`/2. The14 new clean-stdout copying failures comprise six extra-LF outputs and eight deletions of two genuine final spaces. These native final differences are not normalized into wins.

The failed request-matching cases retain preassigned constants that have zero matches in the actual source user records. Extra attempts repeat those constants and change ordinal bookkeeping. Six new2048-token actions end in repetitive, unclosed tool blocks; a seventh unclosed block stops after209 tokens without its closing delimiter. All seven lack an executable completed tool call and a semantic final. Three occur before any tool execution; four follow a failed selector. They are recorded model errors scored wrong, not unknown/missing infrastructure outcomes.

## Cost and next decision

Both arms make66 physical root calls and zero child calls, with zero physical-call errors, start-only records or unknown-cost calls. Equal call totals hide changed behavior: the new run has fewer executed first tools but more failed retries. Input tokens69,717→71,347 (+1,630); output tokens21,111→27,319 (+6,208;29.4%). Owner time404.60→415.29s is descriptive, not a stable throughput claim. The seven malformed actions consume12,497 output tokens, without completing their proposed tools.

Retire this **single appended generic-instruction condition** on the exposed panel. It did not elicit the intended behavior, reduced clean retrieval and exactness, and increased token cost. Preserve it as a negative intervention result; do not sweep alternative wording over these same eight cases. This does not prove that an explicitly trained inspection policy is impossible, nor establish a new recursion/decomposition algorithm. No new SFT/RL step, checkpoint selection or rollout is authorized by this audit. The separately running fresh RLOO recipe changes both its batch and objective and remains a different comparison.

## Immutable evidence

- Primary [REPORT.json](REPORT.json): `453f6795e4b185f39ccf238ca62f14947be51e4b87d2449ea5018bf962cde14f`.
- Existing local raw [EVIDENCE.json](../../../../../ARTIFACTS.md): `003e02658a8cbe4101b0fda1b53413ecad24206ddccb5c2f288a6d4c63ce4be8`. Treat this as private raw material, not a publication artifact.
- Additive [MECHANISM_REVIEW.json](MECHANISM_REVIEW.json): `56d1a2ec78f8b8ed8b61ca74380b72496effd80550ec4e4b0457b41e013df928`.
- Analyzer CPU_READY: `3c78706686eec4924d25765abb84b90d3d26d37498c0648b291ff078b1514586`; source experiment READY: `575aaf1ebc3f27bd79f9da0673d3babefab373a403da992768c98abe5b173b3d`.

The additive review exports hashes, coordinates, classifications and whitespace edit codepoints—not private answers, source documents or generated-program text. All earlier PENDING receipts and primary metrics remain unchanged. No generated code was executed and no GPU/model call was made during analysis.
