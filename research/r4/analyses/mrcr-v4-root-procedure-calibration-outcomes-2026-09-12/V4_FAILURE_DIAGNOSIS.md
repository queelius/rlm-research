# V4 failure diagnosis

Attempt-004 is not a scientific null. All 32 planned coordinates were recorded, but every episode
failed in task setup before any native model request with the same `SandboxError`: reading
`/context.txt` returned “No such file or directory.” Thus there are zero observable scores, zero
root/child/native calls, and no basis for root-RL eligibility.

The allocation runtime and image were correctly selected. The remaining fault was Python class
identity: V3/V4 patched `MRCRTask.setup` on the module loaded under the private alias
`mrcr_calibration_old_task`; `SingleAgentEnv` constructed tasks from a separately imported canonical
module named `mrcr_rootless_document_baseline_v2`. Its original setup only attempted to read the
file, so the intended write never ran. V5 repairs only this dispatch seam and is separately sealed.

The independent V4 report is useful only as integrity/failure evidence. It does not authorize an
optimizer update and must not be pooled with a later functioning calibration.
