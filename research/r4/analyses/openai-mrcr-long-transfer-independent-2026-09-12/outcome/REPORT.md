---
schema: openai-mrcr-long-transfer-independent-report-v1
status: COMPLETE_RAW_AUDIT
---

# Procedural-SFT long-input transfer

Base returned 0/16/16 raw-exact; checkpoint32 returned 10/16/16. Across 16 jointly available coordinates, checkpoint32 had 10 wins and 0 losses; 0 pairs remain unknown.

This is a fixed one-shot comparison over 16 context units. The source selection excluded 48 prior short rows and has zero exact core-pair or bidirectional target-to-other-core overlap within the selected cohort. Base pretraining exposure remains unknown.

## Physical evidence

| Arm | Native returned/errors | Root calls (prompt/completion tokens) | Child calls (prompt/completion tokens) |
| --- | ---: | ---: | ---: |
| base | 51/0 | 51 (100388/14560) | 0 (0/0) |
| checkpoint32 | 32/0 | 32 (34352/11431) | 0 (0/0) |

Mechanism categories distinguish exact clean target observations, clean-target copy failures, exact answers without an exact target stdout, and wrong finals without exact target stdout. They are trace descriptions, not causal proof of internal retrieval. Generated programs were never executed by this analyzer.
