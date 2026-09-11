# Approved B-only replay implementation

1. Write focused tests for six paired templates, exact original-render reconstruction, immutable prompt-ID binding and actual generate-boundary capture with a CPU fake; observe RED.
2. Build one authenticated B-only outer spec using saved templates and frozen helpers. No case, label, checkpoint or decoder search.
3. Implement one-model-load capped HF runner; six paired microbatches, per-row/per-batch checkpoints, null infrastructure failures, no retries/resume.
4. Verify in the trained environment with CUDA hidden, freeze source/inputs and publish READY with parent-owned launch command. No GPU action by preparation agent.
