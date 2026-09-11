"""Qualified released-base service wrapper in the local study namespace."""
from pathlib import Path
import study as s
def qualified_wrapper():
    with s.aliases({'study':s}):wrapper=s.load('new_context_alien_service',s.ALIEN/'service_wrapper.py','edd6216899b3c7dc276b885742d29bf9946bac383cd04bee59762cde9e5964b7')
    return wrapper
def main():
    wrapper=qualified_wrapper();wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
