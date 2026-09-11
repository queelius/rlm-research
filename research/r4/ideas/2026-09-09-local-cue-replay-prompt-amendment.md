# MAIN correction before replay preparation is frozen

September9,2026, before READY. The original local-replay design incorrectly required
equality between fresh96 matching and constant physical prompts. Their format
instructions differ, as the completed fresh96 report explicitly states. MAIN
and the preparing agent independently inspected the frozen bodies: the first
Qwen3 AG pair has4684 versus4683 input tokens. No replay model was run and no
READY was published. Preserve the original design and this explicit correction.

Choose a **new shared neutral format instruction**, rather than copying the
constant-arm instruction and making the treatment contradict p0000. Keep exact
fresh96 texts, record order, task definitions, labels, tools, native template and
model revision. Replace only the user format paragraph with the already qualified
shifted72 INSTRUCTION, identically for all three replay cues:

Return only a JSON array in displayed input order, exactly one object per input
record. Emit exactly the keys tag then label. The output format fixes the tag
value. Set label to that displayed input record's canonical label, regardless of
the forced tag value. Do not omit or reorder any input record.

Render this new common request using the actual native typed serializer, freeze
its full prompt IDs, and verify all three replay conditions share those IDs.
Record the exact old-to-new instruction diff and new template qualification.
Do not call these the exact original fresh96 physical prompt IDs. The new neutral
prompt avoids a gratuitous source-ID-versus-constant instruction confound, but
the shifted current source cue still deliberately conflicts with positional label
assignment; its named-label score remains a secondary diagnostic.

All other choices in local-cue-replay-main-design.md remain:32 fixed positions,
shared gold-label constant-tag prior history, current-tag-only difference,
finite-candidate complete-label likelihoods, raw HF inference rather than guided
decoding, no truncation/reselection and no attention/generalization claim.
