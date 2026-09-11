# Bounded MRCR document pilot

Approved scope: six frozen, distinct MRCR context groups; one fixed question each;
paired file-backed vanilla/sketch RLM; frozen 4B step-0 endpoint; 12 episodes;
30-minute inference cap. No GPU launch by this sidecar's preparation task.

1. Check treatment isolation, unique document groups, strict root-terminal scoring,
   and the one-read-only-context boundary with focused CPU tests.
2. Reuse the inspected context-only sketch and official metric port. Integrate the
   qualified native Prime TrainClient and nano-RLM harness through a small taskset.
3. Seal data, source, endpoint, image/cache provenance; retain every episode record.
4. Verify CPU imports/configuration and a trusted-code-only rootless boundary probe.

Actual supported native cap: six sampled model turns across branches, recursion
depth one, 2,048 output tokens per request, 180 seconds per episode. The initial
proposal's separate two-subcall/eight-call knobs are not supported by this harness;
they are replaced by the stricter shared six-turn budget, not silently asserted.
Gold is never TaskData, container content, or prompt content. No answer-file or
last-assistant fallback is used. Direct-context inference/truncation is out of scope.
