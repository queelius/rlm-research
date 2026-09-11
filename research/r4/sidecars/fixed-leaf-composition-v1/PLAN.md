# Implementation plan

Use the parent's explicitly assigned external sidecar as isolation; no repository/worktree
or live-source changes. Existing experiment helpers are read-only.

1. Add focused tests for frozen coordinate/batch mapping, exact request parity/no gold,
   whole-array versus item scoring, cancellation and infrastructure/null distinctions.
2. Implement additive data/selection binding and direct HTTP runner by reusing frozen
   leaf72 make_request/score/usage/write-once helpers; no GPU or live preflight during prep.
3. Freeze the independent spec and request hashes, validate the actual parent composition
   manifest and selected checkpoint, and run focused CPU/mock-transport checks.
4. Publish READY with the explicit parent-owned binding/server-dir launch command.
   Runtime service identity remains a launch-time check; do not label a stale alias live.
