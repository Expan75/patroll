import os
import pandas as pd
import requests as reqs
from bs4 import BeautifulSoup

DATA_DIR = "data/raw"
FILENAME = "active_patents.csv"


def format_query_url(page_n=1, n_results=100):
    """formats a query for given page_n (paginated page of result) given a page number n_results per page

    Args:
        page_n int: page number to fetch results from. Indexed from 1, defaults to 1.
        n_results int: number of results per page. Defaults to 100.

    Returns:
        string of formatted url /w queries for given page
    """
    return f"https://tc.prv.se/spd/search?hits=true&inforce=TRUE&tab=2&from=01012016&lang=en&start={page_n * n_results}&range={n_results}"


def parse_row(row):
    data = [
        td.text.strip().replace("  ", "").replace("\n", "").replace("\r", "")
        for td in row.find_all("td")
    ]
    return data


# config setup request loop
current_page = 1
cache = set()

while True:
    print(f"Sending GET for page: {current_page}...")

    # format url and send request
    url = format_query_url(page_n=current_page)
    req = reqs.get(url)

    # write data to file given valid request and data hasn't already been mined
    if req.status_code == 200:
        soup = BeautifulSoup(markup=req.text, features="lxml")
        rows = soup.find_all("tr")
        # transform into 2dim array, skip header and pagination row (first and last)
        data = []
        for row in rows[1:-1]:
            row_data = parse_row(row)[2:]
            # encase title in single brackets
            row_data[2] = "'" + row_data[2] + "'"
            data.append(",".join(row_data))

        # also skips first to datapoints in each row (number & img if active)
        # get hash of first parsed row
        try:
            row_hash = hash(data[0])
        except IndexError:
            # implies no results were found on page, break loop
            print(
                f"Couldn't get first row of data on page {current_page}. Assumed to have traversed last page, shutting down..."
            )
            break

        # check if data exists in cache, if not add it
        if row_hash in cache:
            print("data already mined, Shutting down query loop...")
            # assumes we've gone through all results and got redirected to front page
            break
        else:
            cache.add(row_hash)

        # setup file write append
        filepath = os.path.join(DATA_DIR, FILENAME)
        with open(filepath, "a+") as f:
            f.writelines(data)
    else:
        f"no successful request was made for page: {current_page}. Shutting down query loop..."
        break

    current_page += 1

print("exiting gracefully...")