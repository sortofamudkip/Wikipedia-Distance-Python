# Wikipedia Distance

A small project that finds the Wikipedia distance between articles. Inspired by [Six Degrees of Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Six_degrees_of_Wikipedia).

The **Wikipedia distance** between articles A and B is defined as: starting from A, the number of links required to reach B. Another way to put this is the number or articles in between A and B, plus one.

Note that by this definition, the Wikipedia distance between two articles is **not** unique. If it is possible to reach B from A in 2 or 5 links, then those are both valid distances.

For example, the Wikipedia Distance between `Mongolia` and `Vintage_Wings_of_Canada` is 3, because of the link chain `Mongolia` -> `Ottawa` -> `Gatineau-Ottawa_Executive_Airport` -> `Vintage_Wings_of_Canada`.

This project utilizes Wikipedia's API and Python 3 to implement BFS and DFS, two common search algorithms, on Wikipedia articles.

## Modules used
* Builtin: `argparse`, `urllib`, `queue`, `pprint` (the latter for debugging)
* External: `requests`

## Environment
* Python 3

## Usage
```
python main.py link1 link2
```
Where `link1` is the starting article, and `link2` is the target article. 

Example: 
```
python main.py Mongolia Vintage_Wings_of_Canada
```

Additional flags:
* `-p` or `--policy`: either `bfs` or `dfs` (default).
* `-d` or `--dist`: maximum recursion depth for DFS. Default at 3.

Full example:
```
python main.py Mongolia Vintage_Wings_of_Canada -p DFS -d 6
```

## How it works
Wikipedia articles are usually accessed by their title, but they are not uniquely defined. For example the titles `Greenhouse_gas` and `Greenhouse_gases` refer to the same article. `Greenhouse_gases` is a redirect, which will make searching more tedious.

Thus to obtain an article, we first follow all redirects then obtain its `pageid`, which is unique.

The code itself heavily uses the following functions:

### `get_pageID(title)`
Given a title, follow all redirects and return its pageID and search status. If `good` is `True`, then the search was successful, otherwise the page's ID cannot be found, i.e. page itself doesn't exist.

### `get_links(title)`
Given a title, return a list of all the titles the article links to, along with search status. Note that it returns *titles*, not pageIDs. If `good` is `True`, then the search was successful, otherwise the page's articles could not be found.

For every element returned, you need to call `get_pageID` to get its ID.

### `BFS(start)`
Standard BFS search, with the nodes being the article names. As Wikipedia links are unweighted edges, BFS is guaranteed to find the shortest Wikipedia distance. Note that `start` is a **pageID**.

If a path is found, it returns the path as a list of titles; else it returns `False`.

Much, much slower compared to DFS, as it needs to find _every_ neighbours' pageID because it can move onto the next layer.

### `DFS(start, depth, path, seen)`
Standard DFS search. Not guaranteed to do find the shortest distance, but faster.

If a path is found, it returns the path as a list of titles; else it returns `False`.

