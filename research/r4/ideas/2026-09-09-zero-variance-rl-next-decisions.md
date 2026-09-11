# When a sampled batch gives no reward contrast

September9,2026. Focused primary-literature check, not a new experiment or a
general literature review. All links were opened on this date; no third-party
code or datasets were downloaded or executed for this note.

## The observation we need to explain

Our adaptive root-RL campaign completed128 training attempts and seven actual
updates. In round8, one prompt had8/8correct; the other had0/7correct admitted
answers and one infrastructureNULL. Neither prompt offered a within-prompt
reward contrast, so the frozen rule stopped without update8. The hard prompt's
numeric answers included10,12,16 and19 for gold11. Uniform binary rewards do not
mean identical generated answers or task mastery. Checkpoints and the original
STOP remain intact; a new study now evaluates last-saved7 explicitly.

## Relevant work and what it does not settle

[DAPO, v1, March18,2025](https://arxiv.org/html/2503.14476v1), section3.2,
collects additional prompt groups and filters groups whose sampled answers are
all correct or all wrong. This preserves groups with reward variation for an
update. It motivates bounded refill sampling for us, not an unbounded search
for favorable results. Its mathematical-reasoning setup and other simultaneous
algorithm changes are not evidence that this alone improves our multi-turn RLM.

[No Prompt Left Behind, v3, February9,2026](https://arxiv.org/html/2509.21880v3),
sections3.2–3.3, instead gives uniform-reward groups token-dependent advantages
derived from model entropy and correctness. Entropy is detached for that scaling.
Its ablations warn against treating an arbitrary positive/negative constant as
equivalent to the full method. This is a candidate new objective, not a correction
we should silently apply to saved rollouts or an already accepted training run.

[Learning from Hard Prompts, v1, August28,2026](https://arxiv.org/html/2608.27982v1)
analyzes difficulty-dependent effects of conditioning on mixed-reward groups and
proposes amplifying rare correct responses. It is a recent preprint using math
benchmarks, not independently verified RLM evidence. Its warning makes prompt
difficulty, sampled group composition and retained/discarded rollout costs
important metadata even if we first try ordinary bounded refill sampling.

## Ranked experimental choices

1. Prefer a separately frozen, bounded group-refill continuation if the current
   richer-SFT readout provides a usable warm start. Keep exact terminal reward,
   fixed child, native root-action likelihoods and optimizer recipe. Freeze the
   candidate training-prompt order, sampling seeds, per-update candidate cap and
   total wall/rollout budget. Collect only from the same policy until an update;
   never mix stale-policy groups without explicit likelihood treatment. Keep
   every attempted/discarded/NULL group in the cost ledger. A four-update pilot
   with at most four groups of eight rollouts per update and a45-minute inclusive
   planning cap is a starting design, not ready launch authority. Compare fresh
   paired pre/post task answers, not accuracy on selected mixed groups.
2. If obtaining any mixed groups consumes most of that budget, stop extending
   refill caps. A separately controlled entropy-shaped or distance-to-answer
   objective could then be informative. Distance reward changes what is valued;
   entropy shaping changes token credit and needs its own exact native audit.
   Do not add both together, or reward helper counts instead of correct work.
3. If the coordinator still stops after partial evidence, first test whether
   interface feedback or complete trajectories repair that prerequisite. Our
   newly completed ledger pilot exposes exactly this issue. More policy updates
   on an unusable interface are not automatically the most informative GPU job.

The key comparison is information gained per allocated GPU hour, not the number
of optimizer steps. For any promoted follow-up, log all sampled prompt groups,
source split/context IDs, rewards, native admission/NULL reasons, mixed-group
yield, retained advantages, token/episode weights, optimizer/correction proofs,
checkpoints, actual model load/readout costs and a fixed evaluation rule. No
current result establishes a new RL algorithm or broad decomposition ability.
