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

import logging
from datetime import datetime, timezone
from langchain.memory import ConversationBufferWindowMemory
from database.schema import (
    GoogleScholarDB,
    GoogleScholarNetworkDB,
    StoryBuilder,
    ScreeningBuilder,
    MemoryEntry,
    ChatMemoryDB,
    EvidenceBuilder,
)
from database.firebase_config import FirestoreClient


class StoryClient(FirestoreClient):
    """Story builder client - preserved from original"""

    def __init__(self):
        super().__init__()
        self._model = StoryBuilder
        self._collection = self.client.collection("story_builder")


class ScreeningClient(FirestoreClient):
    """Screening builder client - preserved from original"""

    def __init__(self):
        super().__init__()
        self._model = ScreeningBuilder
        self._collection = self.client.collection("screening_builder")


class GoogleScholarClient(FirestoreClient):
    """Google Scholar client - preserved from original"""

    def __init__(self):
        super().__init__()
        self._model = GoogleScholarDB
        self._collection = self.client.collection("google_scholar")


class EvidenceClient(FirestoreClient):
    """Evidence builder client - preserved from original"""

    def __init__(self):
        super().__init__()
        self._model = EvidenceBuilder
        self._collection = self.client.collection("evidence_letter")


class GoogleScholarNetworkClient(FirestoreClient):
    """Google Scholar network client - preserved from original"""

    def __init__(self):
        super().__init__()
        self._model = GoogleScholarNetworkDB
        self._collection = self.client.collection("google_scholar_network")


class ChatMemoryClient(FirestoreClient):
    """Chat memory client - preserved from original"""

    def __init__(self):
        super().__init__()
        self._model = ChatMemoryDB
        self._collection = self.client.collection("chat_memory")
        self.logger = logging.getLogger(__name__)

    async def store_conversation(
        self,
        attorney_id: str,
        applicant_id: str,
        user_message: str,
        assistant_response: str,
    ):
        """Store conversation in memory - preserved from original"""
        try:
            self.logger.info(f"Storing conversation for {attorney_id}/{applicant_id}")

            # Try to find existing memory document
            memory_docs = await self.find_top_k(
                attorney_id=attorney_id, applicant_id=applicant_id, k=1
            )

            new_entry = MemoryEntry(
                user_message=user_message,
                assistant_response=assistant_response,
                timestamp=datetime.now(timezone.utc),
            )

            if memory_docs:
                # Update existing memory
                memory_doc, doc_id = memory_docs[0]
                memory_doc.history.append(new_entry)
                memory_doc.date_updated = datetime.now(timezone.utc)

                # Keep only last 10 conversations
                if len(memory_doc.history) > 10:
                    memory_doc.history = memory_doc.history[-10:]

                await self.replace(attorney_id, applicant_id, doc_id, memory_doc)
                self.logger.info(
                    f"Updated existing conversation memory for {attorney_id}/{applicant_id}"
                )
            else:
                # Create new memory document
                memory_doc = ChatMemoryDB(
                    attorney_id=attorney_id,
                    applicant_id=applicant_id,
                    history=[new_entry],
                )
                await self.insert(attorney_id, applicant_id, memory_doc)
                self.logger.info(
                    f"Created new conversation memory for {attorney_id}/{applicant_id}"
                )

        except Exception as e:
            # Log error but don't fail the main operation
            self.logger.error(
                f"Error storing conversation memory for {attorney_id}/{applicant_id}: {e}"
            )

    def get_langchain_memory(
        self, attorney_id: str, applicant_id: str
    ) -> ConversationBufferWindowMemory:
        """Get LangChain memory object - preserved from original"""
        try:
            # Retrieve existing memory
            memory_docs = self.find_top_k(
                attorney_id=attorney_id, applicant_id=applicant_id, k=1
            )

            memory = ConversationBufferWindowMemory(k=5, return_messages=True)

            if memory_docs:
                memory_doc, _ = memory_docs[0]
                # Load last 5 conversations
                for entry in memory_doc.history[-5:]:
                    memory.chat_memory.add_user_message(entry.user_message)
                    memory.chat_memory.add_ai_message(entry.assistant_response)

            return memory

        except Exception as e:
            # Return empty memory on error
            self.logger.error(
                f"Error loading conversation memory for {attorney_id}/{applicant_id}: {e}"
            )
            return ConversationBufferWindowMemory(k=5, return_messages=True)
