# Root token-TIS: the high-only advantage does not repeat

The high-dose arm repeats its exact diary answer, but **its advantage over base does not replicate**: all three arms answer that context exactly in seed block2. Base also gains a second exact answer. These successes follow broad document dumps, not correct Python retrieval.

Each cell below is raw exact / available, with unavailable outcomes in parentheses. Every arm planned and recorded16 episodes.

| Fixed arm | Seed block1 | Seed block2 |
|---|---:|---:|
| Base | 0/15 (1 unknown) | 2/15 (1 unknown) |
| LR1e-5 | 0/15 (1 unknown) | 1/16 (0 unknown) |
| LR1e-4 | 1/15 (1 unknown) | 1/16 (0 unknown) |

Against base, high has1 win/0 losses among15 paired available contexts in block1, then0 wins/1 loss among15 in block2. Low has0/0, then0/1. Low versus high is1 high win in block1 and no exact difference across all16 contexts in block2. These are **16 repeated contexts with two decoding seeds**, not32 independent contexts; no pooled significance claim is made. All fixed arms and null unknowns remain visible.

## Mechanism

The diary record `omrcr-2568744ab02d7c2786c8` is the old high-only success. In block2 all three arms emit identical first programs using `data.get('diary_entries', [])`, which fails because the document is a list. Their identical second programs dump the context (17,591 saved observation characters), then select and mutate a matching **user request**, not its assistant successor. Nevertheless, all three finals copy the correct2,290-character diary from the exposed context. The native final/gold SHA is `9fa8717e9ff178353dc159e287c881b9fd30afb7860361bf9f72e7735dafb910` in all four exact diary episodes across the two blocks.

Base's new balance-article exact (`omrcr-62f0a8e60638c25131ad`) follows two schema errors and a20,010-character `print(data)` observation. Its code does not select by role/ordinal/successor. Low returns an introductory social-media example instead; high has an empty invalid terminal. This is the block2 paired loss for both doses.

Across all96 recorded arm×seed×context episodes, the inert procedure detector finds zero role/ordinal/successor candidates and zero clean correct-target observations. This is a bounded static/observation diagnostic, not proof about every possible program. All four new exacts were inspected directly and are dump-and-copy successes. The earlier positive signal therefore does not establish procedure acquisition or a stable dose benefit.

The strongest block2 nonexact partials are the relations poem: base0.9536 and high0.954715, with literal escaped newlines; low returns the user request itself. These partial scores do not show a successful retrieval selector.

## Unknowns and provenance

Block2 base's fish-song context (`omrcr-574a80aeed5114ad4217`) becomes unavailable after repeated dumps: native HTTP400 reports11,510 prompt tokens versus the8,192 limit. It is not an owner-timeout censoring event. Block1's shared unknown is instead the relations-poem context, with11,232 tokens versus8,192. All owners released their service; incomplete owner flags caused by these unknowns are preserved, not relabeled as all-model-successful runs.

[derive.py](derive.py) reuses the qualified mapper/classifier/scorer through explicitly bound owner/study/collector modules and output paths. Each seed block runs in a fresh Python interpreter to prevent inherited module-alias leakage. All96 saved derivations reproduce; raw final/gold equality and nonempty final/native equality are checked separately; all96 physical initial prefixes match the frozen prefixes. Across blocks, the16 context/gold/prefix identities and all three checkpoint bindings are identical. [DERIVED.json](DERIVED.json) records428 source hashes and all paired context units, SHA `3f2361b11b927197eae9a2bad583c2d43f6d41c1928b2211b2c6a07690f44d43`. [REPORT.json](REPORT.json) gives the compact machine-readable result. The original first-block derive/RESULT and all scored outputs are untouched.

## Research decision

Deprioritize or retire **this specific one-step root-token-TIS corpus/gradient recipe**, pending fresh usable SFT-procedure rollouts and the qualified terminal-strip-disabled reward path. The two-block result does not support another dose selection or repeat of the same weak rollout recipe. It does not show that TIS or policy-gradient learning generally fails. This remains an exploratory, adaptively exposed held panel and a fixed training-gradient comparison, not a training-seed replication. No generated code, GPU, or extra evaluation was used; no primary score was repaired retroactively.
