# Root campaign live snapshot

State: in_progress; snapshot2026-09-09T00:41:28.884606+00:00.

| Stage | Recorded/planned | Native candidate successes | Export status |
|---|---:|---:|---|
| validation-00 | 8/8 | 2 | complete_authenticated |
| round-01/collection | 32/32 | 12 | complete_authenticated |
| round-02/collection | 26/32 | 10 | pending |
| validation-02 | 0/8 | pending | pending |

Missing/pending/censored coordinates are not negatives. Native candidates remain provisional until export admission; recovered provider errors do not erase completed outcomes.

Round1: checkpoint_committed; actual Adam[1], root tokens23130, delta0.147623.
Round2: pending_no_committed_update.

validation-00: audited root/child calls14/43, action tokens3627/3140; root/child length stops0/1.
Recursive usage in6 recorded episodes; structured/executed tool calls6/6; first-action classes{"empty_content": 2, "structured_ipython": 6}.
Provider-error events0, recovered-error completed episodes0, overlength heuristic episodes0; admitted invalid terminals2.
Export authority: strict successes2/8, admitted outcomes8; exclusions{}; unavailable-group reasonNone.

round-01/collection: audited root/child calls70/372, action tokens25261/51582; root/child length stops1/14.
Recursive usage in21 recorded episodes; structured/executed tool calls109/109; first-action classes{"empty_content": 10, "structured_ipython": 22}.
Provider-error events0, recovered-error completed episodes0, overlength heuristic episodes0; admitted invalid terminals13.
Actual mixed-group credit: {"advantage_values": [-1.7320508075688774, -1.0, -0.5773502691896258, 0.5773502691896258, 1.0, 1.7320508075688774], "child_or_observation_credit_tokens": 0, "episodes": 28, "group_id": "205944413bd055fcbf05ed29b777abea6207f53ef71363bc40f938add16af254", "root_action_tokens": 23130, "turns": 63}.
Export authority: strict successes12/32, admitted outcomes32; exclusions{}; unavailable-group reasonNone.

round-02/collection: audited root/child calls50/144, action tokens15557/9887; root/child length stops1/3.
Recursive usage in15 recorded episodes; structured/executed tool calls24/24; first-action classes{"empty_content": 8, "structured_ipython": 18}.
Provider-error events0, recovered-error completed episodes0, overlength heuristic episodes0; admitted invalid terminals8.

Prior pilot2/8, unchanged replay4/8, post2/8 is separate-seed trajectory-noise context, not pooled/matched campaign control. Two updates and fixed8 are exploratory; do not infer general learning or complete recursive coverage.

Detailed coordinate outcomes, role calls/tokens/errors, mixed group eligibility and hashes are in METRICS/AUDIT. No GPU/network model requests or input mutations.
