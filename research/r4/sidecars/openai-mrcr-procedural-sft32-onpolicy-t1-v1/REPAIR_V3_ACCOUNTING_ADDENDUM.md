# Attempt-003 prelaunch accounting addendum

This additive note does not change sealed `READY_V3.json` or its scientific inputs.

- The V3 CPU fixture installs the real role hook and native capture, traverses a real
  `env.run_slot`, and observes a successful T1 native POST. Its fake provider does not assert
  the Authorization header or compare the physical prompt IDs to the frozen prefix. The earlier
  V2 fixture separately asserted both bearer-header presence and exact frozen initial prefix.
  Therefore V3's sealed `CPU_TESTS_V3.json` field `authenticated: true` / READY phrase
  `authenticated_root_generate_post` should be read as transport configuration inherited from
  the TrainClient, not as a V3-local header assertion.
- One actual live GPU diagnostic call occurred during attempt-002 root-cause analysis. It is
  recorded separately under
  `analyses/openai-mrcr-sft32-t1-live-diagnostic-2026-09-12/RECEIPT.json` and is excluded from
  the frozen 32-episode experiment.

