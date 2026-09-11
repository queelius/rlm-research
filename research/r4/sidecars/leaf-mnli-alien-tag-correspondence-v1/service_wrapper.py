"""Exact qualified released-base launcher under the local study binding."""
from pathlib import Path
import study as s
def qualified_wrapper():
    with s.aliases({'study':s.base}):wrapper=s.load('alien_tag_service',s.BASE/'service_wrapper.py','f72056d9a7497e637c2f9bb7bbbd8b031e34eb541037997dcff9cd6885ef3f86')
    if wrapper.s is not s.base:raise ValueError('wrong service study')
    return wrapper
def main():
    wrapper=qualified_wrapper();wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
