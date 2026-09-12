"""All12 inert comparison; preserve official scores and prior quoted-arm evidence."""
from pathlib import Path
import analyze as m

r=m.a.read(m.ROOT/'REPORT.json');assert m.a.sha(m.ROOT/'REPORT.json')=='0d931dd1bbef5d28872b19afe03d5fcf686643620a6d03e2ba07f9a7477f0f4f'
notes=[
('Nevada','W→W; loses date detail','New answer retains Nevada/1864 but drops October31 and stays a sentence. Selected12 contains the full annotated date. It also drops the Michael/Nevada citation3. No exact-score loss masks this substantive answer-detail loss; admission-to-Union versus land-acquisition annotation ambiguity remains.'),
('Maness','W→C; answer-phrase gain','New2011 is a concise extraction of the date already correct in the old Cardinals2011 sentence. Citation7 is unchanged and still omits player/team source5. Quoted helper stayed verbose and wrong. This is no newly recovered team/year fact.'),
('Tuolumne','C→C; unchanged direct support','UnitedStates and citations2/12 are unchanged. Source2 directly supports country; absent bordering-counties source0 still prevents proof of the full annotated chain. Quoted helper cited2/4 instead.'),
('Raven','C→C; answer article removed','TransamericaPyramid remains correct; article removal has no official effect. Citation9 still omits show-location source2. The quoted helper, unlike this arm, added2 and achieved full supportEM.'),
('Christian','W→W; wrong entity unchanged','Same martyrs answer/source7 despite explicit Jesus/Christianity source3 and persecution source17. This is an entity-joining failure unaffected by answer phrasing. Quoted arm named Jesus in a sentence, but its helper had been rejected; do not attribute that content change to accepted relations.'),
('Idol','W→W; concise justified abstention','Insufficient evidence replaces the verbose abstention; citations unchanged6/10/12/18. Frozen sources still lack MayorTurner party and NC voting-year facts. No phrasing rule can supply missing2008 evidence.'),
('House music','W→W; unsupported-connection stance persists','Still rejects the nested connection rather than using the useful local house-music fact11; recognition bridge7 is absent. Drops all citations, reducing supportF1. It avoids the quoted arm\'s explicit false claim Nixon was not president but does not solve the query.'),
('Boston','W→C; requested measurement units','48.4 becomes48.4 square miles, the same answer-form win as quoted helper. Source0 already contained the number and units. Citation0 unchanged; explicit Massachusetts→Boston source13 remains absent. Not proof of a newly solved bridge.'),
('Tornado','W→W; extra wording retained','Still fewer than20 tornadoes per year with citation11. Only capitalization changes; quoted arm alone narrows to fewer than20 and scores exact. Requested quantity was already correct in all arms; missing immigrant-religion source1 remains missing.'),
('Italy','W→W; wrong alliance interpretation','New answer denies becoming an ally and cites0/9/17; baseline cited0/9/18. Source9 contains the1943 transition, while the Rila/Bulgaria/Ottoman chain is absent. Neither the denial nor previous Axis dates answers the intended Allies question; not a format-only error.'),
('Copenhagen','W→W; wrong-person city unchanged','Still copies LexingtonKentucky from unrelated mayor source2. Quoted arm instead abstained because selected AnneMarie source18 lacks death city. This shorter instruction does not prevent the wrong-person substitution; official answer remains Copenhagen.'),
('Falklands','C→C; same complete support set','UnitedKingdom remains exact; citations5/15/13 only reorder the original set5/13/15 and retain supportEM1. Quoted helper had added irrelevant SaintKitts11, reducing support exactness.'),
]
assert len(notes)==len(r['questions'])==12
cases=[]
for q,(label,category,finding) in zip(r['questions'],notes):
    cases.append({'record_id':q['record_id'],'label':label,'category':category,'finding':finding,
        'answers':{arm:v['score']['parsed'] for arm,v in q['outcomes'].items()},'quoted_answer':q['quoted_arm_outcome']['score']['parsed'],
        'official':{arm:{k:v['score'][k] for k in ('answer_em','answer_f1','support_em','support_f1')} for arm,v in q['outcomes'].items()},
        'source_payload_path':q['source_payload_path'],'source_payload_sha256':q['source_payload_sha256'],'native_paths':q['calls']})
wins=[q['record_id'] for q in r['questions'] if q['outcomes']['direct']['outcome']=='W' and q['outcomes']['concise']['outcome']=='C']
quoted_wins=[q['record_id'] for q in r['questions'] if q['outcomes']['direct']['outcome']=='W' and q['quoted_arm_outcome']['outcome']=='C']
value={'schema':'musique-direct-answer-contract-all12-mechanism-v1','primary_unchanged':True,'cases':cases,
       'direct_to_concise_wins':wins,'direct_to_quoted_wins':quoted_wins,'common_win_ids':sorted(set(wins)&set(quoted_wins)),
       'all12_reviewed':True,'sources_and_raw_request_delta_verified':True,'source_report_sha256':m.a.sha(m.ROOT/'REPORT.json'),
       'adjudication_source_sha256':m.a.sha(Path(__file__)),'costs':r['natural_full_policy_cost'],
       'quoted_costs_context_only':r['quoted_natural_policy_cost_context_only'],
       'decision':'Same aggregate5/12 at fewer calls, but only one common win and no faithful-composition dominance. Preserve both results; no best-prompt selection or exposed-panel sweep.',
       'limits':'Adaptively proposed universal instruction on exposed12; one final draw per case. Source content/citation judgments are inert diagnostics, not rewritten official metrics. No GPU, model calls or generated-code execution.'}
m.a.write_x(m.ROOT/'MECHANISM_REVIEW.json',value)
lines=['# Direct answer contract: cheap exactness gains, different winners','',
       '**3/12 direct →5/12 concise**, all12 available;2 wins/0 losses. All12 raw native decodes, expected request bodies, old-seed/model binding and exact instruction-only prompt deltas pass; zero independent/owner score mismatches. Existing scores are unchanged.',
       '', '**The wins are Maness and Boston.** The quoted helper won Boston and tornado, so only Boston overlaps. Both concise-arm wins already had correct answer content in the direct baseline:2011 appeared in a full sentence, and48.4 lacked requested units. There is no new retrieved fact.',
       '', '| Condition | Exact /12 | Natural calls | Prompt tokens | Completion tokens | Support EM /12 |','|---|---:|---:|---:|---:|---:|',
       '| Cached direct |3|48|66,295|1,078|2|','| Concise direct |5|48|67,375|880|1|','| Quoted relations, contextual comparison |5|60|79,124|5,597|1|',
       '', 'Newly spent concise work is12 physical calls,10,692 prompt and306 completion tokens; all costs are known. Cached36 acquisition calls are charged to each deployed policy but not rerun. Token costs are not matched. Concise support-F1 sum falls6.536→5.452; quoted support-F1 sum was7.707. Equal exactness at fewer calls is not equivalent behavior or faithfulness dominance.',
       '', '| Case | Outcome and mechanism |','|---|---|']
for c in cases:lines.append(f"| [{c['label']}]({c['source_payload_path']}) | {c['category']}. {c['finding']} |")
lines+=['','The strongest caution is hidden harm within already-wrong rows: Nevada loses month/day; Christian still chooses martyrs; Copenhagen still copies another person\'s city. The explicit concise instruction is not consistently obeyed and does not fix missing selection or relation joining. Do not launch a best-prompt sweep on these exposed12 or describe this as a decomposition improvement.',
        '', 'REPORT.json retains all12 original paragraphs, decoded final strings, source/support gold only on the host, request/response paths and SHA256. MECHANISM_REVIEW.json links both conditions and the prior quoted result without pooling or rewriting outcomes.',
        '',f"REPORT SHA256 `{value['source_report_sha256']}`; MECHANISM_REVIEW SHA256 `{m.a.sha(m.ROOT/'MECHANISM_REVIEW.json')}`. No GPU or generated-code execution."]
m.a.write_x(m.ROOT/'REPORT.md','\n'.join(lines))
print({'review_sha256':m.a.sha(m.ROOT/'MECHANISM_REVIEW.json'),'markdown_sha256':m.a.sha(m.ROOT/'REPORT.md'),'common_wins':value['common_win_ids']})
