# Fixed procedural-SFT readout

This evaluator never selects a checkpoint. It first runs fixed checkpoint4 once on every one of the
32 training records. The heldout phase remains closed unless all32 episodes are scientifically
available and at least8 raw-string exact answers span at least4 distinct context hashes. Normalized
exact and the official partial score are reported but cannot satisfy that gate. A failed gate ends
with a train failure diagnosis; no heldout request is made and no intermediate checkpoint is tried.

After a passing manipulation check, the only heldout comparison is a paired base versus fixed
checkpoint4 readout over all16 heldout records and two pre-frozen repeats. Both policies use the same
coordinates, seeds, original public questions and original JSON bytes. The official OpenAI scorer
receives the unstripped reply and answer. Missing/infrastructure outcomes remain unavailable rather
than wrong. Exact native prompt/action/logprob mapping, initial-prefix checks, cumulative six-action
cap, root/child counts, unknown usage and clean release are retained from short32 V2.

The dual-LoRA service needs an alias for each role. A CPU checkpoint-seal command therefore derives
an all-zero LoRA with the exact checkpoint4 adapter structure. It is checked tensor-by-tensor and is
mathematically the released base policy; it serves both the base root and the fixed child. The
checkpoint4 arm changes only the root alias. This controls the serving path but should be reported as
zero-LoRA base transport, not bare-base transport. Trusted depth headers and the previously qualified
native role overlay route depth0 to the chosen root and depth1 to the zero adapter.

All heldout bytes/prefixes and host-only labels are frozen before inference. They are absent from the
training READY and cannot affect the teacher, training dose, checkpoint choice, or train gate.
Heldout means held from this project update, not absent from base-model pretraining.

