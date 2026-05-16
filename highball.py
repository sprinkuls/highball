import re
from dataclasses import dataclass
from pathlib import Path

import logging
import sys
import os
from dotenv import load_dotenv
import mercari


# ok so like mutable java record?
@dataclass
class Search:
    search_name: str
    search_terms: list[str]


# const
# TODO: this should probably not be local to the file running
DATA_PATH = Path("seenIDs.txt")  # where we want store IDs after the program closes

# global state (but like it's actually globally relevant
logger = logging.getLogger(__name__)
seen_ids: set[str] = set()  # store the products we've already seen so we don't re-check them
user_searches: list[Search] = []  # list of dicts


# "bootstrap" highball, basically just set things up for the rest of the program, get into a known good state.
# if this is the first run of the program, should set up from the user's searches
# if it's not, then we should read the data we've previously seen from file.
def startup():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                seen_ids.add(line.strip())
    else:
        for search in user_searches:
            print(f"\"{search.search_name}\"'s results:")
            for term in search.search_terms:
                ids = mercari.get_ids_from_search(term)
                if ids is None:
                    # TODO: put retry logic here
                    raise Exception
                print(term, "\tids:", ids[:3])
                seen_ids.update(ids)


def shutdown():
    with open(DATA_PATH, "w") as f:
        for id in seen_ids:
            f.write(f"{id}\n")


def main():
    # "bootstrap" process. basically, we want to keep a list of "seen" listings on disk for if/when this program
    # closes. then, when it runs again, we load this list back into memory.

    # so already, when the program begins, we'll need some list of searches that the user wants to make.
    # well, actually, it might be best to have some way to like "add a search term", where all we do is
    # read in all the ids currently on the results page, then save them to the big seen_ids set.

    # clearly just store searches as dicts, right?
    # then we can easily write these as JSON and read them back in without any trouble.
    test_search = Search('Pro1', ['PD-KB300', 'PD-KB300NL', 'PD-KB300B', 'PD-KB300BN'])
    user_searches.append(test_search)

    while True:
        pass


if __name__ == '__main__':
    try:
        handler = logging.FileHandler("highball.log", mode="w", encoding="utf-8")
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.info('highball started')

        main()
    except KeyboardInterrupt:
        logger.info('highball ^Closed (interrupt')
        sys.exit(0)
