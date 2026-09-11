# Cross-family matching-key check: frozen design

This inference-only study asks whether the late-position benefit of explicit correspondence keys
appears in a released instruction model outside the Qwen family. It reuses the exact 16 exposed
MultiNLI contexts, three public-reference conditions, and three formats—labels only, sequential row
numbers, and opaque stable keys—from the adopted stable-key study. All 144 calls are newly rendered
with the local Mistral-7B-Instruct-v0.3 tokenizer. Within-Mistral paired contrasts are primary;
absolute comparisons with Qwen are descriptive only.

For each tagged format, the primary statistic is its positions-17-through-48 accuracy minus labels
only, pooled over the three relation calls but retaining the 16 contexts as paired cluster units.
Report each arm, contract validity, availability, NULL bounds, token use, and context effects. A
positive effect in at least 12/16 complete contexts with no availability loss motivates a fresh-input
replication. A negative or null result narrows portability but must be separated from grammar,
authentication, and missing-response failures. This exploratory gate is not a confidence interval.

The checkpoint is the public, ungated Apache-2.0 `mistralai/Mistral-7B-Instruct-v0.3` revision
`c170c708c41dac9275d15a8fff4eca08d52bab71`, acquired as inert Hugging Face configuration,
tokenizer, and safetensor shards. `trust_remote_code=False`; the config has no `auto_map`. This is a
new model family on research-exposed inputs, not new-corpus evidence, a pure capacity comparison, or
an independent training replication. Grammar-constrained decoding remains part of the interface.

Sampling is explicitly temperature 0.5 with the exact inherited paired seed per context and all
other request fields frozen. Mistral's native chat template and EOS token 2 are used; no Qwen token
constant is used. The service exposes only the pinned released base, no adapter, with an 8448-token
bound: the largest native Mistral prompt plus the unchanged 3072-token output allowance is 8275,
which does not fit the earlier 8192-token service bound but is below the model's native 32768 limit.
MAIN alone may allocate one A100. The cap is 2400 seconds outer / 2370 owned / 2250 work,
four workers, 90 seconds per call, no retries or repairs, and all 144 planned slots retained.
