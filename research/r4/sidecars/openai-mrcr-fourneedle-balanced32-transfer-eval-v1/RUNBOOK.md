MAIN only, private credential environment and one exclusive GPU:

`python owner.py verify --stage cp32`

`python owner.py run --stage cp32 --outer-seconds 1100`

`python owner.py verify --stage lr1e4`

`python owner.py run --stage lr1e4 --outer-seconds 1100`

External supervisors should cap each owner at 1200 seconds. Run both arms regardless of the first score; require clean release before the next stage.
