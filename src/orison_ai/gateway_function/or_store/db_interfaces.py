#! /usr/bin/env python3.10

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

# External

from typing import List
from datetime import datetime
from mongoengine import DoesNotExist
from langchain.memory import ConversationBufferWindowMemory

# Internal

from or_store.models import (
    GoogleScholarDB,
    GoogleScholarNetworkDB,
    StoryBuilder,
    ScreeningBuilder,
    MemoryEntry,
    ChatMemoryDB,
)
from or_store.firebase import FirestoreClient


class StoryClient(FirestoreClient):
    def __init__(self):
        """
        Initializes an instance of a StoryClient object, which can be used
        to insert into or update a database collection given a file
        """
        super(StoryClient, self).__init__()
        self._model = StoryBuilder
        self._collection = self.client.collection("story_builder")


class ScreeningClient(FirestoreClient):
    def __init__(self):
        """
        Initializes an instance of a StoryClient object, which can be used
        to insert into or update a database collection given a file
        """
        super(ScreeningClient, self).__init__()
        self._model = ScreeningBuilder
        self._collection = self.client.collection("screening_builder")


class GoogleScholarClient(FirestoreClient):
    def __init__(self):
        """
        Initializes an instance of a GoogleScholarClient object, which can be used
        to insert into or update a database collection given a file
        """
        super(GoogleScholarClient, self).__init__()
        self._model = GoogleScholarDB
        self._collection = self.client.collection("google_scholar")


class GoogleScholarNetworkClient(FirestoreClient):
    def __init__(self):
        """
        Initializes an instance of a GoogleScholarNetworkClient object, which can be used
        to insert into or update a database collection given a file
        """
        super(GoogleScholarNetworkClient, self).__init__()
        self._model = GoogleScholarNetworkDB
        self._collection = self.client.collection("google_scholar_network")


class ChatMemoryClient(FirestoreClient):
    def __init__(self):
        """
        Initializes an instance of a ChatMemoryClient object, which interacts with the chat memory collection.
        """
        super(ChatMemoryClient, self).__init__()
        self._model = ChatMemoryDB
        self._collection = self.client.collection("chat_memory")

    async def get_memory(
        self, applicant_id: str, attorney_id: str
    ) -> List[MemoryEntry]:
        """
        Retrieves the chat memory for a given applicant and attorney.
        """
        try:
            memory_record, _ = await self.find_top(
                applicant_id=applicant_id, attorney_id=attorney_id
            )
            return memory_record
        except DoesNotExist:
            return []

    async def update_memory(
        self,
        applicant_id: str,
        attorney_id: str,
        user_message: str,
        assistant_response: str,
    ):
        """
        Updates the chat memory for a given applicant and attorney with a new user message and assistant response.
        """
        memory_entry = MemoryEntry(
            user_message=user_message,
            assistant_response=assistant_response,
        )
        try:
            memory_record, doc_id = await self.find_top(
                applicant_id=applicant_id, attorney_id=attorney_id
            )
            memory_record.history.append(memory_entry)
            memory_record.date_updated = datetime.utcnow()
            await self.replace(
                applicant_id=applicant_id,
                attorney_id=attorney_id,
                doc_id=doc_id,
                doc=memory_record,
            )
        except DoesNotExist:
            memory_record = ChatMemoryDB(
                applicant_id=applicant_id,
                attorney_id=attorney_id,
                history=[memory_entry],
                date_updated=datetime.utcnow(),
            )
            await self.insert(
                applicant_id=applicant_id, attorney_id=attorney_id, doc=memory_record
            )
        except Exception as e:
            raise e

    async def clear_memory(self, applicant_id: str, attorney_id: str):
        """
        Clears the chat memory for a given applicant and attorney.
        """
        try:
            memory_record, _ = self.find_top(
                applicant_id=applicant_id, attorney_id=attorney_id
            )
            memory_record.update(history=[], date_updated=datetime.utcnow())
        except DoesNotExist:
            pass

    async def load_memory_into_buffer(
        self,
        memory_buffer: ConversationBufferWindowMemory,
        applicant_id: str,
        attorney_id: str,
    ):
        """
        Loads existing memory from DB into an empty ConversationBufferWindowMemory.
        """
        memory_record = await self.get_memory(applicant_id, attorney_id)
        for entry in memory_record.history:
            await memory_buffer.asave_context(
                {"question": entry.user_message},  # User's message
                {"answer": entry.assistant_response},  # Assistant's response
            )
