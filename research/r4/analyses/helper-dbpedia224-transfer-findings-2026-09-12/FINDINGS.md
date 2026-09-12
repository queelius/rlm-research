# DBpedia transfer: essentially unchanged

All four fixed models returned 224/224 available labels in 56/56 valid four-record calls, with qualified runtime and clean release. No endpoint or seed was chosen from these outcomes.

| Fixed model | Correct / 224 | Accuracy | Owner seconds |
|---|---:|---:|---:|
| c32 | 209 | 93.30% | 213.31 |
| rl_step8 | 209 | 93.30% | 246.65 |
| sft_step8 | 208 | 92.86% | 223.26 |
| rl_seed2_step8 | 210 | 93.75% | 211.05 |

| Before → after | Wins / losses | Labels changed | Wrong → different wrong |
|---|---:|---:|---:|
| c32 → rl_seed2_step8 | 1 / 0 | 1 | 0 |
| c32 → rl_step8 | 0 / 0 | 1 | 1 |
| c32 → sft_step8 | 0 / 1 | 1 | 0 |
| rl_step8 → rl_seed2_step8 | 1 / 0 | 1 | 0 |
| rl_step8 → sft_step8 | 0 / 1 | 2 | 1 |
| sft_step8 → rl_seed2_step8 | 2 / 0 | 2 | 0 |

All four agree on 222/224 labels. RL seed1's only c32-relative change remains wrong; seed2 corrects that OfficeHolder item. SFT introduces one Village error. These two items explain all variation; article text is not reproduced.

| Gold class (16 each) | c32 | RL seed1 | SFT | RL seed2 |
|---|---:|---:|---:|---:|
| Album | 14 | 14 | 14 | 14 |
| Animal | 16 | 16 | 16 | 16 |
| Artist | 14 | 14 | 14 | 14 |
| Athlete | 16 | 16 | 16 | 16 |
| Building | 14 | 14 | 14 | 14 |
| Company | 14 | 14 | 14 | 14 |
| EducationalInstitution | 16 | 16 | 16 | 16 |
| Film | 16 | 16 | 16 | 16 |
| MeanOfTransportation | 16 | 16 | 16 | 16 |
| NaturalPlace | 15 | 15 | 15 | 15 |
| OfficeHolder | 15 | 15 | 15 | 16 |
| Plant | 16 | 16 | 16 | 16 |
| Village | 16 | 16 | 15 | 16 |
| WrittenWork | 11 | 11 | 11 | 11 |

Every arm used 60,945 input tokens (36,832 cached); outputs were c32: 4294, rl_step8: 4291, sft_step8: 4300, rl_seed2_step8: 4292. All usage fields were available. Training cost is separate.

Decision: do not promote AG-trained RL as broad helper capability transfer or meaningfully superior to SFT. DBpedia is almost invariant across these fixed endpoints. The released-base reference will distinguish recovery of pretrained skill from improvement beyond base; different cache/LoRA settings preclude a matched-cost interpretation.

Scope: fourteen balanced classes, sixteen records each; uncertainty units are 56 shared B4 requests. Local holdout is not pretraining exclusion. No whole-RLM/delegation capability was measured. The source audit contains inherited fresh512 wording; the actual verified DBpedia denominator here is 224, and panels are not pooled.

Reproduce with `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python derive.py --check`. FINDINGS.json retains source/model/response hashes without raw articles or full native calls.
