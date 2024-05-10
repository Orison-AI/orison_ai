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
from orison_ai.src.database.models import Story
from orison_ai.src.database.client import DBClient
from orison_ai.src.utils.constants import DB_NAME

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class StoryClient(DBClient):
    def __init__(
        self,
        db_name: str = DB_NAME,
        db_path: str = "mongodb://mongodb:27017/",
    ):
        """
        Initializes an instance of a DatabaseModifier object, which can be used
        to insert into or update a database collection given a file

        :param db_name: the name of the database to insert into
        :param db_path: the path to the database
        """
        super(StoryClient, self).__init__(db_name, db_path)
        self._model = Story
        self._collection = self._db[self._model.__name__]
