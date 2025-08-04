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
import time
import logging

# Internal

from orison_ai.services.scholar.scholar_service import (
    ScholarService,
    get_google_scholar_info,
    gather_network,
    gather_network_database,
)
from orison_ai.services.scholar.config import ScholarServiceConfig
from orison_ai.database.schema import GoogleScholarDB, GoogleScholarNetworkDB
from orison_ai.database.firestore_clients import (
    GoogleScholarClient,
    GoogleScholarNetworkClient,
)

logger = logging.getLogger(__name__)


class TestScholarService:
    """Consolidated test suite for Google Scholar service and database operations"""

    TEST_ATTORNEY_ID = "test_attorney"
    TEST_APPLICANT_ID = "test_applicant"
    TEST_SCHOLAR_ID = "QW93AM0AAAAJ"
    TEST_SCHOLAR_URL = f"https://scholar.google.com/citations?user={TEST_SCHOLAR_ID}"
    TEST_AUTHOR_NAME = "Rishi Malhan"

    # Shared test data to avoid duplicate API calls
    _scholar_data = None
    _network_data = None

    @pytest.fixture(scope="class")
    def event_loop(self):
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    @pytest.mark.asyncio
    async def test_scholar_info_retrieval(self):
        """Test scholar info retrieval - this is the main API call that others will reuse"""
        logger.info("🚀 Starting scholar info retrieval test (main API call)")

        service = ScholarService()
        logger.info(
            f"📋 Test parameters: attorney_id={self.TEST_ATTORNEY_ID}, applicant_id={self.TEST_APPLICANT_ID}, scholar_url={self.TEST_SCHOLAR_URL}"
        )

        start_time = time.time()
        logger.info("⏱️  Initiating scholar data fetch...")

        result = await service.get_scholar_info(
            self.TEST_ATTORNEY_ID,
            self.TEST_APPLICANT_ID,
            self.TEST_SCHOLAR_URL,
            self.TEST_AUTHOR_NAME,
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify basic structure
        assert isinstance(result, GoogleScholarDB)
        assert result.author.name is not None
        assert result.author.cited_by is not None

        # Store for reuse in other tests
        self._scholar_data = result

        logger.info(f"✅ Scholar data retrieved in {elapsed:.3f}s")
        logger.info(f"📋 GoogleScholarDB: {result.to_json()}")

        # Performance assertion
        assert (
            elapsed < 5.0
        ), f"Performance test failed: {elapsed:.3f}s exceeds 5s limit"
        logger.info(f"🎯 Performance test PASSED: {elapsed:.3f}s < 5.0s")

    @pytest.mark.asyncio
    async def test_global_function_performance(self):
        """Test global function performance - reuses data from previous test"""
        logger.info("🌐 Starting global function performance test")

        # Use the data from the previous test instead of making another API call
        if self._scholar_data is None:
            pytest.skip("Skipping - scholar data not available from previous test")

        start_time = time.time()
        logger.info("⏱️  Testing global function with cached data...")

        # Test the global function but use cached data for verification
        result = await get_google_scholar_info(
            self.TEST_ATTORNEY_ID,
            self.TEST_APPLICANT_ID,
            self.TEST_SCHOLAR_URL,
            self.TEST_AUTHOR_NAME,
        )

        end_time = time.time()
        elapsed = end_time - start_time

        assert isinstance(result, GoogleScholarDB)
        assert result.author.name is not None

        logger.info(f"✅ Global function completed in {elapsed:.3f}s")

        # Performance assertion
        assert (
            elapsed < 5.0
        ), f"Global function performance test failed: {elapsed:.3f}s exceeds 5s limit"
        logger.info(
            f"🎯 Global function performance test PASSED: {elapsed:.3f}s < 5.0s"
        )

    @pytest.mark.asyncio
    async def test_network_database_building(self):
        """Test network database building - single API call for network data"""
        logger.info("🗄️ Starting network database building test")
        logger.info(
            f"📋 Network DB parameters: root_scholar_id={self.TEST_SCHOLAR_ID}, max_depth=1, max_size=10"
        )

        # Initialize service with a config that includes the name mapping
        config = ScholarServiceConfig.from_env()
        config.add_name_mapping(self.TEST_SCHOLAR_ID, self.TEST_AUTHOR_NAME)
        service = ScholarService(config)

        start_time = time.time()
        logger.info("⏱️  Initiating network database construction...")

        network_db = await service.build_network_database(
            self.TEST_SCHOLAR_ID, self.TEST_AUTHOR_NAME, max_depth=1, max_size=5
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Store for reuse in database test
        self._network_data = network_db

        logger.info(f"✅ Network database built in {elapsed:.3f}s")
        logger.info(f"🗄️ GoogleScholarNetworkDB: {network_db.to_json()}")

        # Verify the network database structure
        assert isinstance(network_db, GoogleScholarNetworkDB)
        assert network_db.root_scholar_id == self.TEST_SCHOLAR_ID
        assert network_db.root_scholar_name == self.TEST_AUTHOR_NAME
        assert len(network_db.network) > 0
        assert network_db.network_size == len(network_db.network)
        assert network_db.max_depth == 1

        # Verify ScholarSummary objects have detailed information
        for scholar in network_db.network:
            assert scholar.name is not None
            assert scholar.scholar_id is not None
            assert scholar.profile_link is not None
            assert "scholar.google.com" in scholar.profile_link

        # Performance assertion
        assert (
            elapsed < 15.0
        ), f"Network database building performance test failed: {elapsed:.3f}s exceeds 15s limit"
        logger.info(f"🎯 Network database building test PASSED: {elapsed:.3f}s < 15.0s")

    @pytest.mark.asyncio
    async def test_database_operations(self):
        """Test saving scholar and network data to database - uses cached data"""
        logger.info("💾 Starting database operations test")

        # Use cached data from previous tests
        if self._scholar_data is None or self._network_data is None:
            pytest.skip("Skipping - required data not available from previous tests")

        try:
            # Initialize Firestore clients
            scholar_client = GoogleScholarClient()
            network_client = GoogleScholarNetworkClient()

            # 1. Save scholar data
            logger.info("📚 Saving scholar data to database...")
            start_time = time.time()

            # Add metadata to scholar data
            scholar_db = self._scholar_data
            scholar_db.attorney_id = self.TEST_ATTORNEY_ID
            scholar_db.applicant_id = self.TEST_APPLICANT_ID

            # Save to database
            scholar_id = await scholar_client.insert(
                self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, scholar_db
            )
            scholar_time = time.time() - start_time

            logger.info(f"✅ Scholar data saved in {scholar_time:.3f}s")
            logger.info(f"📋 Scholar DB ID: {scholar_id}")

            # 2. Save network data
            logger.info("🌐 Saving network data to database...")
            start_time = time.time()

            # Add metadata to network data
            network_db = self._network_data
            network_db.attorney_id = self.TEST_ATTORNEY_ID
            network_db.applicant_id = self.TEST_APPLICANT_ID

            # Save to database
            network_id = await network_client.insert(
                self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, network_db
            )
            network_time = time.time() - start_time

            logger.info(f"✅ Network data saved in {network_time:.3f}s")
            logger.info(f"📋 Network DB ID: {network_id}")
            logger.info(f"📋 Network Size: {network_db.network_size} scholars")

            # 3. Summary
            total_time = scholar_time + network_time
            logger.info("🎯 Database Operations Summary:")
            logger.info(f"   • Scholar data save: {scholar_time:.3f}s")
            logger.info(f"   • Network data save: {network_time:.3f}s")
            logger.info(f"   • Total save time: {total_time:.3f}s")
            logger.info(f"   • Scholar DB ID: {scholar_id}")
            logger.info(f"   • Network DB ID: {network_id}")
            logger.info(f"   • Network scholars: {network_db.network_size}")

            # Verify the saved data can be retrieved
            retrieved_scholar_docs = await scholar_client.find_top_k(
                self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, k=1
            )
            assert len(retrieved_scholar_docs) > 0, "Scholar data not found in database"

            retrieved_network_docs = await network_client.find_top_k(
                self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, k=1
            )
            assert len(retrieved_network_docs) > 0, "Network data not found in database"

            logger.info("✅ Database operations test PASSED")

        except Exception as e:
            logger.error(f"❌ Database operations test failed: {e}")
            pytest.fail(f"Database operations test failed: {e}")

    @pytest.mark.asyncio
    async def test_global_network_database_function(self):
        """Test global network database building function - reuses network data"""
        logger.info("🗄️ Starting global network database function test")

        # Use cached network data if available
        if self._network_data is not None:
            logger.info("⏱️  Using cached network data for verification...")

            # Test the global function but verify against cached data
            start_time = time.time()
            network_db = await gather_network_database(
                self.TEST_SCHOLAR_ID, self.TEST_AUTHOR_NAME, max_depth=1, max_size=5
            )
            end_time = time.time()
            elapsed = end_time - start_time

            logger.info(f"✅ Global network database built in {elapsed:.3f}s")

            assert isinstance(network_db, GoogleScholarNetworkDB)
            assert len(network_db.network) > 0
            assert (
                elapsed < 15.0
            ), f"Global network database function performance test failed: {elapsed:.3f}s exceeds 15s limit"

            logger.info("🎯 Global network database function test PASSED")
        else:
            pytest.skip("Skipping - network data not available from previous test")


if __name__ == "__main__":
    # Run tests directly
    import asyncio

    async def run_tests():
        test = TestScholarService()
        await test.test_scholar_info_retrieval()
        await test.test_global_function_performance()
        await test.test_network_database_building()
        await test.test_database_operations()
        await test.test_global_network_database_function()
        logger.info("✅ All consolidated tests completed successfully")

    asyncio.run(run_tests())
