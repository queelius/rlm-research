# Direct answer contract: cheap exactness gains, different winners

**3/12 direct →5/12 concise**, all12 available;2 wins/0 losses. All12 raw native decodes, expected request bodies, old-seed/model binding and exact instruction-only prompt deltas pass; zero independent/owner score mismatches. Existing scores are unchanged.

**The wins are Maness and Boston.** The quoted helper won Boston and tornado, so only Boston overlaps. Both concise-arm wins already had correct answer content in the direct baseline:2011 appeared in a full sentence, and48.4 lacked requested units. There is no new retrieved fact.

| Condition | Exact /12 | Natural calls | Prompt tokens | Completion tokens | Support EM /12 |
|---|---:|---:|---:|---:|---:|
| Cached direct |3|48|66,295|1,078|2|
| Concise direct |5|48|67,375|880|1|
| Quoted relations, contextual comparison |5|60|79,124|5,597|1|

Newly spent concise work is12 physical calls,10,692 prompt and306 completion tokens; all costs are known. Cached36 acquisition calls are charged to each deployed policy but not rerun. Token costs are not matched. Concise support-F1 sum falls6.536→5.452; quoted support-F1 sum was7.707. Equal exactness at fewer calls is not equivalent behavior or faithfulness dominance.

| Case | Outcome and mechanism |
|---|---|
| [Nevada](../../../../ARTIFACTS.md) | W→W; loses date detail. New answer retains Nevada/1864 but drops October31 and stays a sentence. Selected12 contains the full annotated date. It also drops the Michael/Nevada citation3. No exact-score loss masks this substantive answer-detail loss; admission-to-Union versus land-acquisition annotation ambiguity remains. |
| [Maness](../../../../ARTIFACTS.md) | W→C; answer-phrase gain. New2011 is a concise extraction of the date already correct in the old Cardinals2011 sentence. Citation7 is unchanged and still omits player/team source5. Quoted helper stayed verbose and wrong. This is no newly recovered team/year fact. |
| [Tuolumne](../../../../ARTIFACTS.md) | C→C; unchanged direct support. UnitedStates and citations2/12 are unchanged. Source2 directly supports country; absent bordering-counties source0 still prevents proof of the full annotated chain. Quoted helper cited2/4 instead. |
| [Raven](../../../../ARTIFACTS.md) | C→C; answer article removed. TransamericaPyramid remains correct; article removal has no official effect. Citation9 still omits show-location source2. The quoted helper, unlike this arm, added2 and achieved full supportEM. |
| [Christian](../../../../ARTIFACTS.md) | W→W; wrong entity unchanged. Same martyrs answer/source7 despite explicit Jesus/Christianity source3 and persecution source17. This is an entity-joining failure unaffected by answer phrasing. Quoted arm named Jesus in a sentence, but its helper had been rejected; do not attribute that content change to accepted relations. |
| [Idol](../../../../ARTIFACTS.md) | W→W; concise justified abstention. Insufficient evidence replaces the verbose abstention; citations unchanged6/10/12/18. Frozen sources still lack MayorTurner party and NC voting-year facts. No phrasing rule can supply missing2008 evidence. |
| [House music](../../../../ARTIFACTS.md) | W→W; unsupported-connection stance persists. Still rejects the nested connection rather than using the useful local house-music fact11; recognition bridge7 is absent. Drops all citations, reducing supportF1. It avoids the quoted arm's explicit false claim Nixon was not president but does not solve the query. |
| [Boston](../../../../ARTIFACTS.md) | W→C; requested measurement units. 48.4 becomes48.4 square miles, the same answer-form win as quoted helper. Source0 already contained the number and units. Citation0 unchanged; explicit Massachusetts→Boston source13 remains absent. Not proof of a newly solved bridge. |
| [Tornado](../../../../ARTIFACTS.md) | W→W; extra wording retained. Still fewer than20 tornadoes per year with citation11. Only capitalization changes; quoted arm alone narrows to fewer than20 and scores exact. Requested quantity was already correct in all arms; missing immigrant-religion source1 remains missing. |
| [Italy](../../../../ARTIFACTS.md) | W→W; wrong alliance interpretation. New answer denies becoming an ally and cites0/9/17; baseline cited0/9/18. Source9 contains the1943 transition, while the Rila/Bulgaria/Ottoman chain is absent. Neither the denial nor previous Axis dates answers the intended Allies question; not a format-only error. |
| [Copenhagen](../../../../ARTIFACTS.md) | W→W; wrong-person city unchanged. Still copies LexingtonKentucky from unrelated mayor source2. Quoted arm instead abstained because selected AnneMarie source18 lacks death city. This shorter instruction does not prevent the wrong-person substitution; official answer remains Copenhagen. |
| [Falklands](../../../../ARTIFACTS.md) | C→C; same complete support set. UnitedKingdom remains exact; citations5/15/13 only reorder the original set5/13/15 and retain supportEM1. Quoted helper had added irrelevant SaintKitts11, reducing support exactness. |

The strongest caution is hidden harm within already-wrong rows: Nevada loses month/day; Christian still chooses martyrs; Copenhagen still copies another person's city. The explicit concise instruction is not consistently obeyed and does not fix missing selection or relation joining. Do not launch a best-prompt sweep on these exposed12 or describe this as a decomposition improvement.

REPORT.json retains all12 original paragraphs, decoded final strings, source/support gold only on the host, request/response paths and SHA256. MECHANISM_REVIEW.json links both conditions and the prior quoted result without pooling or rewriting outcomes.

REPORT SHA256 `0d931dd1bbef5d28872b19afe03d5fcf686643620a6d03e2ba07f9a7477f0f4f`; MECHANISM_REVIEW SHA256 `1f6ec0c35e6c064f89c8e76688b2426199eb88f31900fbc0880a1640f5edcfd8`. No GPU or generated-code execution.
