import requests as r
import argparse as ag
from bs4 import BeautifulSoup
from urllib.parse import unquote

from pprint import pprint

def reachable(link:str): # if reachable, return page information; else returns a falsy value
    try:
        with r.get(link) as response:
            return response.content if response.status_code == 200 else None
    except r.RequestException as e:
        print(e)
        return None

if __name__ == '__main__':
    # parse args
    ap = ag.ArgumentParser("Computes the Wikipedia Distance between two articles.")
    ap.add_argument("link1", help="Starting wikipedia link, ex: https://en.wikipedia.org/wiki/Alphabet_(formal_languages)")
    ap.add_argument("link2", help="Target wikipedia link, ex: https://en.wikipedia.org/wiki/German_Empire")
    ap.add_argument("-d", "--dist", default=6)
    args = vars(ap.parse_args())
    link1 = args["link1"]
    link2 = args["link2"]
    dist = args["dist"]

    # check if the two links are reachable
    data_link_1 = reachable(unquote(link1))
    data_link_2 = reachable(unquote(link2))
    if not data_link_1: print(f"{link1} is unreachable!"); exit(1)
    if not data_link_1: print(f"{link2} is unreachable!"); exit(1)

