# Bounded retry-path evidence

The inherited nano client has a function wrapper, not a Python decorator:
`recursive-example.6xBrmx/src__rlm__client.py:72` defines `call_with_retries`.
`leaf-contract.7HPUr5/nano__engine.py:698` calls it from `_call_model`.
Its first attempt plus five retries can wait 15, 30, 60, 90 and 120 seconds
(315 seconds cumulative), for transport/timeout/server/404/rate-limit/response
validation failures. It preserves request/idempotency identity and supplies
`x-stainless-retry-count` on later attempts. These paths are under the external
`research-cache/2026-09-08-literature` store.

The live campaign retains this path: `root-rlvr-campaign-v1/campaign_native.py:218`
uses `root-only-credit-v1/native_routing.py:53`, which installs the exact
`leaf-role-routing-v1/source/routing.py:128` header-only overlay. It does not
remove nano retries. The provider-side native TrainClient SDK separately has
`MAX_RETRIES = 0` in pinned `verifiers/v1/clients/base.py:14`.

This source inspection does **not** establish an observed retry or sleep in any
campaign episode. `verifiers/v1/interception/server.py:512–557` can replay an
already completed idempotent response. A retried HTTP request therefore is not
necessarily a second inference, and elapsed tail time alone cannot identify a
retry. Concrete attribution needs retry markers/timestamps or interception replay
logs. No campaign source, artifacts, process or GPU was changed or queried.

This terminal experiment alone replaces that call with one SDK request with
`max_retries=0`, and explicitly keeps native SDK retries at zero. The successful
request body, response and usage are unchanged in the real-SDK regression; only
owned attribution headers differ. Real native-renderer/rootless proofs retain
exact physical token IDs and fixture logprobs. Runtime overlay hashes are
recorded per container, in qualification and the sealed spec. These are
transport changes, not a logprob correction, new renderer or model alteration.
