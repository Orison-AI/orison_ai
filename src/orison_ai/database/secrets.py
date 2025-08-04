#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2025.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal opyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

# External

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OrisonSecrets:
    """Secret management using centralized environment"""

    openai_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    collection_name: str

    @classmethod
    def from_attorney_applicant(cls, attorney_id: str, applicant_id: str):
        """Create secrets from attorney and applicant IDs"""

        # Internal

        from orison_ai.core.environment import get_env

        env = get_env()
        return cls(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name=f"{attorney_id}_{applicant_id}_collection",
        )
