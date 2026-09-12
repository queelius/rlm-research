"""Materialize and authenticate the fixed checkpoint32 evaluation bindings."""

import json

import checkpoint


if __name__ == "__main__":
    print(json.dumps(checkpoint.ensure_checkpoint(), indent=2, sort_keys=True))

