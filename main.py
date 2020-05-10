import requests as r
import argparse as ag
from urllib.parse import unquote
from queue import Queue

from pprint import pprint


# global vars
known_links = {} # pages already discovered (pageids -> linked pageids)
title_to_id = {}
id_to_title = {}
MAX_DEPTH = 3 # maximum length allowed
DEAULT_MAX_DEPTH = 3
dest_pageid = None # the pageid of the dest
SEARCH_POLICY_EXPLANATION = """
Search policies. Current policies include:
    dfs: Depth first search. Quick, but may not find the shortest path. Deafult value.
    bfs: Breadth-first search. Guaranteed to find the shortest path.
"""

def get_pageID(title:str): # given a Wikipedia title, return its page ID (which is unique since it follows redirects.)
    if title in title_to_id: return {"good": True, "contents": title_to_id[title]}
    payload = {
        "action": "query",
        "titles": title,
        "redirects": "y",
        "format": "json"
    }
    try:
        with r.get(url="https://en.wikipedia.org/w/api.php", params=payload) as response:
            json = response.json()
            if "-1" in json["query"]["pages"]: 
                return {"good": False, "contents" : f"{title} does not exist!"}
            else: 
                pageid = list(json["query"]["pages"].keys())[0]
                title_to_id[title] = pageid
                id_to_title[pageid] = title
                return {
                    "good": True, 
                    "contents" : list(json["query"]["pages"].keys())[0]
                }  
    except r.RequestException as e:
        return {"good": False, "contents": f"error while trying to get pageID of {title}: |{e}|"}


def get_links(title:str): # given a title, return all its links. Note that you still need to obtain their IDs afterwards.
    payload = {
        "action": "parse",
        "pageid":  title,
        "format": "json",
        "redirects": "y"
    }
    try:
        with r.get(url="https://en.wikipedia.org/w/api.php", params=payload) as response:
            json = response.json()
            if "error" in json: 
                return {"good": False, "contents" : json["error"]}
            else: 
                good_links = [e["*"] for e in json["parse"]["links"] if e["ns"] == 0]
                # ids = [get_pageID(link) for link in good_links]
                # return_list = [i["contents"] for i in ids if i["good"]]
                # known_links[json["parse"]["pageid"]] = return_list
                return {
                    "good": True, 
                    "contents" : {
                        "pageid": json["parse"]["pageid"],
                        "links": good_links
                    }
                }  
    except r.RequestException as e:
        return {"good": False, "contents": f"error while trying to query links of {title}: |{e}|"}


def BFS(start): # current title
    Q = Queue()
    seen = {start}
    path = {start: start}
    Q.put(start)

    while not Q.empty():
        cur = Q.get_nowait()
        print(f"at: {id_to_title[cur]}")
        if cur == dest_pageid: 
            final_path = []
            while cur != path[cur]: 
                final_path.append(id_to_title[cur])
                cur = path[cur]
            return (final_path + [id_to_title[start]])[::-1]
        data = known_links[cur] if cur in known_links else get_links(cur)
        if not data["good"]: continue # if link is somehow missing, skip it
        neighbours = data["contents"]["links"]
        for neighbour_title in neighbours:
            neighbour = get_pageID(neighbour_title)
            if not neighbour["good"]: continue
            neighbour = neighbour["contents"]
            if neighbour not in seen:
                seen.add(neighbour)
                path[neighbour] = cur
                Q.put(neighbour)
    return False

def DFS(cur, depth, path, seen):
    print("\t" * depth + "at: " + id_to_title[cur])
    if cur == dest_pageid: return path
    if depth == MAX_DEPTH: print("\t" * depth + f"reached depth limit ({MAX_DEPTH}); stopping"); return False
    seen.add(cur)
    data = known_links[cur] if cur in known_links else get_links(cur)
    if not data["good"]: return False # if link is somehow missing, skip it
    neighbours = data["contents"]["links"]
    for n_title in neighbours:
        n = get_pageID(n_title)
        if not n["good"]: continue
        n = n["contents"]
        if n not in seen:
            path.append(id_to_title[n]) # try putting n in
            search = DFS(n, depth+1, path, seen)
            if search: return search
            path.pop()
    return False

if __name__ == '__main__':
    # parse args
    ap = ag.ArgumentParser("Computes the Wikipedia Distance between two (English) articles, based on policy different policies.  \
        Please only input the name of the title, i.e. everything AFTER 'en.wikipedia.org/wiki/'.")
    ap.add_argument("link1", help="Starting Wikipedia title, ex: Alphabet_(formal_languages)")
    ap.add_argument("link2", help="Target Wikipedia title, ex: German_Empire")
    ap.add_argument("-p", "--policy", help=SEARCH_POLICY_EXPLANATION, default="dfs", choices=["bfs", "dfs"])
    ap.add_argument("-d", "--dist", default=DEAULT_MAX_DEPTH)
    args = vars(ap.parse_args())
    link1 = args["link1"]
    link2 = args["link2"]
    policy = args["policy"]
    MAX_DEPTH = args["dist"]

    # check if the two links are reachable
    data_link_1 = get_pageID(unquote(link1))
    data_link_2 = get_pageID(unquote(link2))
    if not data_link_1["good"]: print(data_link_1["contents"]); exit(1)
    if not data_link_2["good"]: print(data_link_2["contents"]); exit(1)

    start_pageid = data_link_1["contents"]
    dest_pageid = data_link_2["contents"]

    if policy == "bfs":
        result = BFS(start_pageid)
    elif policy == "dfs":
        result = DFS(start_pageid, 0, [link1], set())
    else: print("invalid policy!"); exit(1)
    print("path: " + " -> ".join(result) if result else f"No paths between {link1} and {link2}") 

    exit(0)