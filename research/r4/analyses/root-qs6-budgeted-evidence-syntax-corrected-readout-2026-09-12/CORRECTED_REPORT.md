---
title: Corrected syntax-interface readout
date: 2026-09-12
status: complete_call_free_reauthentication
---

# The syntax example reduced invalid actions but worsened observed endpoints

This additive audit re-authenticates the original48 saved episodes against the
exact condition-specific prompts frozen before generation. It makes no model
calls and does not replace the preserved all-unavailable export.

Under the inherited endpoint semantics, plain is C/W/U =
5/17/2
and syntax is 2/19/3.
Among the24 matched pairs, syntax has 1 win,
4 losses, 15 ties and
4 unknown pairs. Returned finite-horizon `stop` or
`length` responses count as observed failures when they are not exactly correct;
only provider/unreturned outcomes remain unavailable.

The stricter action-interface result is plain C/W/U =
3/2/19
and syntax 0/0/24.
Syntax has 0 usability wins and
5 losses. The syntax arm never aligned a strict
final with its accepted local `finish()` state; plain did so five times.

The original raw comparison's useful secondary count remains35→8 rejected API
actions. That lower syntax-error count did not translate into better endpoints.
Two plain and three syntax requests exceeded the8192-token context limit and are
the five remaining unavailable outcomes. Both arms used only physical root calls;
saved-map `classify` callbacks were logical local calls, not child inference.

This is an exploratory result on two familiar, research-exposed contexts. It does
not establish generalization, causal evidence use, or live child-compute savings.
