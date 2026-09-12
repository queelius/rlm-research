# Coordination correction

The four MAIN launch commands for the fresh8 training readout, LR10x trainer,
B05 attempt003 and LR10x readout queue omitted the external `flock` wrapper.
Their imported helper only checks GPU process emptiness; it does not acquire
the coordinator lock itself. Earlier descriptions implying an external lock
for these four launches were inaccurate. Each still had MAIN-only launch
authority, finite owners and GPU-empty checks, and was started after the prior
owner released. No competing GPU owner was observed; this is a coordination
deviation, not evidence of concurrent inference or invalid accuracy data.

The IDs-only follow-on explicitly acquires the existing coordinator lock and
waits for the currently running dose queue's terminal receipt before touching
the GPU. Do not infer that the live dose queue retroactively holds that lock.
Future MAIN launches must use the explicit wrapper. No live process or sealed
source is altered to apply this correction.
