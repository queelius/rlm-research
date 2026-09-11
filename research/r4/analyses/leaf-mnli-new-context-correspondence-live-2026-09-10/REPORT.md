# New-context MNLI correspondence32 independent audit

## Result

The matching-tag advantage extends to this newly selected panel. All 32 native endpoints were
available and whole-contract valid. Matching scored 639/768 displayed labels (83.20%), versus
398/768 (51.82%) for the constant-tag control: +241 labels, or +31.38 percentage points. Matching
won every one of the 16 paired context clusters, with within-context advantages from +8 to +23 of
48 labels. The advantage was positive in all four fixed genres: mean context gain +17 government,
+14.75 slate, +11.5 telephone and +17 travel.

This is breadth evidence for the correspondence effect beyond the repeatedly exposed original eight
contexts. It is not a confirmatory or new-domain replication: these are 16 deterministic selections
from the same cached MNLI validation source and same four genres. “New” is bounded to absence from
the named original, shifted, exact-tag and exposure inventories, not global research or pretraining
unseenness.

## Contract and behavior

Both arms copied 768/768 requested tags, and all 16 endpoints per arm satisfied the exact 48-item,
tag-then-label positional grammar. Therefore the semantic gap is not caused by one arm producing
more malformed outputs. No response was NULL, length-capped or tool-routed; all 32 authenticated
assistant branches ended with `stop`. Neither arm produced a completely correct 48-item batch.

The constant arm's predictions concentrated on neutral (427/768) compared with matching (254/768),
while matching predictions were nearly balanced across contradiction 259, entailment 255 and neutral
254. Against the common gold distribution (272 entailment, 251 contradiction, 245 neutral), matching
correctly labeled 227 entailments, 222 contradictions and 190 neutrals; constant correctly labeled
118, 109 and 171. This is a descriptive error signature, not a preplanned mechanism test.

## Pairing, source and runtime

Each paired request used the same 48 displayed IDs, premises, hypotheses, order and seed. The common
instruction explicitly asked for displayed premise/hypothesis classification and exact copying of
`requested_tag`; only the requested tag values and corresponding positional schema constants differed.
Matching used each public record ID, while constant repeated `mcaf4f357c8f7`. This comparison still
bundles correspondence with diverse-versus-repeated output dictionaries; the separate alien-ID study
addresses that mechanism on the original exposed panel.

The actual service exposed released Qwen3-4B-Instruct-2507 revision `cdbee75f...` with no adapter,
8192 context, bfloat16, four sequences, prefix caching disabled, and vLLM 0.28.0. Live preflight
reported the same model root/alias and service shutdown released all captured processes and ports.
Independent scoring exactly matched all producer admissions and counts.

## Cost

Collection made 32 physical requests and received 32 responses with complete usage. Total observed
usage was 120,279 prompt tokens and 29,804 completion tokens; reported cached tokens were zero for
all requests. Collector time was 178.225 seconds and owner time 215.587 seconds. Provider billing
and FLOPs were not measured.

## Interpretation

The strongest supported claim is narrow: with exact decoder constraints and the released model,
source-corresponding requested tags improve displayed semantic classification on all 16 clusters in
this additional MNLI panel. Exact output validity alone does not remove the effect. The result does
not isolate whether IDs act through binding, local positional steering, lexical diversity or another
structured-decoding interaction, and it does not establish generalization outside MNLI or these four
genres. The next mechanistic comparison should use an unrelated one-to-one alias dictionary against
a wrong visible-record referent while keeping exact requested-tag compliance, rather than adding
another repeated constant control.

## Audit timing and provenance

The method/parser was sealed at 02:41:37 UTC, after owner launch at 02:39:25 but before this auditor
read any response, aggregate or score. The original METHOD incorrectly said prelaunch; the retained
`METHOD_TIMING_CORRECTION.md` supersedes that timing claim. Thus metrics were outcome-unseen but the
method is not a fully prospective prelaunch registration. This auditor did not author the sidecar,
but did contribute prior generic MNLI infrastructure and knew the earlier matching advantage.

Machine-readable details are in `AUDIT.json`; raw evidence is pinned in `OUTCOME_PINS.json`.
