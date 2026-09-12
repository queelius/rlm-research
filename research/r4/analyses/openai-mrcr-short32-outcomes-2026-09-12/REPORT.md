# OpenAI MRCR short32 independent readout

The run recorded **32/32** episodes and is integrity-clean: **False**.
There are **0 exact**, **4 near-exact but
not exact**, **15 marker-prefix wrong below 0.90**,
**11 other wrong**, and **2 unavailable**.

The exact causal audit maps 96 returned native responses: 96
root turns and 0 child turns across 0 delegated
episodes. Native errors/other statuses are 2/0; orphan
starts/results are 0/0.

Python was used in 26 episodes. A code action mentioned
`context.json` in 26 episodes;
24 had an exception-bearing tool
observation and 0 exposed exact
gold in a tool observation. These are procedure diagnostics, not method-faithfulness labels.

Decision: Zero exact retrievals would reject continuous reward mixedness as sufficient root-RL evidence. Inspect the model's actual Python and assumptions, then prefer a simpler exact-verifier retrieval curriculum or prospectively specified procedural SFT from independent training contexts; do not select demonstrations by successful outcome.

This is eight frozen training records x G4. No heldout model query or transfer claim is made.
