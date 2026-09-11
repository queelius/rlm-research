# Fixed-eight SFT24 terminal-RLVR pilot

Question: can eight strict terminal-reward RLVR windows starting from the exact
operator SFT24 policy improve free execution on the frozen composition panel?

The experiment trains only on the first eight QSR training contexts, 24 fresh
episodes per window, all six supported primitive operator/scope cells, fixed c32
child, and the current clarified file/question interface.  It starts from exact
SFT24 weights with fresh AdamW state.  Reward is exactly the authenticated native
final `Answer: N`; no process reward, shaped credit, refill, forced child call,
repair, or evaluation example enters training.  Qualified TIS/PPO, masking,
temperature, optimizer, and original native-token/logprob evidence are unchanged.

The fixed readout is all 48 research-exposed composition questions, once from
unchanged SFT24 and once from the last actually committed RL checkpoint, with new
paired seeds.  It is exploratory, not fresh-context confirmation.  Primary scores
retain NULL endpoint bounds and zero-gold strata.  Frozen diagnostics separately
trace genuine child acquisition, actual observed state, executed requested
operator/target/scope, displayed scalar and final, without reexecuting sampled
code or changing reward.  Correctness alone is not credited as faithful planning.

Eight windows fit the measured QSR throughput inside 5,400 training seconds;
readout gets 5,100 seconds.  Outer/work/owned clocks are 10,800/10,500/10,680
seconds.  Fewer than three actual updates diagnoses a weak instantiation and does
not authorize a rerun.  Selection is the last committed checkpoint, including
step zero; there is no validation or best-checkpoint selection.

This adaptive pilot is motivated by demonstrated acquisition and 29 exact dose24
answers, retrospectively narrowed to 26 requested computations, plus poor
composition transfer.  It does not assume terminal reward will teach faithful
composition.  The frozen composition audit reports 9/48 versus 6/48 exact answers
for SFT24/SFT6, but only two faithful primitive SFT24 successes and no faithful
composed success.  Those outcomes informed interpretation, not coordinates,
reward, seeds, or training data.
