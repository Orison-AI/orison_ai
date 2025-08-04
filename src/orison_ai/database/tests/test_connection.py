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
from datetime import datetime, timezone

# Internal

from database.firebase_config import FireStoreDB
from database.secrets import OrisonSecrets
from database.firebase_storage import FirebaseStorage
from core.environment import get_env

logger = logging.getLogger(__name__)


class TestConnection:
    """Test connectivity to Firebase services"""

    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create event loop for async tests"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    def test_environment_loading(self):
        """Test that environment variables are loaded correctly"""
        try:
            env = get_env()

            # Verify required environment variables are present
            assert env.openai_api_key is not None, "OPENAI_API_KEY not set"
            assert env.qdrant_url is not None, "QDRANT_URL not set"
            assert env.qdrant_api_key is not None, "QDRANT_API_KEY not set"

            logger.info(
                f"Environment variables loaded successfully - "
                f"OpenAI: {'***' + env.openai_api_key[-4:] if len(env.openai_api_key) > 4 else 'SET'}, "
                f"Qdrant: {env.qdrant_url}, "
                f"Firebase: {'SET' if env.firebase_credentials_json else 'NOT SET'}"
            )

        except Exception as e:
            pytest.fail(f"Environment loading failed: {e}")

    def test_secrets_creation(self):
        """Test creating OrisonSecrets from attorney/applicant IDs"""
        try:
            test_attorney_id = "test_attorney_123"
            test_applicant_id = "test_applicant_456"

            secrets = OrisonSecrets.from_attorney_applicant(
                test_attorney_id, test_applicant_id
            )

            assert secrets.openai_api_key is not None
            assert secrets.qdrant_url is not None
            assert secrets.qdrant_api_key is not None
            assert (
                secrets.collection_name
                == f"{test_attorney_id}_{test_applicant_id}_collection"
            )

            logger.info(
                f"OrisonSecrets created successfully - Collection: {secrets.collection_name}"
            )

        except Exception as e:
            pytest.fail(f"Secrets creation failed: {e}")

    def test_firestore_connection(self):
        """Test basic Firestore database connection"""
        try:
            # Initialize Firestore client
            firestore_db = FireStoreDB()

            # Verify client is initialized
            assert firestore_db.client is not None, "Firestore client not initialized"
            assert firestore_db.app is not None, "Firebase app not initialized"

            logger.info(
                f"Firestore connection established successfully - Client: {type(firestore_db.client).__name__}"
            )

        except Exception as e:
            pytest.fail(f"Firestore connection failed: {e}")

    @pytest.mark.asyncio
    async def test_firestore_basic_operation(self):
        """Test basic Firestore read/write operation"""
        try:
            firestore_db = FireStoreDB()

            # Test collection access
            test_collection = "connection_test"
            test_document = "test_doc"
            test_field = "test_field"
            test_value = f"test_value_{datetime.now(timezone.utc).isoformat()}"

            # Try to update a test document
            await firestore_db.update_collection_document(
                collection_name=test_collection,
                document_name=test_document,
                field=test_field,
                value=test_value,
            )

            logger.info(
                f"Firestore basic operation successful - Updated: {test_collection}/{test_document}.{test_field} = {test_value}"
            )

        except Exception as e:
            pytest.fail(f"Firestore basic operation failed: {e}")

    def test_firebase_storage_initialization(self):
        """Test Firebase Storage initialization"""
        try:
            # Initialize Firebase Storage
            storage = FirebaseStorage()

            # Verify storage bucket is accessible
            bucket = storage._bucket()
            assert bucket is not None, "Firebase Storage bucket not accessible"

            logger.info(
                f"Firebase Storage initialized successfully - Bucket: {bucket.name}"
            )

        except Exception as e:
            pytest.fail(f"Firebase Storage initialization failed: {e}")

    @pytest.mark.asyncio
    async def test_full_connectivity_flow(self):
        """Test complete connectivity flow - Environment → Secrets → Firestore → Storage"""
        try:
            # Step 1: Load environment
            env = get_env()
            assert env.openai_api_key is not None

            # Step 2: Create secrets
            secrets = OrisonSecrets.from_attorney_applicant(
                "test_attorney", "test_applicant"
            )
            assert secrets.collection_name is not None

            # Step 3: Initialize Firestore
            firestore_db = FireStoreDB()
            assert firestore_db.client is not None

            # Step 4: Initialize Firebase Storage
            storage = FirebaseStorage()
            bucket = storage._bucket()
            assert bucket is not None

            # Step 5: Test a simple Firestore operation
            test_timestamp = datetime.now(timezone.utc).isoformat()
            await firestore_db.update_collection_document(
                collection_name="connectivity_test",
                document_name="full_flow_test",
                field="last_tested",
                value=test_timestamp,
            )

            logger.info(
                f"Full connectivity flow successful - Environment: ✓, Secrets: ✓, Firestore: ✓, Storage: ✓ "
                f"(Test timestamp: {test_timestamp})"
            )

        except Exception as e:
            pytest.fail(f"Full connectivity flow failed: {e}")
