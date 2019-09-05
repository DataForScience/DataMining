#!/usr/bin/env python

import requests
import sys
from bs4 import BeautifulSoup
import wget
import os

url_base = "https://dumps.wikimedia.org/"
allowed_files = ["stub-meta-history.xml.gz",
                 "geo_tags.sql.gz",
                 "langlinks.sql.gz",
                 ]

allowed_wikis = ["acewiki"]

def get_page(url):
    page = requests.get(url)

    if page.status_code != 200:
        print("Error opening URL:", url, file=sys.stderr)
        return

    soup = BeautifulSoup(page.content, "lxml")

    return soup


def get_files(url):
    global url_base
    soup = get_page(url)

    file_count = 0

    for file_detail in soup.findAll("li", attrs={"class": "file"}):
        link = file_detail.find("a")

        for file in allowed_files:
            if link["href"].endswith(file):
                file_url = url_base + link["href"]

                if not os.path.exists(os.path.basename(link["href"])):
                    print("\n", file_url, file=sys.stderr)
                    wget.download(file_url)
                    file_count += 1

    if file_count == 0:
        print("\nDidn't find any files in", url, file=sys.stderr)
    else:
        print("\nDownloaded", file_count, "files from", url, file=sys.stderr)

if __name__ == "__main__":
    print("Looking for", " ".join(allowed_files), "in", " ".join(allowed_wikis), file=sys.stderr)
    url = os.path.join(url_base, "backup-index-bydb.html")
    soup = get_page(url)

    for item in soup.findAll("li"):
        span = item.find("span")

        if span is None or span["class"] != ["done"]:
            continue

        link = item.find("a")

        if link is None or not link.text.endswith("wiki"):
            continue

        if link.text not in allowed_wikis:
            continue

        url = os.path.join(url_base, link["href"])

        get_files(url)
