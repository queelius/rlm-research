---
title: Fixed checkpoint-2 protected-readout audit method
date: 2026-09-10
status: frozen_before_scientific_content_read_but_after_terminal_file_existed
study: root-composed-rl-checkpoint2-readout-v1
attempt: outputs/attempt-002
planned_endpoints: 72
---

# Question and timing

Does the fixed, optimizer-ordinal checkpoint 2 change protected free behavior relative to the
already collected checkpoint 1 and starting policy? The V4 command began at
1789075280.4919283. While preparing this method I observed only that attempt-002 terminal and cost
filenames existed, with mtimes around 1789075283; I did not read their contents or any episode.
Thus this is not claimed as a preregistration or as frozen before generation. The comparisons and
metrics below are inherited unchanged from the prospective producer design and the earlier
RLVR3 audit.

# Terminal and native gate

Before outcomes, require one exact V4 `OWNER_TERMINAL.json` and MAIN's matching parent `EXIT.json`.
The EXIT completion-marker hash must equal the terminal hash; exit must not time out, the owner must
report release with no active service, and the parent must show an empty GPU. Authenticate V4 READY
identity `9070841dc21ff382456191296a0efba1a05c258e1a14a484ce7bd548f76cc9d0`,
READY SHA-256 `f4dce3c73177642ef4ad3cb44b31ee5c96cb809c2f42b52ee6e2ba0a0528e4a0`,
and the exact checkpoint-2 policy/state/owner pins recorded there.

Reconcile all 72 planned coordinates with export episodes and raw trace files. Verify exact source
coordinate, model dispatch (checkpoint-2 root and fixed c32 child), prompt/native IDs, ordered nodes,
authenticated final branch, and request-to-result correspondence. A returned, authenticated empty or
malformed final is an observed zero. An absent/unreturned/unverified final is NULL, never zero or
repaired. No generated code is executed.

# Fixed comparisons

Join checkpoint 2 by exact coordinate ID to the immutable 72-row checkpoint-1 and start exports.
Primary: checkpoint2 minus checkpoint1 over all 72 planned coordinates. Secondary: checkpoint2 minus
start. Report strict totals with conservative NULL bounds; known-pair wins/losses/ties/unknown; the
48 composed and 24 primitive strata; operator, scope, threshold, slot, and eight context clusters.
Also report each arm's marginal availability so conditioning on joint availability is visible.

For every available checkpoint-2 trace, inspect the actual root programs, child calls and tool
observations. Record child acquisition, complete-map retention, requested operator/scope/threshold
faithfulness, final use of observed state, strict correctness, zero-answer coincidence, and wrong-child
label diagnosis separately. This is an exhaustive agent trace review with reproducible retained
evidence, not a human-annotator study and not proof from scalar agreement. Trusted `qs_problem.py`
may diagnose child-label errors only after the actual observed labels are fixed; it cannot repair or
rescore the model response.

# Physical cost and limitations

Union actual `rollout/role-audit/*-request.json` and `*-result.json` records independently of RESULT
availability. Parse usage only from authenticated `native_wire_response.body`; absent fields remain
unknown, and local provider billing is not inferred. Report root/child calls, HTTP/choice outcomes,
input/output/cache tokens, service/capture/owner elapsed time, and the failed attempt-001 zero-request
environment entry separately. The panel and seeds are research-exposed, checkpoint doses are only
0/1/2, and a single paired seed does not establish a smooth learning curve.
