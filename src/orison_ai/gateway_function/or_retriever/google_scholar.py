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

import logging
import asyncio
from scholarly import scholarly
from concurrent.futures import ThreadPoolExecutor

# Internal

from or_store.models import GoogleScholarDB, Publication, Author
from or_retriever.helpers import (
    url_exists,
    INVALID_URL,
    stringify_keys,
    extract_user,
    INVALID_USER,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_google_scholar_info(
    attorney_id: str, applicant_id: str, scholar_link: str
):
    """
    Extract information from a Google Scholar profile.
    :param scholar_link: The link to the Google Scholar profile
    :return: A GoogleScholarDB object containing the extracted information
    """

    if not scholar_link.startswith("http"):
        scholar_link = "http://" + scholar_link

    try:
        await url_exists(scholar_link)
    except INVALID_URL as e:
        raise e

    scholar_id = await extract_user(scholar_link)
    if scholar_id is None:
        message = "No user ID found in the Google Scholar profile link."
        logger.warning(message)
        raise INVALID_USER(message)
    else:
        logger.info(f"User ID found: {scholar_id}")

    # Fetch data from the Google Scholar profile
    author = scholarly.search_author_id(scholar_id)
    # Fill the author object with more detailed information, including publications
    author = scholarly.fill(author)

    co_authors = []
    for co_author in author.get("coauthors"):
        co_authors.append(
            Author(
                scholar_id=co_author.get("scholar_id"),
                name=co_author.get("name"),
                affiliation=co_author.get("affiliation"),
            )
        )

    with ThreadPoolExecutor() as executor:
        detailed_publications = executor.map(
            lambda x: scholarly.fill(x), author.get("publications")
        )

        publications = []
        for detailed_pub in detailed_publications:
            type_of_paper = "Unknown"
            if "journal" in [
                detailed_pub.get("bib").get("citation"),
                detailed_pub.get("bib").get("publisher"),
            ]:
                type_of_paper = "Journal"
            elif "conference" in [
                detailed_pub.get("bib").get("citation"),
                detailed_pub.get("bib").get("publisher"),
            ]:
                type_of_paper = "Conference"
            elif "article" in [
                detailed_pub.get("bib").get("citation"),
                detailed_pub.get("bib").get("publisher"),
            ]:
                type_of_paper = "Article"
            publications.append(
                Publication(
                    title=detailed_pub.get("bib").get("title"),
                    authors=detailed_pub.get("bib").get("author"),
                    abstract=detailed_pub.get("bib").get("abstract"),
                    cited_by=detailed_pub.get("num_citations"),
                    forum_name=detailed_pub.get("citation"),
                    year=detailed_pub.get("bib").get("pub_year"),
                    type_of_paper=type_of_paper,
                    peer_reviews=detailed_pub.get("bib").get("journal"),
                )
            )

    return GoogleScholarDB(
        attorney_id=attorney_id,
        applicant_id=applicant_id,
        author=Author(
            profile_link=scholar_link,
            scholar_id=scholar_id,
            name=author.get("name"),
            affiliation=author.get("affiliation"),
        ),
        co_authors=co_authors,
        keywords=author.get("interests"),
        homepage=author.get("homepage"),
        cited_by=author.get("citedby"),
        cited_by_5y=author.get("citedby5y"),
        h_index=author.get("hindex"),
        h_index_5y=author.get("hindex5y"),
        cited_each_year=stringify_keys(author.get("cites_per_year")),
        publications=publications,
    )
