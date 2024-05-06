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
from typing import List, Union
from orison_ai.src.database.models import GoogleScholarDB
from orison_ai.src.database.mongo import DBInitializer
from orison_ai.src.utils.constants import DB_NAME
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class GoogleScholarClient(DBInitializer):
    MODEL_NAME = "google_scholar"

    def __init__(
        self,
        user_id: str,
        db_name: str = DB_NAME,
        db_path: str = "mongodb://mongodb:27017/",
    ):
        """
        Initializes an instance of a DatabaseModifier object, which can be used
        to insert into or update a database collection given a file

        :param db_name: the name of the database to insert into
        :param db_path: the path to the database
        """
        super(GoogleScholarClient, self).__init__(db_name, db_path)
        self._collection = self._db[user_id]

    async def find_one(self, user_id: str) -> Union[GoogleScholarDB, None]:
        """
        Finds a GoogleScholarDB item and convert it to GoogleScholarDB object
        given a GoogleScholarDB id

        :param user_id: the unique id to fetch in GoogleScholarDB collection

        :return: the entry found in mongo, converted to a GoogleScholarDB object
        """
        google_scholar_item = await self._collection.find_one({"user_id": user_id})

        if not google_scholar_item:
            _logger.info(f"No GoogleScholarDB with id: {id} was found")
            return None

        return GoogleScholarDB(**google_scholar_item)

    async def find_many(self, ids: List[str]) -> Union[List[GoogleScholarDB], None]:
        """
        Finds many GoogleScholarDB items and convert them to GoogleScholarDB objects
        given GoogleScholarDB ids

        :param ids: ids to fetch in GoogleScholarDB collection

        :return: entries found in mongo, converted to list of GoogleScholarDB objects
        """
        _logger.debug(f"Database operation: find many GoogleScholarDB by ids: {ids}")

        if not isinstance(ids, list):
            raise ValueError(
                'Expected type list of str for parameter "ids". Instead, '
                f"got {type(ids)}"
            )

        if not all(isinstance(id, str) for id in ids):
            raise ValueError('Not all elements in parameter "ids" is of type str')

        return [
            GoogleScholarDB(**item)
            async for item in self._collection.find({"id": {"$in": ids}})
        ]

    async def insert(self, profile: GoogleScholarDB) -> ObjectId:
        """
        Inserts a GoogleScholarDB object into the mongo database

        :param profile: the GoogleScholarDB object to insert into the database

        :return: the inserted GoogleScholarDB's mongo id (not the uniquely generated
            GoogleScholarDB._id)
        """
        _logger.debug(f"Database operation: inserting GoogleScholarDB: {profile}")

        if not isinstance(profile, GoogleScholarDB):
            raise TypeError(
                f"The google scholar profile provided {profile} of type {type(profile)} "
                f"needs to be type {type(GoogleScholarDB)}"
            )

        result = await self._collection.insert_one(profile.to_mongo().to_dict())
        _logger.info(f"GoogleScholarDB inserted. Mongo _id: {result.inserted_id}")

        return result.inserted_id
