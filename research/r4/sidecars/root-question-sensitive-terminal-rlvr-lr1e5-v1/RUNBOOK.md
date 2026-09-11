# MAIN runbook

CPU review must verify `CAMPAIGN.json`, focused tests, fresh CLI imports, exact source-map equality,
and the absent output namespace. MAIN writes an identity-bound `MAIN_REVIEW.json`, runs `lr_seal.py`,
then launches `lr_owner.py run` through the qualified single-GPU lifecycle. The outer parent cap is
15,000 seconds. Do not rerun, refill, resume from high-LR state, or select a checkpoint by outcomes.
