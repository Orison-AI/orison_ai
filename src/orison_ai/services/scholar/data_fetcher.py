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

import asyncio
import logging
import requests
from typing import Dict, Any, List

# Internal

from services.scholar.config import ScholarServiceConfig
from services.scholar.utils import (
    parse_serpapi_response,
    find_author_by_id,
    extract_publication_data,
    extract_coauthors_from_publication,
    create_serpapi_params,
    log_performance,
)

logger = logging.getLogger(__name__)


class ScholarDataFetcher:
    """Handles data fetching from SerpAPI"""

    def __init__(self, config: ScholarServiceConfig):
        self.config = config

    async def fetch_author_data(
        self, scholar_id: str, author_name: str
    ) -> Dict[str, Any]:
        """Fetch author data from Google Scholar"""
        import time

        start_time = time.time()

        try:
            # Validate API key is loaded
            if not self.config.api_key:
                raise ValueError(
                    "SERPAPI_KEY not loaded - check environment configuration"
                )

            # Create search parameters
            params = create_serpapi_params(
                engine="google_scholar",
                query=author_name,
                api_key=self.config.api_key,
                num_results=self.config.default_num_results,
            )

            # Debug logging (mask API key)
            api_key_debug = (
                self.config.api_key[:8] + "..." + self.config.api_key[-4:]
                if self.config.api_key
                else "None"
            )
            logger.info(f"Making SerpAPI request with key: {api_key_debug}")
            logger.info(f"Request URL: {self.config.base_url}")
            logger.info(f"Query: {author_name}")

            # Make API call
            response = requests.get(
                self.config.base_url, params=params, timeout=self.config.timeout
            )

            # Log error responses for debugging
            if response.status_code != 200:
                logger.error(f"SerpAPI error response: {response.status_code}")
                logger.error(f"Response text: {response.text}")
                logger.error(f"Response headers: {dict(response.headers)}")

                # Retry once for 401 errors (might be cold start issue)
                if response.status_code == 401:
                    logger.warning("Retrying 401 error (possible cold start issue)...")
                    import time

                    time.sleep(1)  # Brief delay
                    response = requests.get(
                        self.config.base_url, params=params, timeout=self.config.timeout
                    )
                    if response.status_code != 200:
                        logger.error(f"Retry also failed: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            # Debug: Log response structure
            logger.info(
                f"SerpAPI response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
            )
            if "error" in data:
                logger.error(f"SerpAPI returned error: {data['error']}")
            if "search_metadata" in data:
                logger.info(
                    f"Search status: {data['search_metadata'].get('status', 'Unknown')}"
                )

            # Parse response
            try:
                parsed_data = parse_serpapi_response(data)
                authors = parsed_data["authors"]
                organic_results = parsed_data["organic_results"]

                logger.info(
                    f"Parsed {len(authors)} authors and {len(organic_results)} organic results"
                )
            except Exception as parse_error:
                logger.error(f"Failed to parse SerpAPI response: {parse_error}")
                logger.error(f"Response data: {data}")
                raise

            # Find target author
            try:
                target_author = find_author_by_id(authors, scholar_id)
                logger.info(f"Target author found: {target_author is not None}")
            except Exception as find_error:
                logger.error(f"Failed to find author by ID: {find_error}")
                logger.error(f"Authors data: {authors}")
                raise

            if not target_author:
                # Try a broader search with just the scholar ID
                params = create_serpapi_params(
                    engine="google_scholar",
                    query=f"author:{scholar_id}",
                    api_key=self.config.api_key,
                    num_results=self.config.default_num_results,
                )

                response = requests.get(
                    self.config.base_url, params=params, timeout=self.config.timeout
                )
                response.raise_for_status()
                data = response.json()

                parsed_data = parse_serpapi_response(data)
                authors = parsed_data["authors"]
                organic_results = parsed_data["organic_results"]

                # Try to find the author again
                target_author = find_author_by_id(authors, scholar_id)
                if not target_author:
                    # If still not found, try to extract from organic results
                    for result in organic_results:
                        if "authors" in result:
                            for author in result["authors"]:
                                if author.get("author_id") == scholar_id:
                                    target_author = author
                                    break
                            if target_author:
                                break

                if not target_author:
                    raise ValueError(
                        f"Author with scholar ID {scholar_id} not found in API results"
                    )

            # Extract publications and coauthors
            try:
                publications, coauthors = self._process_publications(
                    organic_results, scholar_id
                )
                logger.info(
                    f"Processed {len(publications)} publications and {len(coauthors)} coauthors"
                )
            except Exception as process_error:
                logger.error(f"Failed to process publications: {process_error}")
                logger.error(f"Organic results: {organic_results}")
                raise

            result = {
                "name": target_author.get("name"),
                "affiliation": target_author.get("affiliations"),
                "email": target_author.get("email"),
                "interests": [],
                "citedby": target_author.get("cited_by"),
                "h_index": None,
                "i10index": None,
                "coauthors": coauthors,
                "publications": publications,
            }

            log_performance("Author data fetch", start_time, time.time())
            return result

        except Exception as e:
            log_performance("Author data fetch", start_time, time.time(), success=False)
            logger.error(f"Failed to fetch author data: {e}")
            raise Exception(f"Failed to fetch scholar data: {e}")

    def _process_publications(
        self, organic_results: List[Dict], target_scholar_id: str
    ) -> tuple:
        """Process publications and extract coauthors"""
        publications = []
        coauthors = []

        for result in organic_results:
            pub_data = extract_publication_data(result, target_scholar_id)

            if pub_data["is_target_author_pub"]:
                # Add publication
                publications.append(
                    {
                        "title": pub_data["title"],
                        "authors": pub_data["authors"],
                        "abstract": pub_data["abstract"],
                        "cited_by": pub_data["cited_by"],
                        "journal": pub_data["journal"],
                        "year": pub_data["year"],
                        "type": pub_data["type"],
                    }
                )

                # Extract coauthors
                coauthors = extract_coauthors_from_publication(
                    pub_data["pub_authors"], target_scholar_id, coauthors
                )

        return publications, coauthors

    async def fetch_coauthor_data(
        self, coauthor_name: str, coauthor_id: str
    ) -> Dict[str, Any]:
        """Fetch coauthor data using their name"""
        import time

        start_time = time.time()

        try:
            params = create_serpapi_params(
                engine="google_scholar",
                query=coauthor_name,
                api_key=self.config.api_key,
                num_results=self.config.default_num_results,
            )

            response = requests.get(
                self.config.base_url, params=params, timeout=self.config.timeout
            )
            response.raise_for_status()
            data = response.json()

            parsed_data = parse_serpapi_response(data)
            authors = parsed_data["authors"]
            organic_results = parsed_data["organic_results"]

            # Find target author
            target_author = find_author_by_id(authors, coauthor_id)
            if not target_author:
                return {"name": coauthor_name, "coauthors": []}

            # Extract coauthors
            _, coauthors = self._process_publications(organic_results, coauthor_id)

            result = {
                "name": target_author.get("name", coauthor_name),
                "coauthors": coauthors[: self.config.max_coauthors],
            }

            log_performance("Coauthor data fetch", start_time, time.time())
            return result

        except Exception as e:
            log_performance(
                "Coauthor data fetch", start_time, time.time(), success=False
            )
            logger.warning(f"Failed to fetch coauthor data for {coauthor_name}: {e}")
            return {"name": coauthor_name, "coauthors": []}

    async def fetch_batch_coauthors(
        self, scholar_ids: List[str], name_resolver
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch batch coauthors with rate limiting"""
        all_results = {}

        # Process in batches
        for i in range(0, len(scholar_ids), self.config.batch_size):
            batch = scholar_ids[i : i + self.config.batch_size]
            tasks = []

            for scholar_id in batch:
                # Get author name using resolver
                author_name = name_resolver(scholar_id)
                if author_name == "Unknown":
                    # For unknown names, try to fetch using a default approach
                    tasks.append(self._fetch_single_author(scholar_id, "Unknown"))
                else:
                    tasks.append(self._fetch_single_author(scholar_id, author_name))

            # Execute batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in batch_results:
                if isinstance(result, tuple) and len(result) == 2:
                    scholar_id, data = result
                    all_results[scholar_id] = data

            # Rate limiting delay
            if i + self.config.batch_size < len(scholar_ids):
                await asyncio.sleep(self.config.rate_limit_delay)

        return all_results

    async def _fetch_single_author(self, scholar_id: str, author_name: str) -> tuple:
        """Fetch single author data"""
        try:
            author_data = await self.fetch_author_data(scholar_id, author_name)
            coauthor_data = {
                "name": author_data.get("name", "Unknown"),
                "coauthors": author_data.get("coauthors", [])[
                    : self.config.max_coauthors
                ],
            }
            return scholar_id, coauthor_data
        except Exception as e:
            logger.warning(f"Failed to fetch coauthors for {scholar_id}: {e}")
            return scholar_id, {"name": "Unknown", "coauthors": []}

    async def _create_unknown_result(self, scholar_id: str) -> tuple:
        """Create result for unknown author"""
        return scholar_id, {"name": "Unknown", "coauthors": []}
