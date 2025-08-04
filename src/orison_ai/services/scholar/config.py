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

import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ScholarServiceConfig:
    """Configuration for Google Scholar service"""

    # API Configuration
    api_key: str
    base_url: str = "https://serpapi.com/search"
    timeout: int = 10

    # Search Configuration
    default_num_results: int = 20
    max_publications: int = 20
    max_coauthors: int = 10

    # Network Configuration
    default_max_depth: int = 1
    default_max_network_size: int = 10
    batch_size: int = 3
    rate_limit_delay: float = 0.5

    # Name Resolution
    name_mapping: Dict[str, str] = None

    def __post_init__(self):
        """Initialize default values"""
        if self.name_mapping is None:
            self.name_mapping = {}

    @classmethod
    def from_env(cls) -> "ScholarServiceConfig":
        """Create config from environment variables"""
        api_key = os.getenv("SERPAPI_KEY")
        if not api_key:
            raise ValueError("SERPAPI_KEY environment variable is required")

        return cls(
            api_key=api_key,
            default_max_depth=int(os.getenv("SCHOLAR_MAX_DEPTH", "1")),
            default_max_network_size=int(os.getenv("SCHOLAR_MAX_NETWORK_SIZE", "50")),
            timeout=int(os.getenv("SCHOLAR_TIMEOUT", "10")),
            default_num_results=int(os.getenv("SCHOLAR_NUM_RESULTS", "20")),
        )

    def get_author_name(self, scholar_id: str) -> str:
        """Get author name from scholar ID using mapping"""
        return self.name_mapping.get(scholar_id, "Unknown")

    def add_name_mapping(self, scholar_id: str, name: str):
        """Add a name mapping for a scholar ID"""
        self.name_mapping[scholar_id] = name

    def add_name_mappings(self, mappings: Dict[str, str]):
        """Add multiple name mappings"""
        self.name_mapping.update(mappings)
