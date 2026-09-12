# Procedural SFT first train readout — 2026-09-12

Four updates improved teacher-forced fit but did not establish the retrieval procedure: **0 raw-exact / 28 available / 32 recorded**, with no child calls. The fixed train manipulation gate failed. Held stages were not run, so this is a training-panel failure, not a measured transfer failure.

## What the model actually did

The readout contains 143 native calls: 140 returned and three provider errors. Returned actions comprise 113 ipython actions and 27 terminal responses. All 32 initial physical prefixes exactly match their teacher prefixes. All 32 episodes encountered a saved Python error; 84 of 108 saved tool observations contain an error type.

First actions invent top-level dictionary keys in 29/32 episodes, e.g. `data['messages']`, `data['poems']`, or `data.get('scenes')`, although the file is a list of role/content messages. The remaining cases also assume unprovided record fields. No generated action matches its teacher AST, no action contains the teacher's indexed successor retrieval pattern, and only two episodes mention the role field at all. Typical recovery prints structure or broad document representations, then selects a request or unrelated example instead of the following assistant response. Five finals equal marker + the requested user instruction; three final bodies are exact substrings of the document's introductory examples under the report's stated raw/newline-only comparison.

Independent inert extraction validates all 32 teachers against the public document and host gold. This, plus matching initial prefixes, argues against a wrong teacher or initial harness prompt as the main cause. A matched base rollout on this exact train32 schedule is absent: lexical mismatch demonstrates procedure non-acquisition, not a causal estimate of behavioral regression or improvement.

## Why four rows are unavailable

| Training record | Saved failure |
|---|---|
| `omrcr-81962be30bd6c8668637` | Provider rejected 8,640 prompt tokens against the 8,192 limit after broad output (largest saved observation 20,051 characters). |
| `omrcr-50ed8cfc6b9065167728` | Same rejection at 9,012 tokens; largest observation 19,912 characters. |
| `omrcr-39fbac00a29ae2b82e1f` | Same rejection at 9,783 tokens; largest observation 15,906 characters. |
| `omrcr-08d6010dc261b9832b1d` | IPython broker `set_broker_scope → _execute_silent → get_shell_msg(timeout=30)` raised `_queue.Empty`, surfaced as a HarnessError after two returned model actions. |

The provider failures are associated with the model's expansive debugging trajectory, but remain unavailable under the frozen taxonomy. The broker timeout's deeper cause cannot be determined from these receipts. All four retain null reward; they are not recoded as incorrect answers. One separate, available episode reached the six-turn limit and receives the existing finite-horizon zero.

## Retrieval versus copying

Three available finals have official similarity ≥0.90 (0.9499, 0.9794, 0.9897) but zero raw exact. Their outputs copy escaped document representations: the formal-letter case becomes exact under a diagnostic-only replacement of literal backslash-n with newline; the news article additionally has an extra quote; the winter poem additionally has a literal Unicode escape and extra quote. These diagnostics do not repair or rescore the submitted outputs.

No saved observation contains the full target body as a raw string; three contain it with escaped newlines. Thus retrieval and representation mistakes dominate this rollout. The teacher terminal task supplies a clean, exact answer observation and already has very low loss; simply increasing terminal-copy weight is not the first supported intervention.

## Fit, decision, and next comparison

Training completed in 160.745 seconds with four immutable checkpoints. Recorded action CE falls 1.4225 → 1.3700 → 1.2460 → 1.0985; weighted terminal loss stays about 0.00212 → 0.00198. These are measurements before each update, not a post-checkpoint4 likelihood evaluation. Adapter displacement reaches L2 1.2877.

The next informative comparison is the authorized **fixed total32-step continuation**: restore checkpoint4 adapter, Adam and RNG; perform 28 further updates on the same immutable corpus, objective and LR1e-4; retain checkpoints and run the same train32 manipulation readout. Keep schema and prompt unchanged to isolate dose. Admit held stages only through the existing train gate. Success must include actual list/role/successor retrieval and raw exact, not only lower forced CE. If a larger dose fits teachers yet still invents schemas, investigate teacher-to-native action likelihood/replay before changing tasks.

Evidence and all 32 episode diagnostics are in [REPORT.json](REPORT.json), including source hashes, native audit indices, error attribution, copying diagnostics, collector totals and training metrics. Generated code was parsed as inert text and never executed; no GPU was accessed. The systematic-debugging workflow kept observed failure causes separate from the dose hypothesis.
