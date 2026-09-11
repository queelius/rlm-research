# Mixed-size training changed behavior but did not make64-item answers reliable

September9,2026. Exploratory analysis of completed runs, not a promoted research
claim. No outputs or scores have been repaired. The two new runs start from the
same original controller adapter as the earlier five-item SFT; "original" does
not mean an untouched pretrained base model.

## Main result

| Training examples contain this many questions | Actual updates | Training seconds | Fixed five-item test | Usable64-item arrays |64-item generation hitting token cap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Five only, earlier selected child |128 |705.625 |473/489 |0/6 |6/6 |
| One, five, sixteen or thirty-two (A) |206 |1151.455 |477/489 |0/6 |5/6 |
| One, five, sixteen or sixty-four (B) |204 |1142.028 |476/489 |0/6 |0/6 |

All three trained models return98/98 valid five-item test arrays. Both new runs
see the same5065 training groups twice and use the fixed final second epoch,
without choosing checkpoints from these test outcomes. They are matched on source
records and exposures, not exact update counts, target-token totals or compute.
The earlier child's checkpoint was selected on validation before its test.

A does not show a reliable jump from32-item training support to64-item use.
B explicitly practices64-item arrays and changes its stopping behavior: every
output is syntactically valid JSON containing only canonical label strings, but
the lengths are62,58,62,57,62 and58. None provides one answer per input record.
B uses1504 generated tokens across these six outputs; the matched old HF probe
uses6144. Shorter generation is not useful completion when records are missing.
The small test differences of three or four items are not a replicated advantage.

## Diagnostic, deliberately separate from successful operation

The strict aligned score is zero when the whole array is unusable. That does not
mean every generated label is semantically wrong. An additive script reads the
complete canonical JSON strings already present at the beginning of each output
and compares the first64 by ordinal position. It never inserts a missing string,
closes a bracket, changes an alias, or substitutes this result for the primary score.

| Training | Positions1–16 | Positions17–32 | Positions33–48 | Positions49–64 | Total diagnostic correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| Earlier five-item child |94/96 |37/96 |22/96 |20/96 |173/384 |
| A |95/96 |65/96 |39/96 |17/96 |216/384 |
| B |95/96 |64/96 |44/96 |13/96 |216/384 |

Available complete strings cover384,380 and359 of the first384 positions,
respectively. In A's final quarter only92/96 are available; in B's,71/96.
The later position scores can mix classification errors with skipped-record
misalignment. Ordinal agreement cannot prove the model intended that record.
The matched HF inputs are physically identical across these three checkpoints;
the six contexts contain384 distinct source groups, reused from development
composition work. There is one greedy output per context, not384 independent trials.

This is a modest diagnostic signal that varied-size training changes where the
model deteriorates, not proof of a solved interface. The exact-cardinality/schema
and record-correspondence tests are the next informative comparisons.

## Interpretation limits and next decisions

1. The final64 evaluation intentionally matches the old HF probe's physical
   prompts. Tool-object key order differs from the training serializer. Semantic
   messages/tools are the same, but this remaining formatting generalization
   demand means we should test exact training-template inputs before attributing
   B's failure solely to insufficient64-item learning. A fresh B-only paired
   twelve-call replay is being prepared; no outcome is assumed.
2. The queued original/old/A/B free-versus-schema64 comparison separates output
   cardinality from within-array correspondence. A forced64-element answer can
   still attach the wrong labels; the earlier child already demonstrated this.
3. The queued SST-2 task changes the task and label vocabulary. It tests broader
   transfer or interference, not pure label renaming or general reasoning.
4. Do not change the running root RLVR campaign based on these leaf outcomes.
   It uses the old selected child throughout and asks a separate control-learning
   question. Its automatic successor will evaluate all four fixed leaf checkpoints.

## Provenance and timing

- A RESULT SHA12ed81d4f88124ec400b35c5c563ef919f61a83ca501ca78bf9ff1a103bedfe6;
  adapter SHAe822c841b78ac448c7860f5e3e7a7053cfce68c57f4a1d8f5584e1c728b35531.
- B RESULT SHA4b638e8ca7335c2c17cde296d54435c8221092dc1256dc65b78ef2bfb1820f60;
  adapter SHA59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200.
- [Reproducible diagnostic](../../../../ARTIFACTS.md#unpublished-files "Not published: analyze.py"), [all three outputs and source hashes](../../../../ARTIFACTS.md#unpublished-files "Not published: A-B-versus-old/DIAGNOSTIC.json").
  The earlier A-only diagnostic remains intact at`A-versus-old/DIAGNOSTIC.json`.
- B started automatically00:01:35. The coordinator detected its completed exit
  and started root RLVR at00:25:36 UTC. Optimization accounts for about19minutes
  of B's approximately24-minute workflow; loading, validation, testing and saving
  account for the remainder. Future RL elapsed time primarily includes generating
  fresh multi-turn experience, not just the short parallel gradient calculation.
