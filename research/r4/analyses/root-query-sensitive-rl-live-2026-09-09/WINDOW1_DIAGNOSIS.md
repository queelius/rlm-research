# Window 1 diagnostic

Read after `METHOD_READY.json` was frozen, while window 2 was collecting. This is a diagnostic of
the already executed traces, not a change to the declared campaign or its reward.

- All 24 planned episodes were recorded. Twenty-two endpoints were authenticated and available;
  two were provider-failure NULLs. There were no integrity failures.
- No episode called `rlm(...)` or used `batch_contract.py`. Child action-token mass is zero, so this
  window contains no executed evidence about child-label quality.
- Thirteen available replies satisfied the exact `Answer: N` shape, but all thirteen had the wrong
  integer. Nine available replies were prose or empty and therefore contract-invalid observed
  failures.
- As an explicitly non-scoring semantic diagnostic, five of the 22 available replies stated the
  gold integer inside otherwise invalid prose: count-single repeat 3; distinct-union repeats 4, 6,
  and 7; and weight-union repeat 7. They remain reward zero and are not repaired.
- Successful-looking manual traces read the public files and classified questions directly. Other
  traces used brittle literal-keyword tests, looked for a nonexistent category field, stopped before
  a final answer, or generated malformed shell/code; one trace replaced its sandbox-local
  `records.json` with invented records. Thus the zero reward mixes non-use of the child interface,
  strict final-only formatting, and genuine semantic/program errors.
- With no successful mixed group, the declared admission rule correctly produced no training group
  and a no-op at Adam step 0. This diagnostic found no measurement-integrity reason to alter the
  campaign.

Gold was used only for the stated post-outcome semantic diagnostic. Native model outputs were not
executed anew, repaired, or rescored.
