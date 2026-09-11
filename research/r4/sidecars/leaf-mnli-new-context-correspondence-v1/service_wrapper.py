"""Explicit reuse of the already qualified released-base launcher."""
from pathlib import Path
import mn_study as s
def qualified_wrapper():
    # The inherited wrapper must itself import the pinned MNLI study. It then installs
    # the already-qualified free-ID study/service aliases at its own execution seam.
    with s.aliases({'study':s.base}):
        wrapper=s.load('mnli_new_context_service',s.BASE/'service_wrapper.py','f72056d9a7497e637c2f9bb7bbbd8b031e34eb541037997dcff9cd6885ef3f86')
    if wrapper.s is not s.base:raise ValueError('inherited service wrapper bound wrong study')
    return wrapper
def main():
    wrapper=qualified_wrapper();wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
