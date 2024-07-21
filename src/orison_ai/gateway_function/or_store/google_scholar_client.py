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

import logging
from or_store.models import (
    GoogleScholarDB,
    GoogleScholarNetworkDB,
)
from or_store.firebase import FirestoreClient

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


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