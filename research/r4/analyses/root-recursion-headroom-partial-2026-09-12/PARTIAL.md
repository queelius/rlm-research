# Root recursion headroom: raw first-repeat diagnostic

## Decision

Do **not** interpret attempt 002 as a clean estimate of the benefit of recursion. The first matched repeat is usable as a protocol diagnostic, but both arms are dominated by Python/protocol failures and accumulated-context overflow. The remaining 48 planned episodes were never attempted after the 600-request admission trigger; they are budget-censored, not wrong answers.

The smallest useful next run is a 12-episode interface qualifier, not a higher-budget replay of all 96 episodes. Use six prospectively fixed tasks covering all six families, one repeat, and both modes. Give both modes the same explicit conditional instruction: if the system advertises `rlm`, call the already-global callable directly with `await rlm(...)` and never import it; otherwise solve from the raw records. Keep raw access, model bindings, temperature 0.5, seeds, and the 2,048-token per-call cap fixed. A 250-request admission trigger and 600-second owned cap are grounded in the observed mean of 14.15 physical calls per episode (679/48). Promote only if there are zero bad imports, zero repeated-identical-action loops, at least 10/12 observable endpoints, all six families are represented, and typed/role audits match by semantic request ID.

## What actually completed

Both first-repeat blocks completed all 24 tasks. No-child consumed 342 root requests in 301.0 seconds; enabled consumed 312 root plus 25 child requests in 368.9 seconds. The attempt stopped at 679 requests before block 2, an overshoot of 79 beyond the admission trigger. The two blocks contain the same 24 `pair_id`s and repeat 0.

Endpoint results on the fixed 24-task denominator were:

| Mode | Correct | Observed wrong | Unavailable | Valid schema | Invalid schema |
|---|---:|---:|---:|---:|---:|
| No child | 1 | 16 | 7 | 7 | 10 |
| Enabled | 4 | 12 | 8 | 6 | 10 |

Only 12 pairs have observable endpoints in both modes: enabled has 2 wins, 0 losses, 1 both-correct, and 9 both-wrong. Another 12 pairs have at least one unavailable endpoint. Those counts are descriptive, not a 24-independent-pair significance test: tasks share eight context clusters, and missingness is substantial and mode-dependent.

## Why request use exploded

This is not mostly long, successful reasoning.

- No-child made 318 Python tool calls; 251 produced error outputs. One episode made 91 model requests and repeated the identical syntax-invalid statement 89 times. Across the arm, 165 tool calls duplicated code already attempted in the same episode.
- Enabled made 290 Python tool calls; 195 produced error outputs. The system explicitly says the callable is already global, yet all 15 enabled episodes that entered multi-turn reasoning attempted `from rlm import rlm`. This produced 135 `ImportError`s; 138 bad imports were attempted. Only 25 genuine child calls occurred. Within-episode duplicate code accounts for 207 calls.
- Seven episodes per arm ended with provider failure when the accumulated decoder prompt exceeded the service's 8,192-token limit. Enabled had one additional setup/runtime-or-trace failure.
- Reported prompt usage reached 1.358M tokens in no-child and 1.340M across enabled root+child calls. This is the cost signature of error accumulation, not evidence of productive depth.

No-child is also intrinsically harder than the familiar root readout: it must infer all needed TREC labels from 16 raw questions and then perform the reduction. It is not artificially denied the raw context, definitions, users, or weights. Still, its ten schema-invalid observed endpoints and error-heavy traces mean the present score cannot isolate legitimate leaf-classification difficulty from control failure.

## Prompt/protocol identification issue

This attempt did not preserve the QS6 training/readout user prompt. For all selected tasks, the old prompt explicitly said the root could use Python and `await rlm(prompt)` and described the request/decoder contract as optional. The new shared prompt removes that clause and says only that the runtime system message truthfully states whether recursion is available.

The enabled system message itself is correct: it says to call the already-global `rlm` directly. But the changed user prompt moved the policy off its demonstrated protocol. In the earlier real-helper48 diagnostic under the old prompt, this same starting policy used `await rlm`, `request_for`, and `strict_map` in all 48 episodes, never attempted `from rlm import rlm`, recorded no trace errors, and used 230 physical requests total. The current behavior therefore reveals material sensitivity to decomposition-interface phrasing. It does not establish that recursion lacks headroom.

## Raw audit status

The owner terminates with `typed/role physical request audit inventories differ`, but that check compares filenames from two different identifier namespaces. Read-only recomputation finds exact semantic `request_id` parity for all 342 no-child and all 337 enabled requests. Both block exports are complete and have no export integrity failures; the service receipt says all owned processes exited and ports are free. The final audit bug should remain recorded, but it does not invalidate the first 48 raw episodes.

If the 12-episode interface qualifier passes, a one-repeat 24-pair run should use at least an 800-request admission trigger and a 1,200-second owned cap: the observed 48-episode matched repeat needed 679 requests and 715 seconds. A second repeat should be a later decision, not silently bundled into that repair.

Exact machine-readable counts, hashes, and scope limits are in `PARTIAL.json`.
