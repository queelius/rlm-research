# Matched three-update helper readout



Reference T1/LR1e-5 checkpoint 3: 232/256 correct, 256/256 available; TREC 120/128, AG News 112/128.

LR10x T1/LR1e-4 stopped checkpoint 3: 228/256 correct, 256/256 available; TREC 117/128, AG News 111/128.

Paired observed outcomes favoring LR10x: 1 wins, 5 losses, 250 ties; 256 jointly observed.



Physical costs (reference/LR10x total tokens): 64962/65416; calls 64/64.



Context only: c32 SFT scored TREC 119 and AG News 112; reference step4 and T2 step4 each scored 120/112. Full raw-decoded records, changed IDs, availability, lineage, and source hashes are in REPORT.json.



Adaptive reused fixed256 panel; not fresh generalization.

Matched update count controls dose count, not parameter-distance or optimizer dynamics.

Unavailable predictions remain separate from wrong predictions; no checkpoint was selected using evaluation.
