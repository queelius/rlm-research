# Six-family recursion-interface qualifier

This is an additive, no-update qualifier for the prompt/API failure observed in recursion-headroom attempt 002. It is not a replacement result and does not estimate recursion benefit.

The frozen panel contains one task from each of J1, J2, M1, M2, T1, and T2, drawn by an outcome-independent family/context mapping from six distinct research-exposed protected contexts already present in the original 24-task panel. Each task is run once in both modes with its original attempt-002 sampling seed, QS6 root, c32 child, temperature 0.5, and 2,048-token call cap. Both modes receive byte-identical user text. That text specifies the full conditional ABI: the callable is already global when advertised, the model must not import it, `request_for` constructs the child prompt, `reply.answer` is passed to `strict_map`, and no-child episodes solve from the unchanged raw files.

One capture specification has one environment depth, so the existing qualified runner cannot interleave modes without twelve separate collector lifecycles. The bounded implementation therefore uses one service and two six-task blocks in frozen order: no-child, then enabled. Pair IDs and source seeds match across modes, and order is reported as a limitation.

The 250-request value is an admission-stop trigger, not a hard cap; in-flight requests may overshoot. Ownership is hard-capped at 600 seconds and the external command at 700 seconds. There are no retries, answer fallbacks, loop guards, training updates, or prompt repair during execution.

The preregistered gate requires zero `from rlm import rlm` attempts, no consecutive identical Python action, at least 10 of 12 observable endpoints, all six families in both modes, and exact typed/role request parity by the semantic `request_id` stored in each audit—not audit filenames. Operational completion and scientific gate passage are reported separately.
