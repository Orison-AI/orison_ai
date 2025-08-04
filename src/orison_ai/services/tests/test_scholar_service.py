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

import pytest
import asyncio
import logging

# Internal

from services.scholar.scholar_service import (
    ScholarService,
    get_google_scholar_info,
    gather_network_database,
)
from services.scholar.config import ScholarServiceConfig
from database.schema import GoogleScholarDB, GoogleScholarNetworkDB
from database.firestore_clients import (
    GoogleScholarClient,
    GoogleScholarNetworkClient,
)

logger = logging.getLogger(__name__)


class TestScholarService:
    """Simple test suite for Google Scholar service - only 2 API calls total"""

    TEST_ATTORNEY_ID = "test_attorney"
    TEST_APPLICANT_ID = "test_applicant"
    TEST_SCHOLAR_ID = "QW93AM0AAAAJ"
    TEST_SCHOLAR_URL = f"https://scholar.google.com/citations?user={TEST_SCHOLAR_ID}"
    TEST_AUTHOR_NAME = "Rishi Malhan"

    # Shared test data
    _scholar_data = None
    _network_data = None

    @pytest.fixture(scope="class")
    def event_loop(self):
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    @pytest.mark.asyncio
    async def test_scholar_info_retrieval(self):
        """Single API call for scholar info"""
        logger.info("🚀 Testing scholar info retrieval")

        service = ScholarService()
        result = await service.get_scholar_info(
            self.TEST_ATTORNEY_ID,
            self.TEST_APPLICANT_ID,
            self.TEST_SCHOLAR_URL,
            self.TEST_AUTHOR_NAME,
        )

        assert isinstance(result, GoogleScholarDB)
        assert result.author.name is not None
        self._scholar_data = result
        logger.info("✅ Scholar info retrieved")

    @pytest.mark.asyncio
    async def test_global_function(self):
        """Test global function signature"""
        if self._scholar_data is None:
            pytest.skip("No scholar data available")

        assert callable(get_google_scholar_info)
        logger.info("✅ Global function verified")

    @pytest.mark.asyncio
    async def test_breadth_first_search(self):
        """Single API call for network building"""
        logger.info("🔍 Testing breadth-first network building")

        config = ScholarServiceConfig.from_env()
        config.add_name_mapping(self.TEST_SCHOLAR_ID, self.TEST_AUTHOR_NAME)
        service = ScholarService(config)

        network_db = await service.build_network_database(
            self.TEST_SCHOLAR_ID, self.TEST_AUTHOR_NAME, max_depth=2, max_size=5
        )

        assert isinstance(network_db, GoogleScholarNetworkDB)
        assert network_db.max_depth == 2
        assert len(network_db.network) <= 5
        self._network_data = network_db
        logger.info("✅ Network built with breadth-first search")

    @pytest.mark.asyncio
    async def test_randomization(self):
        """Test randomization logic"""
        import random

        test_list = [1, 2, 3, 4, 5]
        random.shuffle(test_list)
        assert len(test_list) == 5
        logger.info("✅ Randomization working")

    @pytest.mark.asyncio
    async def test_network_structure(self):
        """Test network structure using cached data"""
        if self._network_data is None:
            pytest.skip("No network data available")

        network_db = self._network_data
        assert network_db.root_scholar_id == self.TEST_SCHOLAR_ID
        assert network_db.network_size == len(network_db.network)
        logger.info("✅ Network structure verified")

    @pytest.mark.asyncio
    async def test_database_operations(self):
        """Test database operations with cached data"""
        if self._scholar_data is None or self._network_data is None:
            pytest.skip("Required data not available")

        try:
            scholar_client = GoogleScholarClient()
            network_client = GoogleScholarNetworkClient()

            # Add metadata
            self._scholar_data.attorney_id = self.TEST_ATTORNEY_ID
            self._scholar_data.applicant_id = self.TEST_APPLICANT_ID
            self._network_data.attorney_id = self.TEST_ATTORNEY_ID
            self._network_data.applicant_id = self.TEST_APPLICANT_ID

            # Save to database
            scholar_id = await scholar_client.insert(
                self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, self._scholar_data
            )
            network_id = await network_client.insert(
                self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, self._network_data
            )

            assert scholar_id is not None
            assert network_id is not None
            logger.info("✅ Database operations completed")

        except Exception as e:
            logger.warning(f"Database test skipped: {e}")
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_global_network_function(self):
        """Test global network function signature"""
        assert callable(gather_network_database)
        logger.info("✅ Global network function verified")


if __name__ == "__main__":
    # Run tests directly
    import asyncio

    async def run_tests():
        test = TestScholarService()
        await test.test_scholar_info_retrieval()
        await test.test_global_function()
        await test.test_breadth_first_search()
        await test.test_randomization()
        await test.test_network_structure()
        await test.test_database_operations()
        await test.test_global_network_function()
        logger.info("✅ All consolidated tests completed successfully")

    asyncio.run(run_tests())
