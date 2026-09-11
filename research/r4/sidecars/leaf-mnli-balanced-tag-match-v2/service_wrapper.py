"""Registered V2 wrapper for the qualified released-base service chain."""
from pathlib import Path
import study as s
def main():
 with s.aliases({'study':s}):wrapper=s.load('tag_match_v2_service',s.V1/'service_wrapper.py','e46ef705ab08439d03b91925bd2f6db59a364bfe64b3f7cc2cb0c56ecdc2d8a1')
 wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
