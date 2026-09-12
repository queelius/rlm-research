# Five changed paths; one whitespace win

All 64 RLOO outputs and their cp32 controls are available. Primary short accuracy is unchanged at25/32, long unchanged at10/16, and four-needle changes10→11/16 (one win, no loss). This is one unreplicated gain on an exposed secondary panel, not evidence of general improvement. The weaker22/32 fixed-baseline-RL arm does not strengthen the primary comparison against cp32.

Actual native prompt/action arrays were compared for every pair: held31/32 entire paths identical; long15/16; four-needle13/16. All64 initial prompts match. First actions match61/64. Thus the large pre-clip training gradient did not produce broad output changes, but neither short nor long paths are completely identical.

## Every changed case against cp32

| Panel / record suffix | Actual change | Interpretation |
|---|---|---|
| Four-needle c09fb4c7d672b0d18934 | Same209-token Python action, exact same clean1261-character stdout, same final prompt. Final317→318 tokens; token256 (two ASCII spaces) inserted before EOS151645. Exact1258→1260 characters. | Sole exact win; final copying/termination, not a new literal selector or retrieval. |
| Four-needle45e34dc2b87a24884f6b | Old206-token valid tool request for “message about pressure,” ordinal3, followed by an ordinal-unavailable traceback and13-token refusal. New first action reaches2048-token length cap, yields no parsed tool and empty terminal. | Both exact0; loss of usable tool-call generation, not an accuracy loss because the old answer was already wrong. |
| Four-needle c6ef6fdb8d43f3f08137 | Old first action reaches2048-token length cap with no parsed tool/empty terminal. New207-token valid “poem about offices,” ordinal4, prints clean1309-character stdout;326-token final omits the final two spaces. | Both exact0; official score0→0.999229. This different case causes no-clean3→2; it is not the exact win. |
| Short746d5e1512abdfa38878, repeat1 | First208-token program changes literal “email about stores” to “message about stores.” Both yield the same ordinal-unavailable traceback. Final21-token refusal is identical; its prompt differs because the program changed. | Both exact0; neither selector works. |
| Long508ab438696a81bec39f | Same208-token first program (“program to find the matrix,” ordinal2) and same ordinal-unavailable traceback. Second action differs but both hit2048-token length cap, parse no tool/final content and return empty terminal. | Both exact0; unresolved selection plus malformed/nonterminating output, no gain. |

The four-needle gains/losses in usable tool generation cancel in this tiny set; the exact-score increment comes only from final spaces. A final-only loss can still change first actions because the weights are shared. This paired sample does not establish either beneficial or harmful retrieval learning.

The saved-gradient analysis supports a terminal-boundary mechanism: the mixed training groups contrast correct two-space endings against early EOS/extra newlines. Eight uniform-zero literal-selector training failures supply no RLOO gradient. No generated program was executed during this audit; code was parsed inertly and actual stored observations/token arrays were inspected. CHANGED_PATHS.json contains all five cases, exact token tails, stop/length statuses, hashes and raw evidence paths without copying entire answers.

## Smallest useful next question

Measure the fixed new RLOO checkpoint once on all original fresh8 training contexts ×4, using the exact old202609250000..31 seeds and unchanged native harness, against the frozen cp32 training batch7/32. This is explicitly an in-sample behavioral diagnostic: it asks whether the update fits the trained decision boundaries without transferring, or whether its likelihood change has not yet altered these sampled trajectories. It is not another validation panel, a replication, or a model-selection rule.

If training behavior improves mainly in final spaces while the exposed primary panels remain flat, more copying-only updates do not yet address the user's delegation/retrieval question. If training exactness stays flat, inspect changed training outcomes and boundary probabilities before authorizing a larger dose; one unchanged paired batch does not prove zero policy change. If it regresses, do not automatically add steps. No four-update pipeline is proposed now.

The more relevant next RL family would be B05 worker reports trained against a clearly defined report-implied global task reward, but only if the current source-visible/report-only feasibility screens show usable claim-valid alternatives and sufficiency contrast across multiple roots. Such a future experiment needs fresh training/test roots and must distinguish an oracle-sibling conditional reward from actual end-to-end root reward. No B05 optimizer or further MRCR update is prepared or authorized here.
