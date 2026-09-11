---
title: Sparse continuation qualified training-runtime correction
date: 2026-09-10
status: additive_prelaunch
---

The frozen V1 campaign named `/project/alex_phd/envs/bootstrap-training-v1/bin/python`, which does
not exist. No V1 GPU job or scientific output was launched. V2 changes only the owner/trainer and
conditional-readout namespaces to attempt 002 and binds the exact existing training environment
that produced the qualified sparse checkpoints. The objective, windows, inputs, policy lineage,
caps, collector, and readout remain unchanged. An actual subprocess import checks PyTorch,
Transformers, PEFT, Accelerate, sparse math, source-native modules, and the V2 entry without loading
a model or initializing CUDA.
