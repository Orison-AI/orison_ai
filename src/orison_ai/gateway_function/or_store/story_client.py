#! /usr/bin/env python3.9

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

import logging
from or_store.models import StoryBuilder, ScreeningBuilder
from or_store.firebase import FirestoreClient

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class StoryClient(FirestoreClient):
    def __init__(self):
        """
        Initializes an instance of a StoryClient object, which can be used
        to insert into or update a database collection given a file
        """
        super(StoryClient, self).__init__()
        self._model = StoryBuilder
        self._async_collection = self.async_client.collection("story_builder")
        self._collection = self.client.collection("story_builder")


class ScreeningClient(FirestoreClient):
    def __init__(self):
        """
        Initializes an instance of a StoryClient object, which can be used
        to insert into or update a database collection given a file
        """
        super(ScreeningClient, self).__init__()
        self._model = ScreeningBuilder
        self._async_collection = self.async_client.collection("screening_builder")
        self._collection = self.client.collection("screening_builder")
