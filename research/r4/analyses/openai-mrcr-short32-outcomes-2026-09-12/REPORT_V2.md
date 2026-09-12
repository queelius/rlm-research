# OpenAI MRCR short32 authoritative raw-string readout

The run recorded **32/32** episodes; integrity clean is
**False**. The official scorer was recomputed on unmodified strings.

- Raw-string exact: **0**
- Strip-normalized exact (secondary only): **0**
- Official >=0.90 but not raw-exact: **4**
- Raw marker-prefix wrong below 0.90: **15**
- Other wrong: **11**
- Unavailable: **2**

Exact causal mapping reports 96 root and
0 child actions across
0 delegated episodes.

Decision: Zero raw-exact retrievals reject continuous reward mixedness as sufficient root-RL evidence. Diagnose the actual JSON procedure before choosing a training method. A prospectively specified filtered-behavior-cloning/SFT method may intentionally select successful training trajectories if its denominator, failures and costs are preserved; evaluation contexts and checkpoints must not be cherry-picked.

Short32 is a composite feasibility screen: compared with V7 it changes the dataset, context length,
underlying conversations, and representation. It does not isolate a JSON-format effect. No heldout
record receives a model query.
