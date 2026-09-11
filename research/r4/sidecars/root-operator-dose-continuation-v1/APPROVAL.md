# Additive approval

MAIN approved ideas/2026-09-10-operator-sft-dose-decision.md SHA51c9c0c878a7537c1a16bcf071a48ff55d29600b919f3a71419f3cea4b9051e3 and YAMLc5c0dcfd6cd99047ea5b282d95156bbe5491aec92284c85e8041a15de50dd28c.

MAIN subsequently approved training-first4320s outer (4200work+90cleanup+30margin), then readout6480s; combined cap10800s unchanged. Freeze96 full evaluation and24 diagnostic coordinates before training READY. Training is exact6→24, same72, no recapture or optimizer reset. No partial24 substitution. Readout implementation may finish concurrently with training; its future source receives a separate seal. All old sources and design artifacts stay immutable. MAIN alone accepts/launches. This sidecar owns no queue or lock operations during preparation.

Original optimizer did not save parameter names. A CPU meta-model using the pinned base configuration, model implementation and PEFT configuration will reconstruct the original named trainable enumeration used by `[p for p in model.parameters() if p.requires_grad]`. The live loader must match this ordered name/shape list before moment attachment. This is source-derived reconstruction, not a claim that names were historically logged.
