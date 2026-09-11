# Execution plan

- Question: does exposing the public J1 sufficient statistics outperform full six-class maps?
- Inputs: exact eight exposed episodes and all 40 ceiling chunks/seeds/orders.
- Calls: 40 new direct-statistics calls, four workers, 90-second call cap.
- Compute: one A100, 1,200-second inclusive outer cap; no root calls or training.
- Control: reuse the sealed 40 full-label ceiling calls once; do not reexecute.
- MAIN alone may launch after READY review.

