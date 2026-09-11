# Count-answer distributions: a small interpretation check

CPU-only descriptive check of frozen host answers, September9,2026. No model
requests, raw episode rescoring or changes to active training/evaluation. BROAD16
final transfer outcomes have not been read for this check. This is not a new
preregistered primary endpoint or an automatically competitive deployed baseline.

The two earlier root-training comparisons share12 task answers, repeated at two
seeds for24 cases per policy. None has a zero answer. The most frequent answer
occurs twice, so even an evaluation-informed best single constant reaches only
4/24; always zero reaches0/24. The observed selected-policy15/24 and16/24 therefore
are not explained by simply outputting one constant on this evaluation. This does
not rule out category/context-specific shortcuts, exposure or count cancellation.

The broader campaign intentionally includes two zero-answer tasks among48
training task groups. Its16-record people-count group in round1 is one of them;
that explains why a CPU fixture returning zero can be correct there. It does not
mean the old positive transfer results were zero-answer tasks. There are no zero
answers in the eight broader validation tasks.

An important prospective caveat for final transfer: the three abbreviation-count
tasks have answers1,1,0. Guessing one would solve two of the three task questions
(four of six seed repeats), without semantic inspection. Preserve this imbalance
and report the reserved-description and reserved-abbreviation breakdowns alongside
the frozen combined reserved-target endpoint. Do not label an abbreviation gain
as general new-category reasoning without this context. These categories were
already known to the fixed child; only requesting them of the root is reserved.

METRICS.json retains every split's unique-task histogram, zero count and
evaluation-informed best constant. Its constants inspect each evaluation's gold
and are explicitly descriptive, not trained/selected on a disjoint development
set. Seed repetition scales the same answers, not source diversity. A count task
can legitimately be correct despite canceling item errors; no new evidence-coverage
condition or reward penalty is introduced.

Exact sources and SHA256 identities are in METRICS. The independent-seed transfer
host-gold file has the same1cb7e891… hash as the original transfer file. Existing
positive root reports remain immutable and linked from the main analysis index.
