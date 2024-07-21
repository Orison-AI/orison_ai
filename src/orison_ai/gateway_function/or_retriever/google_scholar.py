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

    scholar_id = extract_user(scholar_link)
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


from dataclasses import dataclass
from typing import List, Dict, Set


@dataclass
class ScholarSummary:
    scholar_id: str
    publication_count: int
    hindex: int
    hindex_5y: int
    citedby: int
    citedby_5y: int
    coauthor_ids: List[str]


def summarize_scholar(scholar_id: str) -> ScholarSummary:
    # Fetch data from the Google Scholar profile
    data = scholarly.search_author_id(scholar_id)
    # Fill the author object with more detailed information, including publications
    data = scholarly.fill(data, sections=['basics', 'indices', 'coauthors', 'publications'])
    
    return ScholarSummary(
        scholar_id=scholar_id,
        publication_count=len(data.get("publications")),
        hindex=data.get("hindex"),
        hindex_5y=data.get("hindex5y"),
        citedby=data.get("citedby"),
        citedby_5y=data.get("citedby5y"),
        coauthor_ids=[co_author.get("scholar_id") for co_author in data.get("coauthors")]
    )


async def gather_network(scholar_id: str, depth: int, seen_scholar_ids: Set[str]):
    if scholar_id in seen_scholar_ids:
        # print(f"\nAlready seen scholar {scholar_id}")
        return []
    seen_scholar_ids.add(scholar_id)
    if depth == 0:
        return [summarize_scholar(scholar_id)]
    elif depth > 0:
        scholar_summary = summarize_scholar(scholar_id)
        summary = [scholar_summary]
        tasks = list(map(lambda x: gather_network(x, depth-1, seen_scholar_ids), scholar_summary.coauthor_ids))
        others = await asyncio.gather(*tasks)
        retval = []
        for item_list in others:
            for item in item_list:
                retval.append(item)
        retval.append(scholar_summary)
        return retval


async def main():
    url = "https://scholar.google.com/citations?user=pXQ4_EUAAAAJ"
    scholar_id = extract_user(url)
    # summary = summarize_scholar(scholar_id)
    seen = set()
    network = await gather_network(scholar_id, 1, seen)
    # import json
    # json.dump(summary, open("author_summary.json", "w"))
    print(network)
    print("\n")
    print(seen)

if __name__ == "__main__":
    asyncio.run(main())