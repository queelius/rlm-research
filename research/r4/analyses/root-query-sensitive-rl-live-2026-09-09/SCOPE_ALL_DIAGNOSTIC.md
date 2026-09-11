# Scope-all wording diagnostic

Observed at 2026-09-09 22:48--22:53 UTC, after window 4 completed. This does not alter the
frozen campaign.

The structured query encodes scope `all` as users `[u0, u1, u2, u3]`, intending all records across
the four users. The exact frozen count prompt begins: **“Among records belonging to all four users,
a record qualifies when its question category is 'numeric value'. Count qualifying records.”** The
weight prompt substitutes “Sum the visible record weight values of qualifying records.”

Multiple native traces read this wording as an intersection:

- count-all repeat 4, coordinate
  `7e0a85c89170378c12713c1a0e7a787a36fa9c4f6f179eb30eb67d4f0beb9b7c`: “Since each record
  belongs to exactly one user, there cannot be any record that belongs to all four users
  simultaneously.”
- count-all repeat 2, coordinate
  `3a585dc39ae021edd78e4f1c85c8e7c7138a9311debfa198445a8ebe80de4fd6`: “identify which records
  belong to all four users (u0, u1, u2, u3).”
- weight-all repeat 7, coordinate
  `18eab77270553d86907a8d17d0de36f75d85a0b5af2b0a8e79d0a4adcdde0bfb`: “records that are
  shared among all four users.”

These are short excerpts from authenticated, already executed native responses. This is a genuine
linguistic ambiguity, not a scorer or source-authentication failure.

Consequently, supported **count-all** and **weight-all** training behavior and held-out
**distinct-all** readout are confounded by scope interpretation. Count-single, count-union,
distinct-single, distinct-union, weight-single, and weight-union are not affected by this wording.
The campaign continues unchanged: no endpoint is rescored or excluded, and every strict output
retains its declared place in the primary planned denominator.
