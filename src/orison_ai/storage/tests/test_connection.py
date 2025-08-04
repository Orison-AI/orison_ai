#!/usr/bin/env python3.11

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
from qdrant_client import QdrantClient

# Internal

from core.config import VectorConfig
from core.environment import get_env

logger = logging.getLogger(__name__)


class TestQdrantConnection:
    """Test Qdrant vector database connection"""

    def setup_method(self):
        """Setup test configuration"""
        env = get_env()
        self.config = VectorConfig(
            collection_name="test_collection",
            url=env.qdrant_url,
            api_key=env.qdrant_api_key,
        )
        self.client = None

    def teardown_method(self):
        """Cleanup after test"""
        if self.client:
            try:
                self.client.delete_collection("test_collection")
            except:
                pass

    def test_qdrant_connection(self):
        """Test basic Qdrant connection and collection operations"""
        logger.info("Testing Qdrant connection and collection operations")

        # Connect to Qdrant
        self.client = QdrantClient(
            url=self.config.url,
            api_key=self.config.api_key,
            port=self.config.port,
            grpc_port=self.config.grpc_port,
            https=self.config.https,
            timeout=self.config.timeout,
        )

        # Test collection creation
        self.client.create_collection(
            collection_name="test_collection",
            vectors_config={"size": 1536, "distance": "Cosine"},
        )

        # Verify collection exists
        collections = self.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        assert "test_collection" in collection_names

        # Test collection deletion
        self.client.delete_collection("test_collection")

        # Verify collection deleted
        collections = self.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        assert "test_collection" not in collection_names

        logger.info("Qdrant connection test completed successfully")
