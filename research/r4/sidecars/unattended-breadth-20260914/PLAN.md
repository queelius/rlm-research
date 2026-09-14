# Unattended breadth screen implementation plan

Goal: Run finite, resumable paired comparisons on public datasets without Codex or paid APIs.
Architecture: one persistent local Prime/vLLM service at a time, a frozen case manifest,
deterministic staged schedule, per-call receipts, and a deadline-aware campaign owner.
Source and weights remain separate. This exploratory sidecar does not change the RLM API.
Spec: approved September14 conversation: broaden to aggregation, MuSiQue, FinQA,
LongBench v2, and short controls; screen before further training; preserve10% Codex.

Global constraints: one exclusive A100; no gold in model-visible prompts; no input truncation;
no arbitrary generated-code execution; one real scientific response within90s; retain failures;
end at min(start+36h, allocation end-10min); checkpoints after every call/episode.

- [ ] CPU data task: freeze original development/evaluation rows, source identities,
      deterministic disjoint stages, provenance and exclusions in data/.
- [ ] Write test_runner.py first. Assert literal scoring, arithmetic whitelist,
      context rejection, actual HTTP native response decoding, complete-condition resume.
- [ ] Implement runner.py: native token requests; direct, fixed summary delegation,
      evidence-preserving delegation, and bounded arithmetic on FinQA. No unrestricted
      root-policy learning or new optimizer in this initial breadth campaign.
- [ ] Implement campaign.py: reviewed base-service environment, one flock, staged4B/8B
      comparisons, health/deadline checks, and durable progress/terminal files.
- [ ] Run focused CPU fixtures, then pilot on real public cases. Inspect returned
      text and scoring, not merely GPU memory. Fix observed seams additively.
- [ ] Freeze source/config hash manifest, launch detached campaign, verify real returns,
      publish compact source and handoff, preserve10% account reserve.

Experimental plan: base released4B and8B (not a causal model-size comparison), T=.5;
pilot first16 per dataset, next64 screen, subsequent176 extension, subsequent256
replication, with new decode seeds in later blocks. Fixed two-way split initially;
four-way split in a separate later block. Score on all admitted paired examples,
record output format failures separately from unavailable transport. Cases too long
for the shared full-input bound are excluded from ALL arms before calls and counted.
This deliberately covers only the admissible LongBench subset, not a full benchmark.
Extensions require non-floor/non-ceiling scientific outcomes on earlier development
blocks; this is exploratory screening, not untouched confirmatory evaluation.

No expectation that the finite useful queue must consume all36h. Do not create filler.
No adapter weight updates are claimed by this first campaign; later training uses
the newly discovered failure modes after interpretation.
