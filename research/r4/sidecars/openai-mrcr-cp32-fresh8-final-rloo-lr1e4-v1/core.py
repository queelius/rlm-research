"""Unchanged accepted loss/scorer/replay/RNG functions under exact new study scope."""
import study
implementation=study.bound('fresh8_lr10_core',study.SOURCE_TRAIN/'core.py',study=study)
math=implementation.math;scorer=implementation.scorer;loss=implementation.loss
selected_logprobs=implementation.selected_logprobs;replay_check=implementation.replay_check
save_rng=implementation.save_rng;restore_rng=implementation.restore_rng
