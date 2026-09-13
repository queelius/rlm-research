# B05 implementation-ID renaming audit

COMPLETE_RAW_NATIVE_AUDIT: 36/36 native calls returned and all 18 paired coordinates are available.
The renamed panel has strict/semantic exact 2/2
for base and 2/2 for cp1. Both models solve the
same one stage context in both repeats. Cp1 changes only one of 18 selected sets, improving BA on
that coordinate without an exact-answer win; mean BA delta is 0.011905.

On the 17 coordinates valid in both the original and renamed readouts, original mean BA was
0.625024 base versus 0.665675 cp1.
After renaming it is 0.638756 for both. None of either model's 17
renamed selected sets maps back exactly to its original set. Thus most original local cp1 advantage
does not survive this identity change, while the two exact renamed outputs are already present in
the unadapted base. This is consistent with ID/tokenization-sensitive behavior, not proof that the
update memorized names: every continuation changed and the probe remains stochastic and in-sample.
