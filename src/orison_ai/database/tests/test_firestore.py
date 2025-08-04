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

from database.schema import (
    GoogleScholarDB,
    GoogleScholarNetworkDB,
    StoryBuilder,
    ScreeningBuilder,
    EvidenceBuilder,
    ChatMemoryDB,
    Author,
    Publication,
    ScholarSummary,
    QandA,
    MemoryEntry,
)
from database.firestore_clients import (
    GoogleScholarClient,
    GoogleScholarNetworkClient,
    StoryClient,
    ScreeningClient,
    EvidenceClient,
    ChatMemoryClient,
)

logger = logging.getLogger(__name__)


class TestFirestoreSchemas:
    """Test all Firestore data schemas for integrity"""

    # Test constants
    TEST_ATTORNEY_ID = "test_attorney_firestore"
    TEST_APPLICANT_ID = "test_applicant_firestore"

    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create event loop for async tests"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    def create_dummy_author(self) -> Author:
        """Create dummy Author data"""
        return Author(
            profile_link="https://scholar.google.com/citations?user=test123",
            name="Dr. Test Author",
            cited_by=1500,
            h_index=25,
        )

    def create_dummy_publication(self) -> Publication:
        """Create dummy Publication data"""
        return Publication(
            title="Test Publication: Advanced AI Methods",
            year="2023",
            authors="Dr. Test Author, Dr. Test Collaborator",
            abstract="This is a test publication abstract about advanced AI methods.",
            cited_by=150,
            forum_name="Journal of Test Research",
            type_of_paper="Journal",
            peer_reviews="Peer Review 1, Peer Review 2",
        )

    def create_dummy_scholar_summary(self) -> ScholarSummary:
        """Create dummy ScholarSummary data"""
        return ScholarSummary(
            name="Dr. Test Collaborator",
            scholar_id="test_scholar_456",
            citations=800,
            h_index=18,
            publication_count=45,
        )

    def create_dummy_qanda(self) -> QandA:
        """Create dummy QandA data"""
        return QandA(
            question="What is the applicant's experience in AI?",
            answer="The applicant has 5 years of experience in machine learning and AI research.",
            source="Resume.pdf, Page 2",
        )

    def create_dummy_memory_entry(self) -> MemoryEntry:
        """Create dummy MemoryEntry data"""
        return MemoryEntry(
            user_message="Tell me about the applicant's qualifications.",
            assistant_response="The applicant has a strong background in computer science with expertise in AI.",
            timestamp=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    async def test_google_scholar_db_schema(self):
        """Test GoogleScholarDB schema integrity"""
        try:
            client = GoogleScholarClient()

            # Clean up any existing test documents first
            existing_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=10,
            )
            for doc, doc_id in existing_docs:
                await client.delete(
                    self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, doc_id
                )
                logger.info(f"Cleaned up existing document: {doc_id}")

            # Small delay to ensure cleanup is complete
            import asyncio

            await asyncio.sleep(0.1)

            # Create dummy data
            test_scholar = GoogleScholarDB(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                author=self.create_dummy_author(),
                co_authors=[self.create_dummy_author()],
                keywords=["AI", "Machine Learning", "Deep Learning"],
                cited_by=2000,
                h_index=30,
                cited_by_5y=1800,
                h_index_5y=28,
                cited_each_year={"2023": 500, "2022": 450, "2021": 400},
                publications=[self.create_dummy_publication()],
                homepage="https://example.com/researcher",
                other_details={
                    "affiliation": "Test University",
                    "department": "Computer Science",
                },
            )

            # Insert data
            doc_id = await client.insert(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc=test_scholar,
            )

            assert doc_id is not None, "Failed to insert GoogleScholarDB"
            logger.info(f"Document inserted with ID: {doc_id} (type: {type(doc_id)})")

            # Retrieve data
            retrieved_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            assert len(retrieved_docs) > 0, "Failed to retrieve GoogleScholarDB"

            retrieved_scholar, retrieved_id = retrieved_docs[0]
            logger.info(
                f"Document retrieved with ID: {retrieved_id} (type: {type(retrieved_id)})"
            )

            # Verify data integrity
            assert retrieved_scholar.attorney_id == test_scholar.attorney_id
            assert retrieved_scholar.applicant_id == test_scholar.applicant_id
            assert retrieved_scholar.author.name == test_scholar.author.name
            assert retrieved_scholar.cited_by == test_scholar.cited_by
            assert retrieved_scholar.h_index == test_scholar.h_index
            assert len(retrieved_scholar.publications) == len(test_scholar.publications)
            assert retrieved_scholar.keywords == test_scholar.keywords

            logger.info(
                f"GoogleScholarDB schema test passed - "
                f"Inserted ID: {doc_id}, Retrieved ID: {retrieved_id}, "
                f"Author: {retrieved_scholar.author.name}, Citations: {retrieved_scholar.cited_by}"
            )

            # Test delete operation using retrieved document ID
            logger.info(
                f"Attempting to delete document - Insert ID: {doc_id}, Retrieved ID: {retrieved_id}"
            )
            delete_success = await client.delete(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc_id=retrieved_id,  # Use retrieved ID instead of insert ID
            )

            assert (
                delete_success
            ), f"Failed to delete GoogleScholarDB with ID {retrieved_id}"

            # Add small delay to allow for consistency
            import asyncio

            await asyncio.sleep(0.1)

            # Verify deletion by trying to retrieve again
            deleted_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            if len(deleted_docs) > 0:
                remaining_doc, remaining_id = deleted_docs[0]
                logger.error(
                    f"Document still exists after deletion - ID: {remaining_id}, Deleted ID: {retrieved_id}"
                )
                assert (
                    False
                ), f"Document was not properly deleted. Found document with ID: {remaining_id}, tried to delete: {retrieved_id}"

            logger.info(
                f"GoogleScholarDB deletion test passed - Document {retrieved_id} successfully deleted"
            )

        except Exception as e:
            pytest.fail(f"GoogleScholarDB schema test failed: {e}")

    @pytest.mark.asyncio
    async def test_story_builder_schema(self):
        """Test StoryBuilder schema integrity"""
        try:
            client = StoryClient()

            # Clean up any existing test documents first
            existing_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=10,
            )
            for doc, doc_id in existing_docs:
                await client.delete(
                    self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, doc_id
                )
                logger.info(f"Cleaned up existing document: {doc_id}")

            # Small delay to ensure cleanup is complete
            import asyncio

            await asyncio.sleep(0.1)

            # Create dummy data
            test_story = StoryBuilder(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                summary=[
                    self.create_dummy_qanda(),
                    QandA(
                        question="What are the applicant's key achievements?",
                        answer="Published 10 papers in top-tier conferences and received 3 awards.",
                        source="CV.pdf, Page 1",
                    ),
                ],
            )

            # Insert data
            doc_id = await client.insert(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc=test_story,
            )

            assert doc_id is not None, "Failed to insert StoryBuilder"
            logger.info(
                f"StoryBuilder inserted with ID: {doc_id} (type: {type(doc_id)})"
            )

            # Retrieve data
            retrieved_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            assert len(retrieved_docs) > 0, "Failed to retrieve StoryBuilder"

            retrieved_story, retrieved_id = retrieved_docs[0]
            logger.info(
                f"StoryBuilder retrieved with ID: {retrieved_id} (type: {type(retrieved_id)})"
            )

            # Verify data integrity
            assert retrieved_story.attorney_id == test_story.attorney_id
            assert retrieved_story.applicant_id == test_story.applicant_id
            assert len(retrieved_story.summary) == len(test_story.summary)
            assert retrieved_story.summary[0].question == test_story.summary[0].question
            assert retrieved_story.summary[0].answer == test_story.summary[0].answer

            logger.info(
                f"StoryBuilder schema test passed - "
                f"Summary items: {len(retrieved_story.summary)}, "
                f"First question: '{retrieved_story.summary[0].question}'"
            )

            # Test delete operation using retrieved document ID
            logger.info(
                f"Attempting to delete StoryBuilder - Insert ID: {doc_id}, Retrieved ID: {retrieved_id}"
            )
            delete_success = await client.delete(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc_id=retrieved_id,  # Use retrieved ID instead of insert ID
            )

            assert (
                delete_success
            ), f"Failed to delete StoryBuilder with ID {retrieved_id}"

            # Add small delay to allow for consistency
            await asyncio.sleep(0.1)

            # Verify deletion by trying to retrieve again
            deleted_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            if len(deleted_docs) > 0:
                remaining_doc, remaining_id = deleted_docs[0]
                logger.error(
                    f"StoryBuilder still exists after deletion - ID: {remaining_id}, Deleted ID: {retrieved_id}"
                )
                assert (
                    False
                ), f"StoryBuilder was not properly deleted. Found document with ID: {remaining_id}, tried to delete: {retrieved_id}"

            logger.info(
                f"StoryBuilder deletion test passed - Document {retrieved_id} successfully deleted"
            )

        except Exception as e:
            pytest.fail(f"StoryBuilder schema test failed: {e}")

    @pytest.mark.asyncio
    async def test_screening_builder_schema(self):
        """Test ScreeningBuilder schema integrity"""
        try:
            client = ScreeningClient()

            # Clean up any existing test documents first
            existing_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=10,
            )
            for doc, doc_id in existing_docs:
                await client.delete(
                    self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, doc_id
                )
                logger.info(f"Cleaned up existing ScreeningBuilder document: {doc_id}")

            # Small delay to ensure cleanup is complete
            import asyncio

            await asyncio.sleep(0.1)

            # Create dummy data
            test_screening = ScreeningBuilder(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                summary=[
                    QandA(
                        question="Does the applicant meet the education requirements?",
                        answer="Yes, the applicant has a PhD in Computer Science from a top university.",
                        source="Transcript.pdf",
                    ),
                    QandA(
                        question="What is the applicant's work experience?",
                        answer="5 years at Google as a Senior Software Engineer.",
                        source="Resume.pdf, Page 1",
                    ),
                ],
            )

            # Insert data
            doc_id = await client.insert(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc=test_screening,
            )

            assert doc_id is not None, "Failed to insert ScreeningBuilder"
            logger.info(
                f"ScreeningBuilder inserted with ID: {doc_id} (type: {type(doc_id)})"
            )

            # Retrieve data
            retrieved_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            assert len(retrieved_docs) > 0, "Failed to retrieve ScreeningBuilder"

            retrieved_screening, retrieved_id = retrieved_docs[0]
            logger.info(
                f"ScreeningBuilder retrieved with ID: {retrieved_id} (type: {type(retrieved_id)})"
            )

            # Verify data integrity
            assert retrieved_screening.attorney_id == test_screening.attorney_id
            assert retrieved_screening.applicant_id == test_screening.applicant_id
            assert len(retrieved_screening.summary) == len(test_screening.summary)
            assert (
                retrieved_screening.summary[0].question
                == test_screening.summary[0].question
            )

            logger.info(
                f"ScreeningBuilder schema test passed - Summary items: {len(retrieved_screening.summary)}"
            )

            # Test delete operation using retrieved document ID
            logger.info(
                f"Attempting to delete ScreeningBuilder - Insert ID: {doc_id}, Retrieved ID: {retrieved_id}"
            )
            delete_success = await client.delete(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc_id=retrieved_id,
            )

            assert (
                delete_success
            ), f"Failed to delete ScreeningBuilder with ID {retrieved_id}"

            # Add small delay to allow for consistency
            await asyncio.sleep(0.1)

            # Verify deletion by trying to retrieve again
            deleted_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            if len(deleted_docs) > 0:
                remaining_doc, remaining_id = deleted_docs[0]
                logger.error(
                    f"ScreeningBuilder still exists after deletion - ID: {remaining_id}, Deleted ID: {retrieved_id}"
                )
                assert (
                    False
                ), f"ScreeningBuilder was not properly deleted. Found document with ID: {remaining_id}, tried to delete: {retrieved_id}"

            logger.info(
                f"ScreeningBuilder deletion test passed - Document {doc_id} successfully deleted"
            )

        except Exception as e:
            pytest.fail(f"ScreeningBuilder schema test failed: {e}")

    @pytest.mark.asyncio
    async def test_evidence_builder_schema(self):
        """Test EvidenceBuilder schema integrity"""
        try:
            client = EvidenceClient()

            # Clean up any existing test documents first
            existing_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=10,
            )
            for doc, doc_id in existing_docs:
                await client.delete(
                    self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, doc_id
                )
                logger.info(f"Cleaned up existing EvidenceBuilder document: {doc_id}")

            # Small delay to ensure cleanup is complete
            import asyncio

            await asyncio.sleep(0.1)

            # Create dummy data
            test_evidence = EvidenceBuilder(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                summary="The applicant demonstrates exceptional ability in AI research with 50+ publications, 2000+ citations, and recognition from leading institutions.",
            )

            # Insert data
            doc_id = await client.insert(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc=test_evidence,
            )

            assert doc_id is not None, "Failed to insert EvidenceBuilder"
            logger.info(
                f"EvidenceBuilder inserted with ID: {doc_id} (type: {type(doc_id)})"
            )

            # Retrieve data
            retrieved_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            assert len(retrieved_docs) > 0, "Failed to retrieve EvidenceBuilder"

            retrieved_evidence, retrieved_id = retrieved_docs[0]
            logger.info(
                f"EvidenceBuilder retrieved with ID: {retrieved_id} (type: {type(retrieved_id)})"
            )

            # Verify data integrity
            assert retrieved_evidence.attorney_id == test_evidence.attorney_id
            assert retrieved_evidence.applicant_id == test_evidence.applicant_id
            assert retrieved_evidence.summary == test_evidence.summary

            logger.info(
                f"EvidenceBuilder schema test passed - Summary length: {len(retrieved_evidence.summary)} chars"
            )

            # Test delete operation using retrieved document ID
            logger.info(
                f"Attempting to delete EvidenceBuilder - Insert ID: {doc_id}, Retrieved ID: {retrieved_id}"
            )
            delete_success = await client.delete(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc_id=retrieved_id,
            )

            assert (
                delete_success
            ), f"Failed to delete EvidenceBuilder with ID {retrieved_id}"

            # Add small delay to allow for consistency
            await asyncio.sleep(0.1)

            # Verify deletion by trying to retrieve again
            deleted_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            if len(deleted_docs) > 0:
                remaining_doc, remaining_id = deleted_docs[0]
                logger.error(
                    f"EvidenceBuilder still exists after deletion - ID: {remaining_id}, Deleted ID: {retrieved_id}"
                )
                assert (
                    False
                ), f"EvidenceBuilder was not properly deleted. Found document with ID: {remaining_id}, tried to delete: {retrieved_id}"

            logger.info(
                f"EvidenceBuilder deletion test passed - Document {doc_id} successfully deleted"
            )

        except Exception as e:
            pytest.fail(f"EvidenceBuilder schema test failed: {e}")

    @pytest.mark.asyncio
    async def test_chat_memory_db_schema(self):
        """Test ChatMemoryDB schema integrity"""
        try:
            client = ChatMemoryClient()

            # Clean up any existing test documents first
            existing_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=10,
            )
            for doc, doc_id in existing_docs:
                await client.delete(
                    self.TEST_ATTORNEY_ID, self.TEST_APPLICANT_ID, doc_id
                )
                logger.info(f"Cleaned up existing ChatMemoryDB document: {doc_id}")

            # Small delay to ensure cleanup is complete
            import asyncio

            await asyncio.sleep(0.1)

            # Create dummy data
            test_memory = ChatMemoryDB(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                history=[
                    self.create_dummy_memory_entry(),
                    MemoryEntry(
                        user_message="What programming languages does the applicant know?",
                        assistant_response="The applicant is proficient in Python, Java, C++, and JavaScript.",
                        timestamp=datetime.now(timezone.utc),
                    ),
                ],
            )

            # Insert data
            doc_id = await client.insert(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc=test_memory,
            )

            assert doc_id is not None, "Failed to insert ChatMemoryDB"
            logger.info(
                f"ChatMemoryDB inserted with ID: {doc_id} (type: {type(doc_id)})"
            )

            # Retrieve data
            retrieved_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            assert len(retrieved_docs) > 0, "Failed to retrieve ChatMemoryDB"

            retrieved_memory, retrieved_id = retrieved_docs[0]
            logger.info(
                f"ChatMemoryDB retrieved with ID: {retrieved_id} (type: {type(retrieved_id)})"
            )

            # Verify data integrity
            assert retrieved_memory.attorney_id == test_memory.attorney_id
            assert retrieved_memory.applicant_id == test_memory.applicant_id
            assert len(retrieved_memory.history) == len(test_memory.history)
            assert (
                retrieved_memory.history[0].user_message
                == test_memory.history[0].user_message
            )
            assert (
                retrieved_memory.history[0].assistant_response
                == test_memory.history[0].assistant_response
            )

            logger.info(
                f"ChatMemoryDB schema test passed - History entries: {len(retrieved_memory.history)}"
            )

            # Test delete operation using retrieved document ID
            logger.info(
                f"Attempting to delete ChatMemoryDB - Insert ID: {doc_id}, Retrieved ID: {retrieved_id}"
            )
            delete_success = await client.delete(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                doc_id=retrieved_id,
            )

            assert (
                delete_success
            ), f"Failed to delete ChatMemoryDB with ID {retrieved_id}"

            # Add small delay to allow for consistency
            await asyncio.sleep(0.1)

            # Verify deletion by trying to retrieve again
            deleted_docs = await client.find_top_k(
                attorney_id=self.TEST_ATTORNEY_ID,
                applicant_id=self.TEST_APPLICANT_ID,
                k=1,
            )

            if len(deleted_docs) > 0:
                remaining_doc, remaining_id = deleted_docs[0]
                logger.error(
                    f"ChatMemoryDB still exists after deletion - ID: {remaining_id}, Deleted ID: {retrieved_id}"
                )
                assert (
                    False
                ), f"ChatMemoryDB was not properly deleted. Found document with ID: {remaining_id}, tried to delete: {retrieved_id}"

            logger.info(
                f"ChatMemoryDB deletion test passed - Document {doc_id} successfully deleted"
            )

        except Exception as e:
            pytest.fail(f"ChatMemoryDB schema test failed: {e}")
