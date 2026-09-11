# Recovery execution plan

- Execute the same 40 direct-statistics requests as v1 under a new campaign/output path.
- Derive each episode's required call IDs from frozen PLAN membership.
- Missing/unavailable required ID yields NULL; authenticated malformed yields observed-invalid.
- One A100, four workers, 90-second call cap, 1,200-second inclusive owner cap.
- MAIN alone launches; no retry, fallback, reroll, root call, or training.

