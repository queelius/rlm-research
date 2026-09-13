"""Process-local rebinding of the already tested collector to attempt-003 study."""

import collect_v2 as previous
import study_v3 as study

previous.study = study
previous.source.study = study
source = previous.source
execute = previous.execute

