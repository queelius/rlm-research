# Complete-success trajectory SFT: independent audit

Status: **pre-outcome method/parser prepared; awaiting MAIN's terminal trigger.** No new training-result or readout outcomes have been opened.

[METHOD.md](METHOD.md) defines the two primary baseline contrasts, fixed8 versus last-saved RL7 distinction, training weights/masks, strict endpoints versus nulls, native coverage and cost accounting. [EXPECTED_INPUTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: EXPECTED_INPUTS.json") records independently checked27 training-only trajectories/114 physical root actions/15,256 targets, eight orders and24 shared fresh readout coordinates. All114 current teacher actions match saved native/wire IDs and logprobs; this preparation checks those source records rather than redoing the author's entire graph-export framework.

[audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") supplies the terminal-gated parser, reusing the sealed independent row-mean native/endpoint implementation with its documented internal-request-ID join correction. [test_audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: test_audit.py") has three new focused fixtures; inherited endpoint/copy/null fixtures remain in the prior sealed audit. No model-loaded training test or production-source mutation is performed here.

After MAIN's trigger: native CPU Python `audit.py audit --main-terminal-trigger`. A readable result report, compact metrics, conservative mechanism/cost supplement and final source seal will be added. Neither earlier outcome knowledge nor this audit authorizes creating new training candidates or changing the accepted study.
