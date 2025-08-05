#! /usr/bin/env python3.11

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

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class LLMConfig:
    """LLM configuration settings"""

    model: str = "gpt-4o"
    embedding_model: str = "text-embedding-ada-002"
    temperature: float = 0.2
    max_tokens: int = 4096
    max_retries: int = 5
    timeout: float = 90.0
    requests_per_second: float = 7.0
    max_bucket_size: int = 1


@dataclass
class VectorConfig:
    """Vector database configuration"""

    collection_name: str
    url: str
    api_key: str
    # Search settings
    retrieval_limit: int = 10
    # Vectorization settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    min_token_size: int = 144
    # Qdrant settings
    port: int = 6333
    grpc_port: int = 6333
    https: bool = True
    timeout: int = 10
