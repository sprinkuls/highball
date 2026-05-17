import re
from dataclasses import dataclass
from pathlib import Path

import logging
import sys
import os

import requests
from dotenv import load_dotenv
from time import sleep

import mercari


# ok so like mutable java record
@dataclass
class Search:
    search_name: str
    search_terms: list[str]


# const values
# TODO: this should probably not be local to the file running
DATA_PATH = Path("seenIDs.txt")  # where we want store IDs after the program closes
TIME_BETWEEN_REQUESTS = 0.5  # time between each search request (so the server doesn't yell at you)

# global state (but like it's actually globally relevant)
logger = logging.getLogger(__name__)
seen_ids: set[str] = set()  # store the products we've already seen so we don't re-check them
user_searches: list[Search] = []  # list of dicts


# "bootstrap" highball, basically just set things up for the rest of the program, get into a known good state.
# if this is the first run of the program, should set up from the user's searches
# if it's not, then we should read the data we've previously seen from file.
def startup():
    print("starting up...")
    if DATA_PATH.exists():
        with open(DATA_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                print(line.strip())
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
                sleep(TIME_BETWEEN_REQUESTS)


def shutdown():
    print("shutting down...")
    with open(DATA_PATH, "w") as f:
        for id in seen_ids:
            f.write(f"{id}\n")


# TODO
def is_correct_item(item_listing: mercari.Listing) -> bool:
    return True


# TODO: passing jpy_to_usd sucks
def send_notification(listing: mercari.Listing, jpy_to_usd: float) -> None:
    # specifically using environ() over getenv() so it doesn't complain that the variable might not be present
    url = os.environ['NTFY_URL']
    token = os.environ["NTFY_TOKEN"]
    requests.post(
        url,
        data=f"""new listing: {listing.title}
              price: {listing.price_jpy * jpy_to_usd}""",
        headers={
            "Authorization": f"Bearer {token}",
            "Markdown": "yes"
            # "Title": "",
        })


def main():
    # "bootstrap" process. basically, we want to keep a list of "seen" listings on disk for if/when this program
    # closes. then, when it runs again, we load this list back into memory.

    # so already, when the program begins, we'll need some list of searches that the user wants to make.
    # well, actually, it might be best to have some way to like "add a search term", where all we do is
    # read in all the ids currently on the results page, then save them to the big seen_ids set.

    # clearly just store searches as dicts, right?
    # then we can easily write these as JSON and read them back in without any trouble.
    test_search: Search = Search('Pro1', ['PD-KB300', 'PD-KB300NL', 'PD-KB300B', 'PD-KB300BN'])
    user_searches.append(test_search)

    hhkb_search: Search = Search('HHKB', ['hhkb'])
    user_searches.append(hhkb_search)

    keyboard_search: Search = Search('i love gaming', ['keyboard gaming'])
    user_searches.append(keyboard_search)

    startup()
    jpy_to_usd: float = mercari.get_jpy_to_usd()

    # so ok we have now, for all the user's searches, all the ids that have already been seen
    # so for each search page, every

    time_since_get_conversion_rate: int = 0  # in seconds
    time_running: int = 0  # in seconds
    time_between_checks: int = 60  # in seconds, how long to wait before checking all the searches
    while True:
        sleep(time_between_checks)
        time_running += time_between_checks

        if time_since_get_conversion_rate > (6 * 60 * 60):
            time_since_get_conversion_rate = 0
            jpy_to_usd = mercari.get_jpy_to_usd()

        new_ids: set[str] = set()  # specifically a set because multiple searches could find the same ID

        for search in user_searches:
            for search_term in search.search_terms:
                ids = mercari.get_ids_from_search(search_term)
                logger.info(f"searching for: {search_term}")

                sleep(TIME_BETWEEN_REQUESTS)
                if ids is None:
                    raise Exception  # TODO: put retry logic here

                # need to check all the ids rather than, say, the ids up to the first duplicate. that should
                # work in theory, but the issue is that sometimes when two items are added at almost the same time (or
                # maybe the exact same) they can sometimes change orders in the results. this manifests as a result
                # being skipped.
                for id_ in ids:
                    if id_ not in seen_ids:
                        new_ids.add(id_)

        if len(new_ids) == 0:
            continue

        # so now we have all the new listings, pull their pages
        new_items: list[mercari.Listing] = []
        for id_ in new_ids:
            item_listing = mercari.get_listing_from_id(id_)
            logger.info(f"getting listing page for id: {id_}")
            sleep(TIME_BETWEEN_REQUESTS)

            if item_listing is None:
                raise Exception  # TODO: put retry logic here

            if is_correct_item(item_listing):
                new_items.append(item_listing)
                print(item_listing.title, ":", item_listing.price_jpy, ":", item_listing.price_jpy * jpy_to_usd)

        if len(new_items) == 0:
            continue

        # now we have `new_items`, which contains only relevant new listings.
        # notify the user of these, and mark them as seen.
        for item in new_items:
            seen_ids.add(item.id)
            send_notification(item, jpy_to_usd)


if __name__ == '__main__':
    try:
        handler = logging.FileHandler("highball.log", mode="w", encoding="utf-8")
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.info('highball started')

        load_dotenv()

        main()
    except KeyboardInterrupt:
        shutdown()
        logger.info('highball ^Closed (interrupt')
        sys.exit(0)
