# Adaptive root RLVR: live independent audit

Status: **terminal: stopped after seven updates; audit complete.** See the [final report](REPORT.md), [terminal metrics](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_METRICS.json"), [terminal details](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_DETAILS.json"), and [source/analysis seal](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_MANIFEST.json").

The eighth generation had one all-correct task and one all-wrong admitted task, so neither supplied a mixed-reward group. The frozen no-reroll rule stopped the campaign. Validation at update four is unchanged at 2/8; validation/transfer eight were not run. No fixed-final-eight benefit can be estimated, and checkpoint seven is not substituted. All 128 training rollouts were collected; 95 episodes contributed 68,008 root-action tokens to seven updates. The following sections preserve earlier milestone context.

This is an outcome audit, not a new experiment or launch authority. [Main method](METHOD.md) and [auditor method/independence boundary](AUDITOR_METHOD.md) were written before this auditor opened outcomes.

## Four-update readout

Strict validation remains **2/8 → 2/8**, with one win, one loss and six ties; all eight trajectories are admitted. Syntax validity rises 3/8 → 5/8, but full query-relevant map coverage stays 5/8. The win changes a bare `0` into `Answer: 0`; the loss changes a correct strict answer into correct-number explanatory prose, which the frozen contract rejects. This is not evidence of a validation benefit.

All eight paired first-root physical token arrays and complete sampling dictionaries match exactly. Root calls increase 28 → 39 and child calls 15 → 26; every typed map remains structurally valid (15/15 → 26/26). Actual Adam cursors and adapter/optimizer/RNG/state ancestry are authenticated through step four. [Milestone-four metrics](../../../../ARTIFACTS.md#unpublished-files "Not published: MILESTONE4_METRICS.json") contain every coordinate, source-linked physical-prefix proof, role-separated costs and context grouping. Fixed-final-eight remains the primary pending readout; validation four is not used to select a checkpoint.

A [posthoc graph example](../../../../ARTIFACTS.md#unpublished-files "Not published: CASE_VALIDATION4_MAP_COUNT.json") isolates a downstream counting failure: all 32 labels appear in eight printed maps in the final root's physical prompt branch; those maps contain exactly three numeric-value labels, matching gold, but the root answers six. Its eight sampled actions print successive maps without computing a cross-batch count. [The data-only reproducer](../../../../ARTIFACTS.md#unpublished-files "Not published: case_probe.py") checks the official physical branch against wire tokens and never executes the sampled code. This one example is not a prevalence estimate.

The broader [secondary diagnostic](SECONDARY_DIAGNOSTIC.md) and [cached results](../../../../ARTIFACTS.md#unpublished-files "Not published: map-fidelity/") keep unsupported, conflicting and partial map evidence unavailable. In validation four, three trajectories meet its conservative complete-map criterion: all three maps imply the correct aggregate, but two roots give wrong numbers and one fails final syntax. Trajectories that print only aggregate counts often remain parser-partial; this screen must not be presented as an exhaustive failure taxonomy.

## Earlier first milestone

The initial SFT policy scores 2/8 strict validation answers and 0/16 strict transfer answers. Transfer has 15 training-admissible outcomes and one trace/setup-null; its retained empty completed reply is recorded separately. Bare numbers and explanatory prose are not repaired into the required whole-reply `Answer: N` contract.

Round one supplied 15 mixed-group training episodes from 16 attempts (four strict correct, one admission-null). The actual first optimizer update used 7,575 root-action tokens across 51 root turns, with zero child/observation loss tokens. All 504 Adam parameter states have cursor one, initialized fresh from the fixed SFT weights rather than its optimizer. Gradient norm was 0.280566; adapter delta L2 was 0.200036; optimization took 31.31 seconds. The saved adapter starts `f5b6bf47`.

Round two has six strict correct of 16, all admitted and selected; its persistent Adam checkpoint has also committed. These fresh training samples are **not paired learning evidence**. The fixed validation/transfer readouts at later checkpoints are still required.

| Completed stage | Strict correct / planned | Training-admissible | Native verified calls / physical attempts |
| --- | ---: | ---: | ---: |
| Validation 0 | 2/8 | 8/8 | 43/43 |
| Transfer 0 | 0/16 | 15/16 | 66/70 |
| Round 1 collection | 4/16 | 15/16 | 110/113 |
| Round 2 collection | 6/16 | 16/16 | 117/117 |

No native-proof discrepancies were found in these four completed-stage audits. Calls retained in excluded trajectories still count as physical cost; they are not silently turned into training rows or policy-negative examples. Native helper requests occurred in every recorded episode. Requesting beyond the first four records is only a coverage signal, not proof that the root consumed or counted those labels correctly.

## Reproducible artifacts

- [First two-update snapshot](../../../../ARTIFACTS.md#unpublished-files "Not published: snapshots/74b531466f6b0ddb1843d3e194fea2e903f1ceea643bbcf67d2b065fe6fc63ca.json"): content-addressed milestone, pending items and checkpoint metrics.
- [Per-stage audits](../../../../ARTIFACTS.md#unpublished-files "Not published: stages/"): planned coordinates, reconstructed endpoints, admission exclusions, helper/map coverage, root/child usage and exact source hashes.
- [Per-checkpoint audits](../../../../ARTIFACTS.md#unpublished-files "Not published: checkpoints/"): actual Adam cursors, adapter/optimizer/RNG hashes, previous-policy ancestry and root-only token metrics.
- [Auditor](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") and [focused fixtures](../../../../ARTIFACTS.md#unpublished-files "Not published: test_audit.py"): two fixture tests passed after captured missing-implementation RED. Completed stages are processed once; the bounded watcher reads cheap markers between stages.

No fixed-final-eight benefit is available because the campaign stopped. The terminal report supersedes these earlier progress notes; immutable snapshots remain unchanged.
