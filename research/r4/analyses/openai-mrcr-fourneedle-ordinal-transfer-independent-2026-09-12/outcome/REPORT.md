---
schema: openai-mrcr-fourneedle-ordinal-transfer-independent-report-v1
status: COMPLETE_RAW_AUDIT
---

# Four-needle ordinal-transfer readout

Base returned 0/16/16 raw-exact;
checkpoint 32 returned 10/16/16.
Across 16 jointly available context units, checkpoint 32 had
10 wins and 0 losses; 
0 pairs remain unknown.

| Requested occurrence | Base exact/available | Checkpoint 32 exact/available | cp32 wins/losses | Unknown pairs |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 0/8 | 5/8 | 5/0 | 0 |
| 4 | 0/8 | 5/8 | 5/0 | 0 |

## Physical evidence

| Arm | Native returned/errors | Root calls (prompt/completion tokens) | Child calls (prompt/completion tokens) |
| --- | ---: | ---: | ---: |
| base | 52/0 | 52 (140417/14417) | 0 (0/0) |
| checkpoint32 | 31/0 | 31 (33106/10880) | 0 (0/0) |

Mechanism fields separately record exact clean-target stdout, terminal copy success/failure,
first-program literal-request matching, and a conservative ordinal-mention heuristic. They are
descriptive trace evidence, not proof of internal retrieval or correct ordinal selection. Generated
programs were parsed as inert text and never executed. The secondary metric is the official
marker-gated SequenceMatcher similarity. This is same-task ordinal transfer, not a new benchmark.
