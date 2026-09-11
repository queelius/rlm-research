---
id: root-operator-dose-intermediate-readout-v1-ready-v4-correction
date: 2026-09-10
status: additive-prelaunch-correction
---

# READY V4 correction

A final preacceptance self-check found that V3 did not include a free endpoint represented only by
physical records in its slot taxonomy, and its evidence pins omitted request/failure files. V4 adds
the physical-directory union, pins the complete request/response/result/failure/physical evidence
union, and counts a probe response as a confirmed physical attempt without treating an HTTP error as
a returned completion. Request-only remains prepared/attempt-unknown.

V1--V3 remain as rejected pre-review history. Scientific inputs and caps are unchanged.
