# Query-sensitive RL independent audit method

Timing: frozen during window 2 collection, after campaign launch at 2026-09-09 22:28:18.701 UTC
and before this auditor read any training reward, admission, loss, optimizer, or held-out outcome.
Only process/file-name existence and the fact that window 1 had produced generation/result filenames
were observed. This is a source-informed live audit closure, not a prospective preregistration.

Provenance guard: this campaign was approved after relevant earlier outcomes existed. Any
`declared_at` or `outcomes_consulted` fields inherited through `RECIPE.json` describe the older
numerical recipe, not preregistration of this outcome-informed query-sensitive campaign.

Frozen question and inventory: six trained operator/scope cells, three held-out cells, unchanged
low66c root and fixed c32 child; 12 candidate windows × 24 slots = 288 planned training endpoints;
48 fixed readout coordinates × unchanged/trained = 96 finals. The 48 readout inputs comprise 36
held-out-cell and 12 supported-cell pairs over 12 contexts (eight size 16, four size 32).

Audit rules:

1. Recompute every host answer from public records plus sealed host labels and verify train/readout
   group disjointness, query truth tables, zero prevalence, equality diagnostics, model-visible file
   fields, and absence of host gold from prompt/runtime artifacts.
2. For each candidate window, distinguish endpoint availability/reward from stricter complete native
   graph admission. Authenticate export provenance, mixed-within-task selection, masks, root-only
   credit, TIS/PPO values, trainable token mass, and input hashes. An unavailable endpoint remains
   NULL; a returned wrong/malformed final is zero.
3. Reconstruct the candidate-window cursor and actual Adam cursor. Each committed checkpoint must
   advance weights and persistent Adam state exactly once from its predecessor. A homogeneous,
   unadmitted, incomplete, or partial window may advance only the candidate cursor and must not be
   described as an optimizer step. Preserve no-ops, partial attempts, stops, and committed-on-stop
   evidence.
4. For every materialized training/readout trace, authenticate binding, fixed child, first prompt,
   native request/completion tokens and logprobs, final branch/finish route, and strict score. Inspect
   generated code/observations without executing it. Credit actual operator/scope reduction only
   when trace data flow uses acquired/current state; separate direct reasoning, reacquisition,
   incomplete map coverage, loops, and accidental scalar agreement.
5. Primary readout: conservative planned-denominator correctness and NULL bounds, paired trained
   wins/losses/ties/unknowns, held-out versus supported, size 16 versus size 32, and per-context/
   operator/scope summaries. Contexts, not endpoints, are the highest independent units; size 32
   confounds new composition with length.
6. Report actual root/child request and token costs for training, optimization, and each readout.
   Keep endpoint availability, operational-success sensitivity, replayed accounting, service time,
   and provider billing distinct. No source, service, queue, or GPU mutation is authorized.
