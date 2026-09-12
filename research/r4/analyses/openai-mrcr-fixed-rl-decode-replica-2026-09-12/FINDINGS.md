# The fixed-baseline RL gain did not replicate

The new decoding block gives **cp32 25/32 → fixed-RL 22/32**, with zero wins and three losses. All64 planned arm-trajectories were available, both owners completed and released, and the independent raw-token/scoring audit reported no integrity errors. This is evidence against presenting the earlier23→25 result as an established improvement. It is not enough to claim population-level regression either.

The same16 exposed contexts now have two decoding blocks, each with two seeds per context. Earlier:23→25, two wins in two contexts. Replica:25→22, three losses in two other contexts. A descriptive repeated-panel total is48→47 across64 trajectories per arm, with two wins and three losses; **there are still16 context units, not64 independent examples**. This replicates decoding only, not training, the dataset, or the update seed. The earlier long-panel result remains10→10/16 and was not rerun here.

## Every changed path, not just score changes

All32 first physical prompt/action token arrays match across the two models.27 complete native paths and finals are identical. Five paths change, in three contexts. Parsed programs and tool observations match in31/32 pairs; the exception is an already-failing episode that performs extra unsuccessful tools. Nothing here shows improved retrieval.

| Context / repeat | Exact cp32→RL | Native mechanism | Extra completion tokens |
|---|---:|---|---:|
| `omrcr-72618dd842efffd0a22e` /0 | 1→0 | Identical correct program, clean target stdout and final-decision prompt; RL adds exactly one terminal LF. | 0 |
| Same context /1 | 1→0 | Same one-LF copying error. | 0 |
| `omrcr-85610b95bf89de2580a6` /1 | 1→0 | Identical correct retrieval; RL adds exactly one terminal LF. | 0 |
| `omrcr-746d5e1512abdfa38878` /0 | 0→0 | Same failed literal selector and error observation; a16-token wrong final becomes a2048-token, length-limited unclosed tool block with empty semantic final. | 2032 |
| Same context /1 | 0→0 | Same failed literal selector, followed by two additional failed ordinal-rewrite tools. The wrong request literal is retained; the final remains wrong. | 399 |

The three loss finals are bare semantic native spans: no reasoning or tool framing, native content equals the stored root final, and both arms finish with stop. Their RL outputs equal the full gold string plus one LF. This is genuine model-added whitespace, not a renderer/harness trim defect or truncation. Equal completion-token counts do not mean equal output: tokenization can encode the added LF without increasing the total count.

The two still-wrong paths matter operationally. Both first selectors have zero exact normalized matches in the actual source user records. On repeat1 the extra tools alter ordinal bookkeeping and then set ordinal1, rather than inspect the actual request string; they still produce errors. On repeat0 the parser records `UNCLOSED_BLOCK` at the2048-token limit. These are recorded, available wrong outcomes—not missing calls or unknown scores. Changed weights affect post-error behavior even though the update was described as final-decision training.

The first divergence in all five cases occurs after the same first action and first observation. This locates the observed behavioral change. It does not isolate which gradient component or Adam-transformed parameter changes caused it, nor imply a clamp-only intervention.

## Cost and decision

Physical calls rise64→66; prompt tokens70,634→73,829 (+3,195); completion tokens20,739→23,170 (+2,431; about11.7%). All added prompt/output cost comes from the two still-failing repeats. The three correctness losses add no tokens. No child calls, call errors, start-only records, orphan returns or unknown usage were reported. Owner wall time424.32→396.36s is not evidence of lower policy cost: the RL arm used more calls and tokens, and throughput varies. The already-completed one-step training cost remains separate:43.74s science /56.20s owner; no new training occurred for this replica.

Recommended claim: **one final-decision update changed terminal behavior, but its small initial gain was not reproduced; copying and failed error recovery remain bottlenecks.** Downgrade the fixed-baseline recipe from “improvement” to an unstable exploratory result. Do not select a dose, checkpoint or prompt from these outcomes. Any gradient-component follow-up should answer a specific mechanism question, not assume the full update is beneficial.

The forthcoming fresh RLOO run changes both the rollout batch and the objective. Its readout can evaluate that new joint recipe; it is not an isolated RLOO-versus-fixed-baseline test. Literal-input inspection is a separate, predeclared harness intervention and does not retroactively explain this update's terminal effects.

## Evidence and privacy

[RESULTS.json](RESULTS.json), SHA `4acb6a0458cada24767690fefaa656cc52ff74bdd2fd76ff5336952e9ad0e33a`, preserves the independent primary audit. [MECHANISM.json](MECHANISM.json), SHA `29449df42af302badcd876a7684915d1626b92ea76fae05781a805964168c5f2`, inventories all32 pairs and all five changed paths, native turn hashes/statuses, exact whitespace edit operators, episode links and source hashes. The336 primary source pins were reverified before the additive audit. The earlier readout SHA is `4ac83a409099ca5af87d6f433e0872041e7ef5779c71378d5c1a21fff6473e85`.

The new artifacts export no raw private answer, document or generated-program text. Non-whitespace changes are represented only by bounds, lengths and hashes; exact whitespace edits use codepoints. Original private traces remain in their existing locations. No generated code was executed, no model was called and no previous metric or artifact was rewritten.
