---
schema: helper-base4b-ag512-dbpedia224-design-v1
status: CPU_PREPARATION
gpu_launch_authority: MAIN_ONLY
---

# True-base reference on the two frozen transfer panels

## Question

Did the broader AG-News adaptations merely recover competence lost when the original
Qwen3-4B-Instruct-2507 was specialized into c32, or do they improve beyond that released base?

No exact true-base result exists for the frozen official AG test 512 or DBpedia test 224. The
existing released-base control used an older fixed 256-record panel. There, c32 scored 112 and the
base 113 on AG News (four c32-to-base wins, three losses), while c32 scored 119 and base 92 on TREC
(one win, 28 losses). Thus the old evidence is +1 AG but -27 TREC for base, and cannot answer the
new-panel question.

## Frozen comparison

One newly started true-base service evaluates the exact already-sealed AG512 schedule (128 B4
calls) followed by the exact DBpedia224 schedule (56 B4 calls). Request token IDs, schemas,
sampling settings, coordinate IDs, and seeds equal each corresponding c32 request; only the model
alias changes to the real no-adapter endpoint. Raw request and response bytes are saved before
normalization. Missing or invalid calls remain unavailable.

This arm supplements rather than replaces the four fixed c32/RL8/SFT8/RL8-seed2 arms. It was
specified before any base query on either panel.

## Runtime boundary

The true-base service necessarily has `enable_lora=false` and `enable_prefix_caching=false`; the
four adapted endpoints used LoRA and prefix caching. The owner requires the same batch-invariant
kernel marker and exact pre-exec environment attestation, but this does not make runtime cost or
outputs bitwise matched. Report accuracy and paired semantic outcomes; do not claim matched cost.

The owner cap is 900 seconds, external cap 1000 seconds, with no optimizer or root calls. Success
requires all 184 calls/736 records, exact binding, actual kernel marker, and clean release. A partial
run remains evidence but has no primary denominator accuracy.

