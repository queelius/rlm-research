# CPU preparation handoff

Prepared2026-09-09 UTC; zero model/GPU calls. Source/data/spec frozen before READY. No training data, existing helpers, active services or model weights changed.

Prepared identity: `69b5983ba13301ad5b38e9951cd77252b519793d097433f48f05d70c55264e2f`.
SPEC SHA256: `690e3d46bdcb13b5561e7803132de5c76fd8cd6279ea79a700dc271f7f174863`.
Driver SHA256: `eb9509ed00a85cd942d959407deb8c80f495f7fec2426f477265af48e407cb63`.
DATA SHA256: `e3b929cab3e16296e6b92efceddca0a7a84fbec3455c569ec0e66c91cf30e9b8`.

## Data and limitations

Pinned official `stanfordnlp/sst2` revision8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb, validation parquet SHAfb00fe008f6828f86ba2beda8415a4cf5da0c884f21c5f238c87131b5aa19529,72,813bytes. Acquired2026-09-09T00:01:13Z into external cache.872 labelled validation rows,872 normalized groups,0duplicates/0conflicting groups. First256 by predeclared normalized-group SHA order:134negative/122positive, not balanced or filtered by labels. Every original idx and physical row index retained in DATA.dedup, including unselected groups. Prompt sentences retain original representative text; normalization is grouping-only.

[Official dataset card](https://huggingface.co/datasets/stanfordnlp/sst2/blob/8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb/README.md) labels underlying corpus license unknown. This is not changed to Apache2.0: that separately applies to the [archived HF loader library license](https://github.com/huggingface/datasets/blob/88896a7b28610ace95e444b94f9a4bc332cc1ee3/LICENSE). No remote loader was used; already installed PyArrow25.0.1 read parquet directly. [Stanford dataset source](https://nlp.stanford.edu/sentiment/index.html) archived separately. No corpus-license confirmation, blind-test claim or pretraining-overlap exclusion. Public validation and whole-task/prompt/vocabulary shift make this exploratory task transfer, not pure label rename or general reasoning proof.

## Frozen comparison and cost

Four64-sentence contexts × two seeds739019/739043. Each of original, oldSFTc32de, fixed-final A and fixed-final B gets natural5 (104calls), natural64 (8calls), schema64 (8calls):120/model,480total. Natural5 has a residual4 each context/repeat. Exactly1536 item assignments/model across three cells,6144 across all4 models (256 unique groups, not6144 independent examples).

Natural64 and schema64 retain identical messages, generic tools, seed, temperature0.5 and max_tokens1024. The sole request difference is `structured_outputs.json`: array of exact64 enum strings negative/positive. Natural5 changes only sentence grouping/cardinality; no output schema. New sentiment user instructions contain no TREC definitions. Tool attempts are scored as contract failures, never executed. No retries, fallback or output repair. Six-TREC-label leakage diagnostic does not count as sentiment correctness.

HF local tokenizer estimates745–2365 input tokens, max3389 with output reserve. Actual provider prompt IDs remain authoritative; HF/vLLM serialization identity is explicitly not claimed. Source version-specific BatchEncoding shape was caught before publishing DATA/SPEC, reproduced by focused test, fixed by extracting flat input_ids. Sources unchanged after SPEC publication.

1200-second wall cap/model,120-second request timeout,4concurrent calls, maximum122,880 output tokens/model (491,520total). Estimate5–15minutes total inference plus ~1–3minutes per required service reload;4800seconds total inference hard cap. These are prospective estimates, not measured cost. First-response endpoints only, parent owns A100/service scheduling. No new model downloads needed.

## Binding and launch

Use a fresh complete endpoint descriptor for each actual alias. `bind --condition original|old_sft|A|B --endpoint ... --output ...` authenticates frozen source/data, adapter disk/config hashes and base manifest. A/B additionally require fixed immutable training MANIFEST identity, recipe/data/source closure, completed actual RESULT, matching SELECTION epoch2 and step206/204, exact checkpoint path, optimizer/RNG member inventory and checkpoint hash agreement. It never selects by sentiment outputs. Each bound spec freezes actual alias, endpoint and complete requests; each run retains request/response, alias, costs, actual provider IDs, per-call and per-coordinate JSON.

CPU_BIND_QUALIFICATION.json binds the historical original endpoint only to prove the binding path; it is NOT evidence that that historical service is currently live. Parent should bind the descriptor of the actual newly started service. Runtime checks `/models` alias and root adapter path and per-response alias. The fresh service's vLLM version0.28.0, base parent, max length8192 and inference casting config should be checked by parent's standard serving preflight; this narrow runner does not independently query `/version`. Partial call artifacts remain retained if preflight/runtime crashes; normal timeout/error returns produce SUMMARY with incomplete/infra distinctions. Do not resume by overwriting an output directory; a fresh attempt must remain separately identifiable.

## Verification

Six focused CPU tests pass (`/project/alex_phd/envs/rlm/bin/python -m pytest -q test_driver.py`), with grouping/scoring/request/provenance tests red before implementation and tokenizer regression red before fix. Fake HTTP collector test verifies natural/schema difference, actual alias/prompt ID retention, per-call checkpoints and strict0vs1 outcomes. Full tokenizer preparation and hash closure passed using local training interpreter with CUDA_VISIBLE_DEVICES empty. CPU original-weight binding passed with real disk identities, no network/model calls. A/B bindings necessarily remain runtime actions once their final RESULT files and serving descriptors exist. No full framework tests or GPU qualification were performed.

The bounded-design skill kept the three-cell comparison small; test-first/systematic-debugging caught incorrect tokenizer token counting before publication. Existing read-only source reuse was via an independently loaded module object; no frozen helper file was modified.
