"""Run the frozen collector with the additive V2 contract-valid scorer."""

import scoring_v2
import study

study.score_content = scoring_v2.score_content
study.score_missing = scoring_v2.score_missing
study.summarize = scoring_v2.summarize

import driver as inherited  # noqa: E402


if __name__ == "__main__":
    inherited.main()

