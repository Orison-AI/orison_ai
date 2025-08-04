"""
Google Scholar service utilities and helper functions.
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def extract_scholar_id(scholar_link: str) -> str:
    """Extract scholar ID from Google Scholar URL"""
    if not scholar_link.startswith("http"):
        scholar_link = "http://" + scholar_link

    parts = scholar_link.split("user=")
    if len(parts) < 2:
        return ""

    scholar_id = parts[1].split("&")[0]
    return scholar_id


def extract_year_from_summary(summary: str) -> str:
    """Extract year from publication summary"""
    year_match = re.search(r"(\d{4})", summary)
    return year_match.group(1) if year_match else ""


def validate_scholar_id(scholar_id: str) -> bool:
    """Validate if scholar ID format is correct"""
    if not scholar_id:
        return False
    # Google Scholar IDs are typically 12 characters long
    return len(scholar_id) == 12 and scholar_id.isalnum()


def build_scholar_url(scholar_id: str) -> str:
    """Build Google Scholar URL from scholar ID"""
    return f"https://scholar.google.com/citations?user={scholar_id}"


def parse_serpapi_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse SerpAPI response and extract common fields"""
    if data.get("error"):
        raise Exception(f"API error: {data.get('error')}")

    return {
        "profiles": data.get("profiles", {}),
        "organic_results": data.get("organic_results", []),
        "authors": data.get("profiles", {}).get("authors", []),
    }


def find_author_by_id(authors: list, target_id: str) -> Optional[Dict[str, Any]]:
    """Find author in list by scholar ID"""
    for author in authors:
        if author.get("author_id") == target_id:
            return author
    return None


def extract_publication_data(
    result: Dict[str, Any], target_scholar_id: str
) -> Dict[str, Any]:
    """Extract publication data from SerpAPI result"""
    pub_authors = result.get("publication_info", {}).get("authors", [])

    return {
        "title": result.get("title"),
        "authors": ", ".join([a.get("name", "") for a in pub_authors]),
        "abstract": result.get("snippet", ""),
        "cited_by": result.get("inline_links", {}).get("cited_by", {}).get("total", 0),
        "journal": result.get("publication_info", {}).get("summary", ""),
        "year": extract_year_from_summary(
            result.get("publication_info", {}).get("summary", "")
        ),
        "type": "Journal Article",
        "pub_authors": pub_authors,
        "is_target_author_pub": any(
            author.get("author_id") == target_scholar_id for author in pub_authors
        ),
    }


def extract_coauthors_from_publication(
    pub_authors: list, target_scholar_id: str, existing_coauthors: list
) -> list:
    """Extract coauthors from publication authors list"""
    coauthors = existing_coauthors.copy()

    for author in pub_authors:
        if author.get("author_id") != target_scholar_id:
            coauthor_exists = any(
                c.get("scholar_id") == author.get("author_id") for c in coauthors
            )
            if not coauthor_exists:
                coauthors.append(
                    {
                        "scholar_id": author.get("author_id"),
                        "name": author.get("name"),
                        "affiliation": "",
                    }
                )

    return coauthors


def create_serpapi_params(
    engine: str, query: str, api_key: str, num_results: int = 100
) -> Dict[str, Any]:
    """Create standardized SerpAPI parameters"""
    return {
        "engine": engine,
        "q": query,
        "api_key": api_key,
        "num": num_results,
    }


def log_performance(
    operation: str, start_time: float, end_time: float, success: bool = True
):
    """Log performance metrics"""
    elapsed = end_time - start_time
    status = "✅" if success else "❌"
    logger.info(f"{status} {operation} completed in {elapsed:.3f}s")
