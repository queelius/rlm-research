---
schema: research-decision-v1
updated_utc: 2026-09-12T12:29:00Z
status: exploratory_followup_selected
question: Does broader task-specific experience make reward-based helper training useful?
evidence:
  ag_one_step_report: helper-agnews-native-hf-outcomes-2026-09-12/REPORT.json
  ag_one_step_report_sha256: f60238fa2411acc210e52db57d313a6bf9364b237c628c2f72aae2c396e1dc29
  anomaly_mechanism_report: anomalyxl-budget-shape-v2-mechanism-2026-09-12/REPORT.md
  anomaly_mechanism_sha256: eb9d897d3b16e897b60230b1fd4b49a2e9de0a02214448c0679c00d9b2cdc6fe
decision: replicate_small_positive_before_increasing_learning_dose
publication_status: no_meaningful_RL_improvement_established
---

# What changed

The new news-classification run improved one of 256 answers and harmed none:
211 correct before training, 212 afterward. The changed answer was a science
or technology story previously classified as world news. Every answer was
available, both services were qualified, and the training audit authenticated
all 128 responses and one real optimizer update. This is a small positive
observation, not convincing evidence of a useful improvement.

The 128 sampled maps contain four labels each, giving 512 label decisions over
128 distinct training articles. There were 403 correct decisions. Five of the
32 groups had differing reward values across their four responses. The others
had zero within-group training signal even when some labels were wrong. Thus
new material alone did not automatically solve the reward-variation problem.

Training plus collection and handoff took 257.138 seconds; the HF phase alone
took 76.352 seconds. The two separately started evaluation owners took 111.255
and 117.272 seconds. External wrapper elapsed time was 549.203 seconds across
the three stages, with additional between-stage checks. Never report the
76-second phase as the cost of the whole experiment.

The new panel also leaves clear room to improve: science/technology was correct
on only 34 of 64 examples before training and 35 after. Do not use those test
outcomes to pick training articles or a checkpoint. A larger training inventory
and a different 512-item test set were already frozen without model scoring.

# Next decisions

1. Honor the original pilot rule: repeat the same one-step study with new
   sampling and training RNG seeds. Start again from the supervised helper and
   fresh Adam; do not continue the newly trained checkpoint. Keep the same
   training articles and fixed evaluation protocol. This probes seed sensitivity,
   not independent-dataset transfer.
2. Prepare, but do not yet launch, eight updates on eight distinct sets of 128
   articles. Preserve Adam state and RNG across updates. Assess only the fixed
   endpoint on the fresh 512-item panel, not whichever checkpoint looks best.
   A later comparison must distinguish a larger dose from a changed corpus;
   this exploratory package deliberately changes both relative to the pilot.
3. Prepare a supervised baseline using the same 1,024 articles. If supervised
   learning improves but RL does not, the material contains learnable signal
   that the chosen reward-learning procedure did not exploit. Match and disclose
   article exposure and update counts; do not pretend the answer-token budgets
   or loss functions are identical.
4. Keep root-procedure learning separate. The queued conversation-search
   calibration asks whether the controller can produce real inspections and
   differing rewards. It uses one underlying conversation and no weight update;
   it is neither a recursion-benefit test nor a generalization result.

# Direction retired for now

The current free-form numerical Python variant is not promoted. Twelve of its
20 Python trials had no final answer. The eight remaining finals were valid
JSON but wrong: channel/time confusion, reversed interval endpoints, and an
incorrect rolling statistic explain the saved failures. This is not a broken
scorer masquerading as a learning problem. Another increase in token or time
limits is not the most informative use of the GPU.

If revisited, establish a correct CPU diagnostic baseline before asking the
model to select vetted generic analysis operations. That would be a new
tool-selection study, not a repaired positive result on the exposed ten cases.

# What could become reportable

The current strongest cross-run conclusion is a boundary: varied answers,
nonzero reward gradients, and actual parameter changes are not sufficient
evidence of improved task performance. A publishable learning result needs
replicated gains on separate examples and a clear explanation of what changed.
The upcoming RL/SFT and root-procedure comparisons are intended to identify
that change, not accumulate more variants of the same unproductive setup.
