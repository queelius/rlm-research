"""Qualified released-base service in the replication namespace."""
from pathlib import Path
import study as s
def main():
    with s.aliases({'study':s}):wrapper=s.load('field_order_replication_service',s.QUALIFIED/'service_wrapper.py','72bd90f6af3cb9fb52818a20ffc6822804a9d42a8bb9f8ed6974ad6b3173ba73')
    wrapper.__file__=str(Path(__file__).resolve());wrapper.main()
if __name__=='__main__':main()
