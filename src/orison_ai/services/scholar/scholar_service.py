#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2025.
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
from dataclasses import dataclass
from typing import Dict, Any, List

# Internal

from orison_ai.core.environment import get_env
from orison_ai.database.schema import (
    GoogleScholarDB,
    Author,
    Publication,
    ScholarSummary,
    GoogleScholarNetworkDB,
)
from orison_ai.services.scholar.config import ScholarServiceConfig
from orison_ai.services.scholar.data_fetcher import ScholarDataFetcher
from orison_ai.services.scholar.utils import extract_scholar_id, build_scholar_url

logger = logging.getLogger(__name__)


@dataclass
class ScholarService:
    """Google Scholar service"""

    def __init__(self, config: ScholarServiceConfig = None):
        """Initialize ScholarService - actual initialization happens when needed"""
        self.env = get_env()
        self.config = config or ScholarServiceConfig.from_env()
        self.data_fetcher = None

    def _initialize(self):
        """Initialize all components"""
        if self.data_fetcher is None:
            self.data_fetcher = ScholarDataFetcher(self.config)

    async def get_scholar_info(
        self,
        attorney_id: str,
        applicant_id: str,
        scholar_link: str,
        author_name: str = None,
    ) -> GoogleScholarDB:
        """Get scholar information"""
        # Initialize components if needed
        if self.data_fetcher is None:
            self._initialize()

        scholar_id = extract_scholar_id(scholar_link)
        if not scholar_id:
            raise ValueError(f"Invalid scholar URL: {scholar_link}")

        # Use provided author name or get from config
        if not author_name:
            author_name = self.config.get_author_name(scholar_id)
            if author_name == "Unknown":
                raise ValueError(
                    f"Author name not provided and not found in mapping for scholar ID: {scholar_id}"
                )

        # Fetch author data
        author_data = await self.data_fetcher.fetch_author_data(scholar_id, author_name)

        return self._build_scholar_db(
            attorney_id, applicant_id, scholar_link, author_data
        )

    def _build_scholar_db(
        self,
        attorney_id: str,
        applicant_id: str,
        scholar_link: str,
        author_data: Dict[str, Any],
    ) -> GoogleScholarDB:
        """Build GoogleScholarDB"""

        # Process coauthors
        coauthors = []
        for coauthor in author_data.get("coauthors", [])[: self.config.max_coauthors]:
            coauthors.append(
                Author(
                    profile_link=build_scholar_url(coauthor.get("scholar_id", "")),
                    scholar_id=coauthor.get("scholar_id"),
                    name=coauthor.get("name"),
                    affiliation=coauthor.get("affiliation"),
                )
            )

        # Process publications
        publications = []
        for pub_data in author_data.get("publications", []):
            publications.append(
                Publication(
                    title=pub_data.get("title"),
                    authors=pub_data.get("authors"),
                    abstract=pub_data.get("abstract", ""),
                    cited_by=pub_data.get("cited_by", 0),
                    forum_name=pub_data.get("journal", ""),
                    year=pub_data.get("year", ""),
                    type_of_paper=pub_data.get("type", "Unknown"),
                    peer_reviews=pub_data.get("journal", ""),
                )
            )

        return GoogleScholarDB(
            attorney_id=attorney_id,
            applicant_id=applicant_id,
            author=Author(
                profile_link=scholar_link,
                scholar_id=extract_scholar_id(scholar_link),
                name=author_data.get("name"),
                affiliation=author_data.get("affiliation"),
                email=author_data.get("email"),
                interests=author_data.get("interests", []),
                cited_by=author_data.get("citedby"),
                h_index=author_data.get("h_index"),
                i10_index=author_data.get("i10index"),
            ),
            co_authors=coauthors,
            publications=publications,
        )

    async def build_network(
        self,
        root_scholar_id: str,
        author_name: str,
        max_depth: int = None,
        max_size: int = None,
    ) -> List[ScholarSummary]:
        """Build scholar network"""
        # Initialize components if needed
        if self.data_fetcher is None:
            self._initialize()

        max_depth = max_depth or self.config.default_max_depth
        max_size = max_size or self.config.default_max_network_size

        network = []
        queue = [(root_scholar_id, 0)]  # (scholar_id, depth)
        processed = {root_scholar_id}
        # Store co-author names we already have
        coauthor_names = {}

        logger.info(f"Building network: max_depth={max_depth}, max_size={max_size}")

        while queue and len(network) < max_size:
            current_batch = []

            # Process in batches to utilize parallelization
            batch_size = min(5, len(queue))  # Process up to 5 at once
            for _ in range(batch_size):
                if not queue:
                    break
                scholar_id, depth = queue.pop(0)

                if depth < max_depth:
                    current_batch.append(scholar_id)

            if not current_batch:
                break

            # Fetch batch data in parallel
            if current_batch == [root_scholar_id]:
                # For root scholar, use the provided author name
                root_author_data = await self.data_fetcher.fetch_author_data(
                    root_scholar_id, author_name
                )
                batch_results = {
                    root_scholar_id: {
                        "name": root_author_data.get("name", author_name),
                        "coauthors": root_author_data.get("coauthors", [])[
                            : self.config.max_coauthors
                        ],
                    }
                }
            else:
                # For other scholars, use stored names or config mapping
                def name_resolver(scholar_id):
                    return coauthor_names.get(
                        scholar_id, self.config.get_author_name(scholar_id)
                    )

                batch_results = await self.data_fetcher.fetch_batch_coauthors(
                    current_batch, name_resolver
                )

            for scholar_id, coauthors in batch_results.items():
                # Add to network
                network.append(
                    ScholarSummary(
                        scholar_id=scholar_id, name=coauthors.get("name", "Unknown")
                    )
                )

                # Add coauthors to queue for next depth level
                if len(network) < max_size:
                    for coauthor in coauthors.get("coauthors", [])[
                        : self.config.max_coauthors
                    ]:
                        coauthor_id = coauthor.get("scholar_id")
                        coauthor_name = coauthor.get("name", "")
                        if (
                            coauthor_id
                            and coauthor_id not in processed
                            and coauthor_name != "Unknown"
                        ):
                            # Store the co-author name for future use
                            coauthor_names[coauthor_id] = coauthor_name

                            # Fetch coauthor data using their name
                            coauthor_data = await self.data_fetcher.fetch_coauthor_data(
                                coauthor_name, coauthor_id
                            )

                            # Add coauthor to network
                            network.append(
                                ScholarSummary(
                                    scholar_id=coauthor_id,
                                    name=coauthor_data.get("name", coauthor_name),
                                )
                            )

                            # Add their coauthors to queue for next depth
                            for sub_coauthor in coauthor_data.get("coauthors", [])[:5]:
                                sub_coauthor_id = sub_coauthor.get("scholar_id")
                                sub_coauthor_name = sub_coauthor.get("name", "")
                                if (
                                    sub_coauthor_id
                                    and sub_coauthor_id not in processed
                                    and sub_coauthor_name != "Unknown"
                                ):
                                    queue.append((sub_coauthor_id, depth + 1))
                                    coauthor_names[sub_coauthor_id] = sub_coauthor_name
                                    processed.add(sub_coauthor_id)

                            processed.add(coauthor_id)

        logger.info(f"Built network of {len(network)} scholars")
        return network[:max_size]  # Ensure we don't exceed max_size

    async def build_network_database(
        self,
        root_scholar_id: str,
        author_name: str,
        max_depth: int = None,
        max_size: int = None,
    ) -> GoogleScholarNetworkDB:
        """Build complete GoogleScholarNetworkDB with detailed ScholarSummary objects"""
        # Initialize components if needed
        if self.data_fetcher is None:
            self._initialize()

        # Get the basic network
        network_summaries = await self.build_network(
            root_scholar_id, author_name, max_depth, max_size
        )

        # Build detailed ScholarSummary objects
        detailed_network = []

        for summary in network_summaries:
            try:
                # Fetch detailed author data
                if summary.scholar_id == root_scholar_id:
                    author_data = await self.data_fetcher.fetch_author_data(
                        root_scholar_id, author_name
                    )
                else:
                    # For co-authors, we need to get their name first
                    author_name_for_coauthor = summary.name
                    if author_name_for_coauthor == "Unknown":
                        # Skip unknown authors
                        continue
                    author_data = await self.data_fetcher.fetch_author_data(
                        summary.scholar_id, author_name_for_coauthor
                    )

                # Build detailed ScholarSummary
                detailed_summary = ScholarSummary(
                    name=author_data.get("name", summary.name),
                    scholar_id=summary.scholar_id,
                    citations=author_data.get("citedby", 0),
                    h_index=author_data.get("h_index", 0),
                    publication_count=len(author_data.get("publications", [])),
                    affiliation=author_data.get("affiliation", ""),
                    email=author_data.get("email", ""),
                    interests=author_data.get("interests", []),
                    i10_index=author_data.get("i10index", 0),
                    profile_link=build_scholar_url(summary.scholar_id),
                )
                detailed_network.append(detailed_summary)

            except Exception as e:
                logger.warning(
                    f"Failed to get detailed data for {summary.scholar_id}: {e}"
                )
                # Add basic summary if detailed fetch fails
                basic_summary = ScholarSummary(
                    name=summary.name,
                    scholar_id=summary.scholar_id,
                    citations=0,
                    h_index=0,
                    publication_count=0,
                    affiliation="",
                    email="",
                    interests=[],
                    i10_index=0,
                    profile_link=build_scholar_url(summary.scholar_id),
                )
                detailed_network.append(basic_summary)

        # Build the network database
        network_db = GoogleScholarNetworkDB(
            attorney_id="",  # Will be set by caller
            applicant_id="",  # Will be set by caller
            network=detailed_network,
            root_scholar_id=root_scholar_id,
            root_scholar_name=author_name,
            network_size=len(detailed_network),
            max_depth=max_depth or self.config.default_max_depth,
        )

        return network_db


# Global service instance with default config
_service = ScholarService()


async def get_google_scholar_info(
    attorney_id: str, applicant_id: str, scholar_link: str, author_name: str = None
) -> GoogleScholarDB:
    """Get Google Scholar info"""
    return await _service.get_scholar_info(
        attorney_id, applicant_id, scholar_link, author_name
    )


async def gather_network(
    root_scholar_id: str, author_name: str, max_depth: int = None, max_size: int = None
) -> List[ScholarSummary]:
    """Build network"""
    return await _service.build_network(
        root_scholar_id, author_name, max_depth, max_size
    )


async def gather_network_database(
    root_scholar_id: str, author_name: str, max_depth: int = None, max_size: int = None
) -> GoogleScholarNetworkDB:
    """Build complete network database"""
    return await _service.build_network_database(
        root_scholar_id, author_name, max_depth, max_size
    )


def extract_user(scholar_link: str) -> str:
    """Extract user ID from scholar link"""
    return extract_scholar_id(scholar_link)
