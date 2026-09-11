"""Registered wrapper for the already qualified released-base launcher."""
from pathlib import Path
import study as s
def main():
 with s.aliases({'study':s.prior}):wrapper=s.load('balanced_tag_service',s.PRIOR/'service_wrapper.py','e0962269de54f9ddc758aaa11d435f09e2ae7f5e4f3202fe75c9102bf7b62653')
 wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
