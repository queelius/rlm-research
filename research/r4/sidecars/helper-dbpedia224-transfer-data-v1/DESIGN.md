# New-domain helper transfer screen: data freeze

Question: does news-specific RL help, preserve, or damage classification of
encyclopedia entries under a different category vocabulary? This is a different
source domain and label space, but still a short-text classification task. It
does not test planning, recursion, or unknown pretraining exposure.

Freeze 224 official-test entries, 16 in each of the dataset's 14 classes, using
hash ranking with a fixed namespace. Remove every member of normalized duplicate
content groups and nonempty-title groups before selection. Empty titles do not
constitute one duplicate group. Preserve title/content bytes and source indices.
No model scores or predicted answers affect selection. Do not train on this set.

Reuse the exact historical Qwen helper chat wrapper, with a new encyclopedia
classification instruction and all 14 literal category names. Use 56 fixed B4
requests, temperature zero, 1,024 maximum output tokens, and ordered keyed JSON.
The four intended endpoints are c32, fixed RL8 seed one, fixed SFT8, and fixed
RL8 seed two. Report all, including nulls. No GPU launch is authorized by this
data receipt; evaluator preparation and a measured runtime cap remain separate.

The pinned card declares CC-BY-SA-3.0 and mentions GNU FDL. Keep the source card
and attribution; source texts remain outside Git. Existing scoped r4 manifest/
question/idea search found no DBpedia evaluation or training record; this is a
documented local search, not proof about unrecorded history or model pretraining.
