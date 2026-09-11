"""Registered no-adapter Mistral wrapper on the qualified allocation launcher."""
from pathlib import Path
import study as s
def main():
 wrapper=s.load('mistral_qualified_wrapper',s.FREE/'service_wrapper_v3.py','4347c92894a24e357a74f8b9e372edcc4b3327532de183d9a59873331dc5a9d0',{'study':s});wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
