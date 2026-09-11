"""Qualified released-base service in the local V2 study namespace."""
from pathlib import Path
import study as s
def qualified_wrapper():
    with s.aliases({'study':s}):return s.load('visible_reference_service_v2',s.QUALIFIED/'service_wrapper.py','72bd90f6af3cb9fb52818a20ffc6822804a9d42a8bb9f8ed6974ad6b3173ba73')
def main():
    wrapper=qualified_wrapper();wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
