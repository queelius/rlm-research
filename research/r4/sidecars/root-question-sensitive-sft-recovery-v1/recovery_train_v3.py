"""V3 trainer entry; qualified numerical objective, coherent combined-corpus identity."""
import recovery_study_v3 as s


def main():
    import qs_train as qualified
    qualified.s = s; qualified.implementation.cache_clear()
    module = qualified.implementation(); module.s = s
    module.run(module.parse_args())


if __name__ == "__main__": main()

