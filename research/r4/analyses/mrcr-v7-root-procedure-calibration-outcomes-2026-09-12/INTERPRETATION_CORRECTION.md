# Interpretation correction: V7 versus short32

Short32 is a **composite feasibility screen**, not a representation-only ablation. Relative to V7,
it changes the source dataset, underlying conversations, context lengths, target questions/answers,
and external representation. Therefore a better short32 result cannot be attributed specifically to
JSON structure.

The actual selected short32 source is a top-level JSON array of ordered message objects with exactly
`role` and `content` keys. For the first selected document, the eight messages comprise five user
and three assistant messages. The root receives only neutral file type/size metadata; no target
needle, relevant position, parser hint, or gold-derived statistic is added.

If short32 exposes the same linkage failure, a future identifying comparison should keep the same
short tasks and exact JSON bytes in both arms. The intervention arm may add a neutral preview stating
the top-level type, keys/value types, that ordered user/assistant messages form conversation records,
and how boundaries are represented. It must not name a target keyword, ordinal, relevant record,
gold content, or answer-derived statistic. All task IDs, policies, seeds, sampling, budgets, scorer,
and failure taxonomy remain matched.

Training-method nuance: prospectively filtered behavior cloning or rejection-sampling SFT from
successful **training** trajectories is legitimate when its selection rule, denominator, failures,
and collection costs are retained and heldout/evaluation examples or checkpoints are not
cherry-picked. The concern is outcome-driven evaluation selection, not predefined train-only
filtering as a method.
