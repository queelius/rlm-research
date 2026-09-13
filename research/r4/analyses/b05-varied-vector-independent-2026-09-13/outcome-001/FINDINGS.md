# Varied vector64: usable, sparse local contrast; whole-token boundaries

The independent saved-native audit found **zero issues**. All64 planned outputs were available and full-length literal-boolean JSON, with no unknowns or malformed vectors. Exact complete sets:33/64; mean per-attempt BA0.852683; TP396/FP29/FN28/TN123 over576 repeated candidate decisions (144 unique candidates,16 contexts,G4). Width6 contributed30/32 exact; width12 contributed3/32. These are training rollouts, not evidence of training improvement or a comparison against another panel.

Every actual prompt, physical token prefix, seed, sampling/model binding, native completion ID/log-probability record, parsed/raw response hash and grade was checked. Public transforms and disjoint generation were independently reconstructed for all16 train and12 pre-frozen held contexts. Held generation was not run. Actual cost:116,308 input+1,214 output=117,522 tokens; output11–46 tokens; all64 stop normally; owner67.013s.

## Contrast retained across every group

Six of16 groups vary at11 of144 candidate positions, giving44 nonzero candidate-action RLOO advantages out of576. Joint BA varies in those six groups (24/64 nonzero action advantages); joint exact varies in only three (12/64). The independent diagnostic uses candidate correctness minus the other three samples' mean; this is not a chosen training loss or class-balancing contract.

| Root | Width/history | Exact/G4 | Varying positions, zero-based | Nonzero local action advantages |
|---|---|---:|---|---:|
| root_f98585cb708789 | 6/1 | 4 | none | 0 |
| root_80b031692d7b74 | 6/1 | 3 | 2,3 | 8 |
| root_7af77d61fdcb80 | 6/1 | 4 | none | 0 |
| root_c6f3d7721ad840 | 6/1 | 4 | none | 0 |
| root_cad29474572c4b | 6/3 | 4 | none | 0 |
| root_b9793fdd64bd8b | 6/3 | 4 | none | 0 |
| root_dc29bbe9570c21 | 6/3 | 3 | 1 | 4 |
| root_326df977fa228b | 6/3 | 4 | none | 0 |
| root_222ecef3cfd04e | 12/1 | 0 | 1,10 | 8 |
| root_d7fad122ad5bde | 12/1 | 0 | none | 0 |
| root_cd5359418db6a5 | 12/1 | 0 | none | 0 |
| root_e748d8e26ebb44 | 12/1 | 3 | 6,8 | 8 |
| root_5072e2052d1561 | 12/3 | 0 | 1,8 | 8 |
| root_42bee96c14222d | 12/3 | 0 | 1,10 | 8 |
| root_fa42b509b187e5 | 12/3 | 0 | none | 0 |
| root_6f565c8a6598be | 12/3 | 0 | none | 0 |

The three variable but zero-exact groups show why exact-only feedback misses useful changes. BA already detects those changes, so this is not evidence that local credit uniquely recovers otherwise invisible reward. Local credit instead avoids assigning the same nonzero aggregate advantage to unchanged decisions. All six variable groups also contain unchanged candidate decisions. Six groups are always exact; four are always wrong with no candidate variation. Of57 erroneous candidate actions,21 occur at varying positions and36 repeat at static positions. No group or zero-advantage action was filtered.

## Native-token feasibility, not character-exclusive credit

All576 candidate values map to **one distinct native token each**, with no token intersecting two decisions. The literal-character spans are unambiguous, but518 tokens include inseparable preceding punctuation or whitespace:

| Decoded token text | Count |
|---|---:|
| `true` | 40 |
| `false` | 18 |
| ` true` | 137 |
| ` false` | 63 |
| `,true` | 248 |
| `,false` | 70 |

Thus all64 rows are span-qualified but zero rows have exclusively boolean-character tokens. The feasible contract credits the **whole native token overlapping one decision**, including its leading comma/space. It must not re-encode, split token log-probability by character, or claim structural characters receive zero credit. Other structural/EOS tokens remain outside those decision spans. This file creates no mask, loss or optimizer.

## Checkpoint note review

Read-only review of `docs/research-checkpoints/2026-09-13-decision-interfaces-and-record-grouping.md` found no material numerical/scientific error against the three independent reports. Small future clarifications: singleton's two false positives are the same low-quality candidate in both repeats, and its independent audit has now passed. Published primary scores stay unchanged.

Evidence: [REPORT.json](REPORT.json), SHA256 `394f0d7035ccea378ecd23605c54b3218c49ada80956afa27037d45c21abdd01`; source run RESULT `41056161d571322eb6aebe4efbb80a0b399ba65e6f703160af34c5a8d8a32164`. Full hashes and narrow interpretation are in [MECHANISM.json](MECHANISM.json).
