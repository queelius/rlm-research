# Direct OOLONG reward audit v1

## Finding

Across all 88 immutable traces, the stored official rewards replay exactly. The
official scorer marks 27 traces exact, while the task-aware final-answer
parser marks 13. There are 14 official-exact but
strict-false episodes (51.9% of official exact rewards), zero false negatives,
and all
14 format-contaminated rewards are 2,048-token length truncations.
They occur only at source IDs 12000006, 12000008, 12000029, and 12000031.

Heldout policy v0 and v4 are unchanged under both views: official exact is
2/8 -> 2/8; strict exact is
1/8 -> 1/8. The official 2/8 result at each
version contains one genuine formatted answer and one truncated gold mention, so the defensible
heldout exact result is 1/8 at each version with paired delta +0.

## Training-batch attribution

Each of the four admitted optimizer batches has one unique match to its recorded eight-episode
reward mean, truncation mean, output-token mean, completion time, and complete four-rollout groups.
Under that reconstruction, admitted format-contaminated episodes = 0. This
is a conservative aggregate reconstruction, not direct shipment lineage; `audit.json` preserves
the exact groups, traces, matching status, and candidate counts. Contamination is present in
buffered/non-admitted training traces and both heldout evaluations, even though it is not found in
the four reconstructed admitted batches.

## RLVR implication

Reward must be gated by a schema-complete task-aware final answer. A gold substring anywhere in
reasoning is not evidence of task success, and an unparsed/truncated terminal response should be
invalid or excluded before advantage construction. Numeric partial rewards are reported separately
as intentional official shaping on valid formatted answers; an exact-only RLVR objective should
binarize correctness only after successful parsing. This single run cannot support a learning
claim because strict heldout success is unchanged and the official outcome is reward-contaminated.
