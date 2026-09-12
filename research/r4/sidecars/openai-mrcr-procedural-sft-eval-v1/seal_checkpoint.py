"""CPU-only conditional checkpoint/zero-adapter seal after training completes."""

import json

import checkpoint


if __name__ == "__main__":
    print(json.dumps(checkpoint.seal_checkpoint(), sort_keys=True))

