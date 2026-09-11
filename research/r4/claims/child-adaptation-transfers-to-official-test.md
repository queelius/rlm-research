---
id: child-adaptation-transfers-to-official-test
status: strong_exploratory_component_result
updated_utc: 2026-09-10T18:46:16Z
question: Does child-model fine-tuning improve classification beyond its optimizer corpus?
scope: six_class_TREC_child_only
evidence:
  - sidecar: leaf-adapter-by-granularity-v1
    report: analyses/leaf-adapter-by-granularity-live-2026-09-10/REPORT.md
    exposure: child_optimizer_exposed
  - sidecar: leaf-trec-test-adapter-granularity-v1
    report: analyses/leaf-trec-test-adapter-granularity-live-2026-09-10/REPORT.md
    audit_sha256: 1953a24a9e5cd8988b599e8ad5d0d36f4d712f42944853fe604a7e9aee817ebc
    report_sha256: ba8b83e92af1afcedcd912e1e10ca10b1bb442d4c97e7659b1a3174a527479c7
    main_adoption: analyses/leaf-trec-test-adapter-granularity-live-2026-09-10/MAIN_ADOPTION.json
    exposure: optimizer_disjoint_but_489_of_500_previously_research_evaluated
planned_native_calls: 148
verified_native_calls: 148
null_native_calls: 0
---

# Fine-tuning improved the model that handles individual records

The small child model learned a useful classification skill that transfers beyond
the questions used to update its weights. On all500 official TREC test questions,
its label accuracy improved from64.0% to84.5% with100-record batches and from71.7%
to88.5% with16-record batches. Both comparisons used the same base model, with
or without the fixed trained adapter, and two fresh paired sampling seeds.

| Batch width | Base, correct /1,000 | Trained, correct /1,000 | Gain |
| --- | ---: | ---: | ---: |
| 100 records | 640 | 845 | 20.5 percentage points |
| 16 records | 717 | 885 | 16.8 percentage points |

Each denominator counts500 source records twice, once perseed; it is not1,000
independent questions. Every one of148 requests returned a verified complete
map. The gains have the same sign for bothseeds. MAIN replayed the frozen native
reader on all148 calls, checked481 evidence pins without mismatch, and recomputed
the totals. It is a replay of the same parser, not an independent implementation.

## Why this matters to the RLM

The controller can perform the right calculation and still give a wrong answer
because a child mislabels a record. That happened in10 trained-controller examples
in the original question-sensitive study. Improving child semantics is therefore
a concrete way to address a demonstrated bottleneck. This leaf-only comparison
does not measure whether the complete RLM improves.

## Important limits

None of these500 normalized groups occurs in the actual5,065-group optimizer
corpus. However,489 had already been evaluated in this research project; this is
not a pristine unseen benchmark. The11 that overlap raw training source files
were excluded from the optimizer. No source rows were removed from this test.

The label errors are correlated within batches and the two seeds reuse records.
The gain is not universal across classes: the small abbreviation stratum worsens
at16-record width. The frozen adapter was not selected using this result, but
there is only one training realization. TREC's cached redistribution license is
unspecified; no permission to redistribute source data is inferred.

## Next question

Does a better child translate into more correct, actually-performed composed
answers when the controller and harness are held fixed? Use new paired calls
under both child weights, preserve all tasks and failures, and measure actual
root calculations as well as final answers. A separate query-conditioned child
interface could ask only for distinctions needed by the current calculation;
that is a new hypothesis, not an established benefit.
