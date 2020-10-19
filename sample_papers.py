import glob
import json
import os
import random
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple

DATA_DIR = "data"


# Seed random number generator for replicability
random.seed(42)


# Pair of conference nickname and year
ConferenceId = Tuple[str, int]


# For every conference in this list, it is expected that the data directory includes either
# * a file with the name '<conf-name>-<year>.json' or
# * a series of files with the names '<conf-name>-<year>-<part-number>.json'
#
# The data in each of these files was downloaded by going to DBLP and querying
# the API, and then copying and pasting the output JSON files into the `data/` directory.
# For instance, a list of papers at ACL in 2017 can be searched with this URL:
# https://dblp.org/search/publ/api?q=venue%3AACL%3A%20year%3A2017%3A&h=1000&format=json
# The DBLP API can only return 1000 papers at a time, which is a problem for recent
# conferences like NeurIPS which have over 1000 papers. For those conferences, data
# needs to be downloaded in multiple requests. To get the second set of 1000 papers
# at a conference, at the paging parameter `f=<page-start>` to the query like so:
# https://dblp.org/search/publ/api?q=venue%3ANeurIPS%3A%20year%3A2019%3A&h=1000&format=json&f=1000
CONFERENCES: List[ConferenceId] = [
    ("neurips", 2017),
    ("neurips", 2018),
    ("neurips", 2019),
    ("icml", 2017),
    ("icml", 2018),
    ("icml", 2019),
    ("acl", 2017),
    ("acl", 2018),
    ("acl", 2019),
    ("cvpr", 2017),
    ("cvpr", 2018),
    ("cvpr", 2019),
]


papers: Dict[ConferenceId, List[Any]] = defaultdict(list)


for conference in CONFERENCES:

    name, year = conference
    conference_glob = os.path.join(DATA_DIR, f"{name}-{year}*.json")

    for path in glob.glob(conference_glob):
        print("Reading conference data from ", path)

        with open(path) as file_:
            data = json.load(file_)
            papers[(name, year)].extend(data["result"]["hits"]["hit"])

    num_read = len(papers[(name, year)])
    print(f"Loaded data for {num_read} papers for conference {name}-{year}")


sample: Dict[ConferenceId, List[Any]] = {}
PAPERS_PER_CONFERENCE = 10


for conference_id, conference_papers in papers.items():
    sample[conference_id] = random.sample(conference_papers, PAPERS_PER_CONFERENCE)


print("")
for (conference_name, conference_year), conference_sample in sample.items():
    print(f"Papers sampled for {conference_name}-{conference_year}:")
    for paper in conference_sample:
        title = paper["info"]["title"]
        try:
            start_page, end_page = [int(_) for _ in paper["info"]["pages"].split("-")]
            num_pages = end_page - start_page
            print(f"'{title}' ({num_pages} pages)")
        except ValueError:
            print(f"(Error: could not parse number of pages for '{title}')")
    print("")
