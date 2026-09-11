# Root plan SFT: CPU-ready handoff

MAIN alone accepts and launches. No GPU/model calls were made during preparation. Scope: two authored-plan SFT4 arms from fixed low66cce root with c32de child fixed, followed by48 transferred whole-RLM episodes. The source of the training text is the operator, not a sampled or successful native trajectory. Data are384 training source groups, with320 query/length-transfer groups disjoint and192 unused validation groups excluded. These are exposed developmental coordinates; no broad generalization claim.

Both arms use the prospective MAIN LR amendment1e-4, fresh AdamW/WD0/clip1 and four full16-example passes. BaseBF16, adapterFP32 rank8/dropout0. Equal-example/action-token mean CE; one initial action per example,2472 target tokens/pass/arm,9888 target exposures/arm. Four actual Adam steps; save adapter/config/optimizer/RNG/cursor every step, fixed final4 only. Root target token masks exclude initial prompt and all tool/child/fake-provider observations. No behavior probabilities/rewards/advantages exist in authored rows. Public user/category literals are permitted, source semantic labels/count answers are not.

Training order canonical→filter_first; readout order canonical→filter_first→unchanged, fixed by master981320001 hash before inference. Training seed981320002 and four shared example orders; paired transfer seeds201–208/301–308 within981320 namespace. No reselection based on coverage/highLR answers. MAIN's LR amendment alone is explicitly exploratory outcome-informed. Starting weights remain66cce, never the new highLR checkpoint.

Active contract files: RECIPE_V2.json, INPUTS_V2.json, prepared-v2/ROWS_canonical.json, ROWS_filter_first.json, PLAN.json, PROMPTS.json, NATIVE_TEMPLATE.json. Superseded CPU evidence is labeled in CPU_AMENDMENT.md and cannot be selected by the runner.

Exact launch:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-plan-sft-v1/launch.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-plan-sft-v1/outputs/attempt-001
```

CPU verify substitutes `verify` for `run` and omits --output. MAIN wraps the exact run argv with2430s outer cap and shared GPU ownership. Owned clock2400s starts before source verification, shared work2280s; two360s training subprocess maxima and three420s collection maxima, service startups/releases consume shared clock,120s final cleanup reserve. Their phase maxima do not all promise simultaneous fit. No timer reset between stages. A missed fixed4 or failed service ends the attempt with unrun planned outcomesNULL; completed empty/wrong0 remains distinct. No fallback to step3, repeated episodes, answer repair or extra coverage reward.

Readouts preserve original native prompt/serializer/child grammar/broker/public files and current first-four API example, with only private16-coordinate cardinality/crosswalk and exact model binding. Root actions are freely sampled, no forced helper use/ledger/root grammar. Child grammar changes the child's action space symmetrically and gets no training credit. Native wire alias/path, first full token IDs, raw output/null and cache evidence are saved unchanged. Inherited transient runtime retries are possible under the total cap; record actual attempts, not just intended calls.

Immutable image8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c uses the qualified local runtime wrapper and ephemeral /tmp/rlmc.0m4242 store symmetrically. No rebuild/store migration/fallback; absence is a failure. Preparation's fixture uses synthetic provider completions with historical native alias binding to qualify message/action boundaries, not actual weight inference. Real readout descriptors/cards must match the new frozen-low or selected-fixed4 bindings and unchangedc32.

Primary filter_first4 minus canonical4 strict whole ASCII Answer within16 paired transferred coordinates and four context clusters. Report all48/nulls, query/length strata, relevant and irrelevant source-bound child requests, first-four copying, complete evidence, returned-label-to-answer fidelity, native root/child/input/cache/output cost, and failures. Correct direct-root answers are valid. Joint-correct cost is secondary and selection-conditioned. Initial equal seeds need not guarantee identical actions. Stop/pivot if the policy copies inappropriate code or remains wrong despite correct evidence; do not add epochs or silently change data. No implementer result projection substitutes for independent audit.
