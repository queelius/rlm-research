# Flexible allocation: where the remaining errors arise

All60 raw native returns and actual prefixes validate; zero score mismatches. Official result stays fixed3/12 versus flexible3/12, with one win and one loss across12 paired exposed contexts. No retrospective score correction.

The shared eight-candidate pool contains all annotated supports for9/12. Fixed selects all for3/12; flexible for6/12 (four gains, one loss). Two of the four coverage gains still use2+2, so this is evidence about global reranking plus allocation and an extra model call—not quota relaxation alone.

The exact win is supported Raven→San Francisco→Transamerica recovery. The exact loss replaces an unsupported Copenhagen performance-venue copy with the death city of an unrelated Detroit mayor. Maness also changes from Cubs2016 to Cardinals2011, but the correct-content sentence remains EM-wrong. These are diagnostic distinctions, not substitute scores.

Downstream evidence use is now a concrete target: the Jesus Christ source is selected but ignored; house-music qualifiers are read as a causal claim; Italy’s alliance relation is confused. Four flexible endpoints contain the right core value but differ in answer phrasing/units (Nevada date, Maness year, Boston area, tornado count); not all have complete selected bridge support.

Physical:60 calls,75,961 prompt tokens,1,617 completion tokens. Natural fixed:36 calls/48,311 prompt/894 completion tokens. Natural flexible:48 calls/66,295 prompt/1,078 completion tokens. All usage known; token lengths and natural costs are not matched.

## All12 relation reviews

- `q1459e23aa1e832118689` — available_relations_but_answer_span_mismatch: Both conditions retain Corleone→Nevada3 and the Nevada admission date12. Both answer with the given date inside the same verbose sentence, so both are EM-wrong; flexible cites both supports while fixed cites only12. The1+3 allocation changes distractors, not availability of the requested chain. The dataset labels admission as land acquisition; this review follows frozen gold without endorsing that wording.

- `qbb5349a9b7b73dd77f26` — global_reranking_recovers_relation_but_verbosity_hides_content_gain: The candidate pool includes Maness biography5 and Cardinals title history7. Fixed first2+2 omits5 and answers Cubs2016. Flexible remains2+2 but selects5/7 and answers the Cardinals last won in2011. This is a source/entity content improvement, not a quota-relaxation effect, and it remains EM-wrong because the answer is a full sentence. The returned citation omits the biography bridge.

- `q89d2485eaf22e7b31624` — candidate_gap_but_direct_country_relation_sufficient: Candidate pool lacks annotated border paragraph0. Flexible3+1 adds film-location9, but both selected sets already include Tuolumne→United States2 and both answer correctly. The direct country fact can bypass the full annotated chain, so incomplete coverage is not a necessary failure condition.

- `q0617d8bcca5d6bb08ed0` — genuine_selected_source_recovery_and_exact_gain: The shared pool contains Raven→San Francisco2 and Transamerica Pyramid→San Francisco9. Fixed omits9 and says no pyramid is evidenced. Flexible3+1 selects9 and returns The Transamerica Pyramid, an official normalized exact match. The selected source relation supports this gain, unlike a coincidental answer string. Gold supports are split1+1, so better global ranking could recover them even with a2+2 quota; this comparison does not isolate quota relaxation alone.

- `qe758ff5a6c6a4c8ab52f` — recovered_source_not_used_wrong_entity_binding: Flexible2+2 adds Christian3, explicitly based on the life and teachings of Jesus Christ, while retaining persecution→Christians17. Despite both needed relations being present, final chooses Saints Simplicius, Faustinus and Beatrix from distractor7. Fixed also answers martyrs. This is a concrete downstream entity/relation-use failure after improved selection, not missing source.

- `q11c97ffb5874da1e6941` — candidate_date_missing_and_planner_drops_available_bridge: Candidate pool lacks voting-year paragraph4, so the required2008 fact is unavailable. Flexible recovers Daughtry elimination18 while retaining North Carolina10, but discards the available Mayor Turner→Democrat2 bridge in favor of more Idol material. Both finals abstain. Candidate recall and selected bridge coverage both limit this case.

- `qbefa334e11dccbcdb36d` — planner_drops_bridge_and_final_misreads_nested_qualifier: Fixed1/7/11/13 has an alternative complete chain:13 pairs Eisenhower/Nixon;1 identifies Nixon among U.S. presidents;7 gives U.K./U.S. recognition;11 gives UK pirate-radio/DJ support for house music. Fixed final now mentions the radio/DJ answer but rejects diplomatic recognition as its cause, misreading a country-identifying qualifier as a causal claim. Flexible replaces recognition bridge7 with redundant VP14, despite all annotated supports being in the pool, and again rejects the question. More annotated coverage is not the whole explanation: fixed evidence was already sufficient via13.

- `qb53b0da358d8710a5f77` — planner_loses_capital_bridge_and_both_omit_answer_units: Fixed includes Wellesley→Massachusetts4, Massachusetts→Boston13 and Boston land area0. Flexible3+1 drops13 for unrelated Mona/Puerto Rico7 while retaining Raleigh15. Both return48.4 from correct Boston source0 but omit square miles, failing the frozen gold string. The same numeric answer does not establish that flexible resolved the missing Massachusetts/Boston bridge.

- `q7e02378adeb958101023` — available_final_relation_but_extra_answer_words: Pool includes immigrants/religion paragraph1, but neither arm selects it. Both retain Diocese of Charlotte→North Carolina0 and fewer-than20 tornadoes11, and both state the correct count. Their extra answer wording prevents EM; flexible improves answer-F1 by being shorter but cites only11. This is not evidence that allocation recovered the missing religion bridge.

- `q301af64604063fd4fc6b` — partial_candidate_chain_and_wrong_alliance_interpretation: Pool omits Ottoman-Bulgaria19. Flexible adds Italy date/source9 but drops Italy-from-Ottomans12 and leaves available Rila→Bulgaria13 unselected. Its final discusses Axis alignment1936/1940 rather than the requested Allied-side change, despite source9 describing surrender and Allied forces. Missing bridge selection and downstream relation disambiguation coexist; neither branch matches July1943.

- `q16e943b03b89ba19b10b` — unsupported_exact_replaced_by_wrong_person_death_location: Fixed answers Copenhagen citing6, whose city is a performance venue, not the spouse death location. Flexible4+0 selects every annotated support6/9/18 but also distractor2, a biography of Detroit mayor Jerome Cavanagh containing Lexington,Kentucky. It answers that unrelated person’s death city and cites2. Annotated support18 itself describes exhibitions, children and her father dying, not her death city. Thus the official exact loss is real, but it is not loss of demonstrated faithful retrieval; annotation sufficiency and wrong-person binding are separate issues.

- `qcbd5a4bf80cace0d247b` — same_sources_successful_composition: Both select the identical5/11/13/15 set. Sources give Narrow Island→Falklands, conference→London and Falklands representative in London→United Kingdom. Both produce the same exact answer and all three support IDs. This is a successful source-grounded endpoint with no selection intervention for this case.

Next-design details are in NEXT_COMPARISON.md. All source quotes, candidate IDs and finals remain linked through the per-case evidence hashes and raw response hashes in MECHANISM_REVIEW.json.

REPORT SHA `3ff7230537b4ed3f17b35d9dcbaa896ead0cf22267785fa5aae07339a3f2c2b2`; review JSON SHA `9d04a8005f7241dc5f2221a9e8d2b3de40a81f5ceda116b522b060abcded5d1f`. No GPU, model calls or generated-code execution.
