# AG helper credit and SFT signal audit

This audit uses only the two saved128-action AG training collections and committed
SFT checkpoint losses. It does not open the frozen heldout512 inputs or outputs.

## What the sampled maps say

Seed1 produced403/512 correct item decisions. Ten of32 B4 groups were always
4/4, fourteen were always3/4, three were always2/4, and only five had different
correct counts across their four actions. Seed2 produced402/512: nine groups were
always4/4, thirteen always3/4, four always2/4, and six count-mixed. Consequently
only20/128 and24/128 sampled sequences respectively received nonzero count-RLOO
advantages.

Item-level inspection does **not** recover hidden contrast in these collections.
Exactly five seed1 and six seed2 item positions vary in correctness, one in each
already count-mixed group. No constant-count group swaps which item is correct.
For every action, summed leave-one-action-out binary item advantages equal the
correct-count advantage (maximum floating error `1.67e-16`). Thus replacing the
scalar count reward by the sum of four item rewards is mathematically the same
estimator here and activates zero additional groups. A genuinely different arm
would have to localize each item's advantage to that item's label tokens or change
the request unit—not merely rename the reward.

The two fresh draws are also highly concentrated:117/128 decoded maps are
byte-identical and119/128 have the same correct count. Only two mixed contexts
overlap; the union is nine of32. This supports the narrow conclusion that sparse
within-prompt reward contrast, not missing arithmetic in the count reward, limits
these two one-step batches.

## What the SFT checkpoints say

SFT completed all eight committed updates on1,024 unique train records in236.25
owner seconds (224.44 seconds inside training), with20,591 supervised target
tokens. Only1,536 tokens (7.46%) overlap the inner category text; the rest are
IDs, JSON syntax, and end tokens. At step1 the label tokens averaged NLL0.504 and
accounted for21.7% of loss mass, versus structure NLL0.146. By steps6–8 structure
NLL was0.0033/0.0006/0.0008 while label NLL remained0.466/0.458/0.520, so the
remaining loss mass was91.9%/98.5%/98.2% label-associated despite labels being a
small token fraction.

These are disjoint examples at every step, not repeated-example learning curves;
the changing label NLL cannot be interpreted as a before/after improvement.
Likewise loss mass is not gradient contribution, because no separate label and
structure gradient sweeps were run. The safe reading is that the full-vocabulary
objective rapidly makes structure easy and eventually concentrates residual loss
on semantic labels; the fresh512 endpoint is still required to say whether that
changes decisions.

## Next decision

If both the broader eight-step RL endpoint and SFT endpoint are null, do not spend
the next GPU slot on another helper temperature/LR knob or on "per-item reward"
that still sums to the same sequence advantage. Prefer repairing and rerunning the
already frozen MRCR root-procedure calibration: it directly tests the component we
actually want to train, has an exact task-level verifier, and admits a root-only
update only if fresh groups show at least two mixed rewards and real context
inspection. The present MRCR failure was missing `/context.txt` during setup and
contains zero model evidence, so this is a harness qualification rather than a
repeat of a negative model result.

If SFT improves while broader RL does not, then one narrowly paired helper test
becomes warranted: share one fresh action batch from the same c32 parent, compare
the existing full-sequence correct-count RLOO gradient with an item-label-local
gradient, and keep optimizer/denominator/evaluation fixed. That asks whether credit
placement—not data learnability—matters. It must be newly qualified because the
current actions establish neither unbiased token-local credit nor a gain. If
broader RL improves, replicate its endpoint on fresh train/evaluation seeds before
redesigning credit.

Machine-readable counts and exact source/output hashes are in `RESULTS.json`.
