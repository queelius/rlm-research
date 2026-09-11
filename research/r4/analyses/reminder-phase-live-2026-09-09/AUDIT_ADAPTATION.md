# Local audit renderer isolation

The first audit invocation stopped before publishing metrics: installed vLLM
ChatCompletionRequest.model_validate mutates its input dictionary by adding
`tool_choice`. A focused model-free CPU check reproduced that addition; direct
comparison of all 192 raw CALL requests to frozen SPEC requests found no study
request difference. The auditor now passes a deep copy into that validator, as the
qualified original renderer does. Raw/frozen sources remain unchanged. The sealed
METHOD, strict parser, primary estimand and fixtures are byte-identical; this is
local analyzer input isolation, not a scientific repair or score change.
