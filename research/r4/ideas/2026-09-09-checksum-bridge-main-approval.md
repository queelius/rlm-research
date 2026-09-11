# MAIN decision: test whether record correspondence helps the whole RLM

Approved September 9, 2026, 16:27 UTC, before preparation or outcomes for this
comparison. User delegates research decisions; no user response is required.

Implement the 32-episode scalar-checksum amendment in
`2026-09-09-correspondence-to-rlm-checksum-amendment.md`
(SHA256 9542fb49bade8ce2566723b38c20c356de1ee9800cb4dea0c060ca5c61d0e63a),
not the superseded first-match task. Use a new immutable scientific namespace,
`sidecars/root-child-representation-bridge-v1`.

Question: does preserving record identity in a child model's generated output
improve an unchanged root model's final answer? Compare array and ID-map child
generation, normalize only the broker's returned value to the same canonical
map, and keep the root-side interface identical within each task. Preserve raw
sampled tokens, probabilities and native graphs. The intervention changes the
child prompt and allowed output together; it is not an attention probe.

Use the four specified exposed development contexts, fixed low-SFT8 root and
c32 child, two new seeds and balanced paired order. Freeze count and numeric-ID
checksum tasks and whole-answer scoring prospectively. Report checksum as the
primary task and count separately. A checksum can miss colliding subsets and
can fail because of root arithmetic even when child labels improve.

Keep all 32 planned coordinates, observed failures and unavailable results
distinct. Report actual child uptake, eligible batch sizes, correspondence,
coverage, returned-evidence-to-answer fidelity, and native costs. Small batches
or too few eligible paired calls are limited exposure, not a refuted mechanism.
Do not force plans, insert gold answers, repair malformed output, or select
contexts based on outcomes. Use the proposed 1800-second outer envelope with
shared work and cleanup limits, and check the remaining allocation at launch.

CPU preparation and focused causal-seam fixtures run alongside existing GPU
work. MAIN alone accepts and launches. If the native broker projection cannot
be implemented faithfully in a bounded sidecar, report the concrete blocker
and prepare a simpler comparison; do not mutate live or frozen runtimes.
