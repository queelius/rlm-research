"""Qualified native evaluator bound to GPU-dispatch continuation attempt003."""
import postcapture_readout as qualified
import postcapture_binding as b

b.OUTPUT = b.s.SOURCE_ROOT / 'outputs/attempt-003'

if __name__ == '__main__':
    qualified.main()
