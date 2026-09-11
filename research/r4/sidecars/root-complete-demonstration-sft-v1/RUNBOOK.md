# MAIN-only launch

Read READY.json for the exact native Python argv. CPU verification:

`CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-complete-demonstration-sft-v1/launch.py verify`

After MAIN acceptance, use the inherited actual MIG UUID/LD environment and shared
GPU ownership lock, then the same command with `run` and the exact outputs/attempt-001
directory. Parent outer3600s; owned3570s including cleanup; shared work3450s.
No resume/retry. Existing outputs are never overwritten. On capture failure no arm
trains. Do not substitute an old control or a partial/best checkpoint.

Outputs: teacher-service/ lifecycle; capture/example-*/ authored raw native traces,
physical/ actual child responses and marked scripted-root transport, CORPUS_READY;
training-action_only and training-action_terminal checkpoint-0001..0004 with
RESULT/SELECTION; unchanged/action_only/action_terminal rollout/rows, episodes,
typed-audit and TERMINAL. Top TERMINAL retains failure and unavailable stages.
Unrun planned readouts are recovered from prepared/EVAL_PLAN_FINAL.json, not zeros.
Independent scientific analysis belongs after owned service release.
