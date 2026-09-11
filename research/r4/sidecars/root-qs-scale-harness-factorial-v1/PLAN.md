# Launch handoff

MAIN may launch only after `python owner.py verify` succeeds and serialized GPU ownership is granted.
The owner uses one A100, four native workers, 180 seconds per endpoint, no training, no retry, and writes
to the unused fixed namespace `outputs/attempt-001`.

The two root services run serially in the frozen order `sft6`, then `unchanged`. Each service includes
startup and bounded release in its 1,710-second share. The common clocks are 3,420 seconds of service
work, 3,570 seconds owned including final harvest, and a 3,600-second parent cap. A failure is retained
in place and never replaced.

