---
title: Qwen3-8B stable-anchor execution plan
status: CPU preparation only
---

- One released Qwen3-8B, no adapter, no tools, official local chat template with thinking disabled.
- 144 exact paired calls, four workers, 90 seconds/request, 3072 output tokens, 8192 context.
- Shared-clock limits: 2250 work, 2370 owned, 2400 outer seconds; 300 startup and 90 release reserve.
- No retry, repair, reordering, output salvage, or result-dependent adaptation.
