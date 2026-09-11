1. Recompute the frozen diagnostic gates from persisted vectors and exact result hashes.
2. Stop before GPU if any new engineering gate fails.
3. Invoke the immutable V1 sparse trainer on the exact old group/checkpoint once.
4. Authenticate Adam1 to Adam2 and all checkpoint files; no evaluation in this owner.
