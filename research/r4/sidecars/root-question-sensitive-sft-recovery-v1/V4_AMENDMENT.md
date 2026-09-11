# V4 service-status callback amendment

V3 computed the right protected deadline formula but referenced `status` from the outer training block. The recovery `service()` helper called callbacks with only `(stage, end)`, so the service-local start time was inaccessible and Python resolved the older training-stage dictionary. V4 passes the service-local status explicitly as the third callback argument for both capture and readout and anchors protected collection to `service_status["started_epoch"]`.

The focused owner-flow regression advances 20 seconds of capture startup, 100 seconds of capture, 500 seconds of training, 30 seconds of readout startup, and 40 seconds in a failing dev command. It verifies that protected collection still executes and receives `readout_service_start + 1950 + actual_dev_elapsed - 90`, not the training start.

V4 is an owner-only acceptance amendment. All subprocesses and scientific receipts retain the coherent V3 science identity `6767f821559baf6d0b51a3096e2268f8067c600bc33597b08f81baa9f6fdf938`; V4 has a separate source-amendment identity. No corpus, task, seed, model, optimizer, budget, or output namespace changes.

Correction to the V3 prose: the combined72 fixture did monkeypatch `module.load_model` with a sentinel. It proved genuine V3 corpus verification and actual qualified trainer CLI routing **up to an intercepted loader boundary**; it did not exercise the actual model loader or model numerics.

