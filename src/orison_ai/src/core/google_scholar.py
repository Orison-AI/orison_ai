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
import re
import asyncio
import traceback
from scholarly import scholarly

# Internal

from orison_ai.src.database.models import GoogleScholarDB, Publication, Author
from orison_ai.src.utils.urls import url_exists
from orison_ai.src.utils.exceptions import INVALID_URL
from orison_ai.src.utils.data_utils import stringify_keys
from orison_ai.src.database.google_scholar_client import GoogleScholarClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def extract_user(url: str):
    """
    Extract the user ID from a Google Scholar URL.
    :param url: The Google Scholar URL
    """

    match = re.search(r"user=([a-zA-Z0-9]+)", url)
    if match:
        applicant_id = match.group(1)
        return applicant_id
    return None


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
        logger.warning("No user ID found in the Google Scholar profile link.")
        return None
    else:
        logger.info(f"User ID found: {scholar_id}")

    # Fetch data from the Google Scholar profile
    author = await asyncio.to_thread(scholarly.search_author_id, scholar_id)
    # Fill the author object with more detailed information, including publications
    author = await asyncio.to_thread(scholarly.fill, author)

    co_authors = []
    for co_author in author.get("coauthors"):
        co_authors.append(
            Author(
                scholar_id=co_author.get("scholar_id"),
                name=co_author.get("name"),
                affiliation=co_author.get("affiliation"),
            )
        )

    async def get_publication_details_async(publication):
        loop = asyncio.get_running_loop()
        # Run the synchronous function in a default executor (ThreadPoolExecutor)
        detailed_publication = await loop.run_in_executor(
            None, lambda x: scholarly.fill(x), publication
        )
        return detailed_publication

    tasks = [
        asyncio.create_task(get_publication_details_async(publication))
        for publication in author.get("publications")
    ]
    detailed_publications = await asyncio.gather(*tasks)

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


if __name__ == "__main__":
    applicant_id = "rmalhan"
    attorney_id = "demo_v2"
    client = GoogleScholarClient()
    scholar_link = "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao"

    if scholar_link != "":
        try:
            scholar_info = asyncio.run(
                get_google_scholar_info(
                    applicant_id=applicant_id,
                    attorney_id=attorney_id,
                    scholar_link=scholar_link,
                )
            )
        except Exception as e:
            print(
                f"Failed to generate google scholar database. Error: {traceback.format_exc(e)}"
            )
        if scholar_info is not None:
            asyncio.run(client.insert(scholar_info))
