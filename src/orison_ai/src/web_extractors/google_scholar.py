#! /usr/bin/env python3.10

# ==========================================================================
#  Copyright (c) Orison AI, 2024.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal Copyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

# External

import requests
from bs4 import BeautifulSoup
import logging
import re
import traceback
import scholar_network as sn

# Internal

from orison_ai.src.database.models import GoogleScholarDB, Publication
from orison_ai.src.utils.urls import url_exists
from orison_ai.src.utils.exceptions import INVALID_URL

logger = logging.getLogger(__name__)


def extract_user(url: str):
    """
    Extract the user ID from a Google Scholar URL.
    :param url: The Google Scholar URL
    """

    # This pattern matches 'user=' followed by any characters until a '?' or end of string
    match = re.search(r"user=([a-zA-Z0-9]+)", url)
    if match:
        return match.group(1)
    return None


def get_google_scholar_info(profile_link: str):
    """
    Extract information from a Google Scholar profile.
    :param profile_link: The link to the Google Scholar profile
    :return: A GoogleScholarDB object containing the extracted information
    """

    if not profile_link.startswith("http"):
        profile_link = "http://" + profile_link

    try:
        url_exists(profile_link)
    except INVALID_URL as e:
        raise e

    user_id = extract_user(profile_link)
    if user_id is None:
        logger.warning("No user ID found in the Google Scholar profile link.")
        return None

    sn.scrape_single_author(scholar_id=user_id, preferred_browser="chrome")

    # # Fetch search results from Google
    # headers = {"User-Agent": "Mozilla/5.0"}

    # # Fetch data from the Google Scholar profile
    # response = requests.get(profile_link, headers=headers)
    # soup = BeautifulSoup(response.text, "html.parser")

    # # Extract basic information
    # name = soup.find("div", {"id": "gsc_prf_in"}).text.strip()
    # designation = soup.find("div", {"class": "gsc_prf_il"}).text.strip()

    # # Extract number of citations
    # citations = soup.find("td", {"class": "gsc_rsb_std"}).text.strip()

    # # Extract publications and their citations
    # publications = []
    # for row in soup.find_all("tr", {"class": "gsc_a_tr"}):
    #     title = row.find("a", {"class": "gsc_a_at"}).text.strip()
    #     authors = row.find("div", {"class": "gs_gray"}).text.strip()
    #     cited_by = row.find("a", {"class": "gsc_a_ac"}).text.strip()
    #     publications.append(
    #         Publication(title=title, authors=authors, citations_received=cited_by)
    #     )

    # return GoogleScholarDB(
    #     name=name,
    #     designation=designation,
    #     total_citations=citations,
    #     publications=publications,
    # )
    return None


if __name__ == "__main__":
    scholar_link = "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao"

    info = get_google_scholar_info(scholar_link)
    logger.info(f"Google Scholar info: {info}")
