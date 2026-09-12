# Token-TIS held three-arm mechanism check

The high-dose one exact answer is a real raw native success, but it came from dumping the document and copying the answer—not from a correct Python retrieval procedure. This is an exploratory one-answer signal, not evidence for choosing a dose.

## Exact-success matched trace

Row 12, `omrcr-2568744ab02d7c2786c8`, seed `202609132112`, asks for the first diary entry about scenes. All three arms emit the identical first program, including `data.get('diary_entries', [])`; all receive `AttributeError` because the document is a list.

| Arm | Subsequent behavior | Raw outcome |
| --- | --- | --- |
| Base | Another invalid `data.keys()` call, then a truncated first-three-record dump plus a broad keyword match selecting the introductory example record | Wrong “Ties That Bind” example scene; diagnostic score 0.039886 |
| LR 1e-5 | Another invalid `data.keys()` call, then prints only the first, introductory example record | Wrong example scene with literal newline escapes and a long escaped-newline tail; score 0.008044 |
| LR 1e-4 | Prints the entire conversation, then fails again on `data.get('diary_entries', [])` | Correct 2,290-character final, exactly matching host gold and the saved native response |

High dose's second tool observation has 18,051 characters and contains the entire target in Python string representation. Its final correctly decodes/copies document assistant record 2 and prepends the marker. Both generated programs still fail; there is no successful role-aware/ordinal retrieval and no child call. The immediate changed behavior is broader target exposure after the shared first error. The saved sequence does not establish that the optimizer reliably learned this behavior.

## Unavailable and partial outcomes

The unavailable coordinate is the same row 1 (`omrcr-530d9996c900aa5d7b62`) in all three arms. All four returned programs are identical across arms. Schema and syntax errors lead to repeated document dumps of 19,942 and 19,686 saved characters. The fifth native request is rejected with HTTP 400 because its decoder prompt has 11,232 tokens, exceeding 8,192. The last tool result also selects the words `poem about relations` from a user request, not the requested poem. This is context exhaustion, not the owner wall-clock cap; unavailable rewards remain null.

The strongest partial case is row 7, the glue scene: base scores 0.950163 and low dose 0.992803 after failed schema assumptions and broad dumps. Low dose copies the correct scene but inserts 33 characters: a separator/newline plus formatting spaces. High dose instead returns an empty invalid terminal. This is output-format sensitivity and a regression at high dose, not monotonic procedural improvement.

Low dose's row 6 score 0.188700 is only a 183-character chorus excerpt versus a 1,660-character complete-song target, again after a failed schema call and truncated dump. Smaller high-dose partial increases also do not show correct retrieval: row 14 copies the second elephant article instead of the first; row 8 copies the first eggs scene instead of the second. These wrong-ordinal identifications use explicitly diagnostic newline/quote comparisons only; no score was repaired. Row 13's returned letter has no exact document-record match.

## Minimum useful replication

Keep all three frozen arms and all 16 contexts. Predeclare one new shared 16-seed block before generation: 48 additional episodes with unchanged prompts, fixed child, temperature 0.5, 2,048-token completions, six total turns and existing 650/700-second per-arm caps. Report paired raw exact and unavailable/null separately; retain both doses. Annotate target exposure, program failure and blank-terminal behavior on rows 12 and 7. Do not repeat only the successful coordinate or automatically promote high dose. This checks decoding robustness of fixed checkpoints, not robustness to a new training sample/gradient.

The panel's prior exposure is declared in the sealed evaluator; no confirmatory transfer claim is warranted. Nothing from this held analysis was fed into training.

## Evidence boundary

`MECHANISM.json` contains 48 independently checked raw reply/gold comparisons, 21 focused cases, 33 native-call receipts and 96 source hashes relative to `/project/alex_phd/runs/rlm-research-r4`. The high-dose exact episode SHA is `09f1c3a380a8d7bf21f35e9f10213e461ed6c5206d3d2dbb8fa13364a265471b`; its final native-call receipt SHA is `04038a59698b8ec109567be53e280a8caa0637881ea4400a057fd638266a75d3`. Native final/gold text SHA is `9fa8717e9ff178353dc159e287c881b9fd30afb7860361bf9f72e7735dafb910`.

Only saved JSON and text were inspected; no generated program or GPU was executed. Initial decoded messages match across arms on the focal rows; physical-prefix checks remain the collector's preserved evidence. MAIN's derivation and RESULT were not edited. The systematic-debugging skill kept the report tied to the actual error→observation→final sequence instead of treating the score as evidence of a working program.
