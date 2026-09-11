"""Run the unchanged fixed six-update objective on the combined72 corpus."""
import sys
import recovery_study as s
import qs_train as qualified


def main():
    qualified.s = s
    module = qualified.implementation()
    module.s = s
    module.run(module.parse_args())


if __name__ == "__main__": main()

