1. Authenticate the failed qualification, frozen group/generation and checkpoint1.
2. Persist dense-A, dense-B and sparse FP32 LoRA gradient vectors without optimizer construction.
3. Compute pair metrics using CPU float64 chunked dot products.
4. Preserve the original tolerances and report which pair crosses them; do not step or rescore.
