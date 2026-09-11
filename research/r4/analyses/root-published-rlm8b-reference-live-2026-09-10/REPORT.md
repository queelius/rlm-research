# Published 8B native reference: independent terminal audit

Neither package produced a strictly correct authenticated answer: released Qwen3-8B **0/24**, published RLM8B **0/24**. This is a failure of these bounded task/scaffold packages, not an identified weight-learning effect or a general 8B capability ceiling. Retire another full reference rerun for now; a no-thinking switch does not address the observed RLM package failures.

## Outcomes and missingness

| Package | Planned | Native final | Strict correct | Valid format, wrong | Native NULL | Native-correct bounds /24 |
|---|---:|---:|---:|---:|---:|---:|
| Base | 24 | 7 | 0 | 1 | 17 | 0–17 |
| RLM | 24 | 16 | 0 | 1 | 8 | 0–8 |

Available-final accuracy is separately 0/7 and 0/16. Operational success, where a bounded run without a final is unsuccessful, is 0/24 each. NULLs remain NULL in the frozen native-final inventory; these are attempted trajectories, not unstarted or randomly missing observations. Base terminal errors are 7 read timeouts and 10 deadline-before-request failures; RLM has 3 and 5 respectively. The observed upstream loops, malformed programs, invalid label consumption and repeated calls contribute to exhaustion; the final transport manifestation does not establish exogenous missingness.

Each package has 23 nonzero-gold and one zero-gold tasks. Both score 0/23 nonzero and 0/1 zero. All three families score 0/8 per package. Native availability by count/distinct/weight is base 3/1/3 and RLM 6/5/5. The zero cases return bare `0` (base) and quoted `"Answer: 0"` (RLM), both invalid. RLM has two bare nonzero scalars matching gold, at indices13 and18; neither is rescued into the primary score.

| Exposed context | Base native /3 | RLM native /3 | Strict correct, each /3 |
|---|---:|---:|---:|
| readout04 | 1 | 1 | 0 |
| readout05 | 1 | 3 | 0 |
| readout06 | 2 | 2 | 0 |
| readout07 | 0 | 3 | 0 |
| readout08 | 1 | 2 | 0 |
| readout09 | 1 | 1 | 0 |
| readout10 | 1 | 2 | 0 |
| readout11 | 0 | 2 | 0 |

Only five question pairs have both native finals; all five are wrong. Eleven pairs have only RLM available, two only base, six neither. The equal-context operational difference is zero in all eight clusters. Conservative native-correct RLM-minus-base bounds are −17/24 to +8/24 (−70.83 to +33.33 percentage points), not an equivalence interval. The predeclared complete-data bootstrap was not applied. Eight exposed contexts, not48 independent units, support only exploratory descriptions.

## Authentication and scope

The independent method/parser were sealed before launch (METHOD_READY `c797975a…`, PARSER_READY `d518e9ee…`); outcome reads followed MAIN's released-phase/terminal authorization. The auditor reviewed but did not author the study. [AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json") independently authenticates all48 task/gold coordinates and all287 returned native branches: exact actual prompt tokens, decoded completion tokens, worker role/index/messages, seed, sampling, model binding, and current native final lineage. There are no producer scoring disagreements. No sampled program was reexecuted, no partial answer extracted, no prior observation promoted, and no timeout retried.

The actual services bind released Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218` and mit-oasys RLM8B revision `171c96639865d559206cd7ef78c4d8188a91992a`. Both use the latter's pinned chat template, BF16 full weights/no LoRA, context32768, max sequences2, no reasoning/tool parser, root8192/child4096 output caps, temperature0.6/top-p0.95/top-k20/min-p0. Both root and child weights change, and base runs first: this is not a root-only, template-neutral, contemporaneous policy comparison. The official historical RLM `beb0603` code executes in the qualified isolated container; outside recording is distinct from its actual Python semantics. The common paper-derived prompt and task adaptation are not claimed to reproduce original training conditions. QSR readout04–11 are already exposed research contexts; no globally unseen or fresh-transfer claim.

All returned native calls report `finish_reason=stop`. Some root bodies contain many programs/errors in one completion; code appearance or length alone is not evidence of a length finish. Native-final lineages: base five current executed-block finals, one literal final, one observed standalone variable retrieval; RLM fifteen literal finals and one observed standalone variable retrieval. The remaining25 endpoints have no authenticated final.

## Actual evidence use and failure mechanisms

[MECHANISM_V2.json](../../../../ARTIFACTS.md#unpublished-files "Not published: MECHANISM_V2.json") assigns all48 reviewed annotations with raw directories and exact execution-event indices, plus request-level source-text coverage. Base had actual source acquisition in15/24 endpoints (43 returned child calls); RLM17/24 (171 calls). Calls also include model-authored toy tests and repeated requests: these counts do not imply complete maps, valid labels or useful reduction. Automatic context installation is not model-chosen file use.

Base's 43/43 child completions contain `<think>` markup and none is a whole exact category label. Observed roots commonly compare the entire returned string to one label, obtaining0 even when the final child prose names a category. Example base5 completes all four scoped child classifications then executes0 and returns bare0; base11 additionally attempts to retrieve a nonexistent variable named0. Repeated `eval` failures originate in the historical restricted environment (`local_repl.py:113` sets it to `None`), not a recorder regression. Historical child helpers return errors as strings (lines258/263), allowing sampled loops to continue after deadline and consume these strings as labels. Heuristic alternatives also fail; the zero-gold bare0 is not a demonstrated faithful semantic reduction.

RLM has **0/171 thinking-marked children**, but only three whole exact six-category labels. Its prose still defeats whole-string/numeric/first-line parsers. Actual failures include: 92 prose-derived categories assigned to32 records (index16); category mentions anywhere in explanatory text treated as the chosen label (6/8/11); missing `category` fields silently treated as empty (5/12); Python3.11 f-string failures followed by nonexistent-state use (0/9/10); and repeated postdeadline calls replacing usable state with error strings. These are independent of thinking tags.

There is a limited positive process observation, not a successful endpoint: RLM4 extracts exactly16 category-only lines from a batch response in grouped-user order, executes a faithful distinct-user reduction of that predicted map and prints `Answer: 4` (dataset gold2). It then returns the literal `len(qualifying_users)`, not the evaluated answer. This separates semantically imperfect source predictions, identifiable reduction, and final-interface failure. RLM13 executes a heuristic distinct count4 matching gold, despite an observed semantically wrong person-keyword label; it returns bare4. RLM18's heuristic test actually raises a type error before a later bare3; no executed scalar3 is established. Neither diagnostic scalar match warrants rescue or a faithful-success claim.

Read depth: all48 native final/error summaries and program/observation sequences reviewed; base observations read fully, RLM salient full observations plus comment-stripped programs and observation excerpts for remaining sequences. Every returned native branch is computationally authenticated. Not every long child reasoning paragraph was manually read; unidentifiable internal state remains unknown. The first unsealed `MECHANISM.json` draft copied an absent final-key field; V2 corrects that display field from actual `terminal.final`, retaining the draft and leaving scores unchanged.

## Complete physical cost and lifecycle

| Package | Logical calls | Physical attempts | Returned/authenticated | Usage unknown | Known input tokens | Known output tokens |
|---|---:|---:|---:|---:|---:|---:|
| Base | 285 | 103 | 83 | 20 | 142,501 | 110,294 |
| RLM | 369 | 216 | 204 | 12 | 128,194 | 90,632 |
| Total | 654 | 319 | 287 | 32 | 270,695 | 200,926 |

Disk/embedded identity union finds no additional calls outside endpoint snapshots in this run. The335 nonphysical logical failures are all deadline-before-physical-request rejections (182base/153RLM). They are not sampled completions or confirmed GPU generation. Returned calls all have known zero cached tokens; 32 physical attempts lack returned usage, which remains unknown. Provider billing is not measured. Root/child detail is in MECHANISM_V2: base47/56 physical attempts and40/43 returns; RLM36/180 attempts and33/171 returns. Known root output90,753/50,868 and child output19,541/39,764 respectively.

Owner terminal is complete with both services released and no owner error, elapsed2703.981s; outer exit0/no timeout after2731.017s, GPU release recorded. Collectors run1445.845s base and1187.380s RLM. Phase `elapsed_seconds` values1481.027 and2703.721 are cumulative from owner start, **not additive phase durations**. Wall time includes startup, execution, generation waits and release; it is not GPU kernel time. Exact raw/outer pins and per-endpoint artifacts are retained in the audit closure.

## Decision

Do not spend another hour on the same reference48 with a nominal no-thinking toggle. The actual common RLM template has no `enable_thinking` switch; the base checkpoint's own tokenizer template does, so using it adds a template intervention. RLM already emits no thinking markup and still fails label consumption and15/16 final contracts. No-thinking is not an isolated explanation or repair for that package.

A future small **base-only child-format** diagnostic could compare its own supported template with thinking enabled/disabled on fixed genuine source questions and fresh paired seeds, scoring whole labels/semantics and tokens without stripping text. It would answer only child-interface compatibility, not rerun/rescore the current root experiment. Priority remains the informative fixed24 composition/intermediate studies. Reconsider reference adaptation only with a clearer, prospectively isolated final/interface intervention; do not infer that these results negate the published training method.
