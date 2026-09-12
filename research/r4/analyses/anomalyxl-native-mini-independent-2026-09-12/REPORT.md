# Independent AnomalyXL native mini audit

Owner terminal complete: **True**; runtime qualified: **True**; released: **True**.

The frozen inventory contains 20 episodes: 10 direct/Python pairs, two rows in each of 5 official precise families. Independently recomputed official primary means are direct **0.0916** and Python **0.0000**; paired Python-minus-direct mean **-0.0916**.

## Per family

| Family | Direct | Python | Paired delta |
|---|---:|---:|---:|
| classify_with_evidence | 0.0000 | 0.0000 | +0.0000 |
| lead_lag_with_magnitude | 0.0000 | 0.0000 | +0.0000 |
| localize | 0.1992 | 0.0000 | -0.1992 |
| localize_all_channels | 0.0000 | 0.0000 | +0.0000 |
| measure_magnitude | 0.2586 | 0.0000 | -0.2586 |

Wrong, invalid, failed, and unattempted episodes are separate in `RESULTS.json`; partial official credit is also retained.

## Physical evidence

- direct: 10 physical calls, 60516 prompt tokens, 897 completion tokens, 0 request errors.
- python: 14 physical calls, 4786 prompt tokens, 5796 completion tokens, 2 request errors.
- Engineering: 2 calls; exact Python sum6 and final JSON sum6 qualification passed.
- All returned raw token IDs, usage counts, finish reasons, unique provider IDs, decoded texts, and model identity were checked against response wires. Service release receipt is present.

Direct retained mean 1.9141% of original points (range 0.0885%–2.9480%); Python had full rounded arrays. Any advantage therefore mixes information access and computation, not pure reasoning superiority.

Python's three inspection calls are forced for every successful episode; there is no adaptive stopping. There is no recursion or RL in this pilot. The frozen panel contains 0 category-specifically defined no-anomaly rows under the documented rule; this composition was inspected only after outcomes.

## Next decision

Do not start RL. First repeat a larger frozen mini with identical access/budgets or test one deterministic full-data summary control; this ten-pair outcome is too small for optimization.

This Qwen3.5 direct baseline is not comparable to earlier c32/Qwen3-4B task results. The ten-pair result is exploratory, not a TimeRLM reproduction.
