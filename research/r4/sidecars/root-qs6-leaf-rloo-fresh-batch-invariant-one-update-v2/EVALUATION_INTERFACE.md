# V2 one-update evaluation interface

Evaluate only `outputs/attempt-001/checkpoint-0001` when `RESULT.json.status == "UPDATED"`,
`optimizer_steps == 1`, and the V2 RNG receipt records master seed `202609121401` with only
NumPy legacy seed mapped to `745658489`. The checkpoint must satisfy the unchanged V1 full-48
gradient replay, qualification, optimizer-step, and child-only binding contracts. The fixed256
evaluation changes only the child adapter; the QS6 root remains unchanged.

