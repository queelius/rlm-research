# Final-update/selection milestone — 2026-09-09 02:33:22 UTC

All eight actual optimizer steps are authenticated. The final update is Adam7→8 across504 states,20 episodes/47 root turns/11,198 root tokens, gradient0.74279296, deltaL2 0.08727898, optimization35.246s, with all guards passing and zero child/observation credit. Total158 mixed episodes/362 root turns/108,461 root tokens and297.324s optimization. Training, authentication/loading, service startup, collection and whole-run wall times remain distinct.

Fixed validation0/2/4/6/8 is2/3/3/2/4 out of8. The original earliest-maximum rule uniquely selects step8, reproduced independently from all five actual manifests and matching SELECTION.json. Selected and final are the same exact checkpoint here: `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`.

Initial→8 has three newly correct/one newly wrong;4→8 one newly correct/no newly wrong;6→8 two newly correct/no newly wrong. All eight val8 endpoints are admitted and terminal-valid. Actual initial physical prompts/sampling match8/8; first-root actions differ8/8. Val8 costs108,184 logical input/9,676 completion tokens,117 calls,100 subcalls and131.762s rollout, versus initial56,405/6,767 tokens,57 calls,43 subcalls and90.133s. This is not a demonstrated efficiency improvement.

Decision: the modest selected validation gain is exploratory and selection-optimistic (five candidates, only two contexts, no matched unchanged-policy replay). Do not promote it to learning/transfer evidence yet. Complete the already-predeclared original-versus-selected24+24 transfer over six root-new but leaf-train-supported contexts; keep weight selection frozen before those outcomes. No new training or model selection is authorized by this note.

Evidence: `step08-20260909T023046.482537Z.json` SHA256 `aa25c6e281a208bf3a29494ff058e2cd41e889d86f0c655975d64adde278a874`; `validation08-selected-20260909T023322.894125Z.json` SHA256 `aeb95acb9321b13e81be91011ab1d03c8d63825280f0a4e251b639b6ed3786da`; `FIRST_ACTIONS_VAL08.json` SHA256 `09a79aa7234107ed26622bba16a4c189e2a1cc094f17d24284a35fa0c029915e`. No GPU calls by the observer.
