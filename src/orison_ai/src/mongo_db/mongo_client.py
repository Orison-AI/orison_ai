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
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import logging
from typing import Optional
from mongoengine import Document, EmbeddedDocument
from typing import List, Union
from pymongo import DESCENDING, ASCENDING

# Internal
from orison_ai.src.utils.constants import DB_NAME
from orison_store.database import models

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class InsertionError(Exception):
    pass


class DBInitializer:
    def __init__(
        self, db_name: str = DB_NAME, db_path: str = "mongodb://mongodb:27017/"
    ):
        """
        Initializes an instance of a MongoDB object, which can be used to
        connect to a MongoDB database
        DB_NAME is the law firm database name
        Collection names are specific to applicant profiles

        :param db_name: the name of the database to connect to
        :param db_path: the path to the database
        """
        self.client = AsyncIOMotorClient(db_path)
        self._db = self.client[db_name]
        self._collection = None


class DBClient(DBInitializer):
    def __init__(
        self,
        db_name: str = DB_NAME,
        db_path: str = "mongodb://mongodb:27017/",
    ):
        # ToDo: Do we want to maintain unique collections
        """
        Initializes an instance of a DatabaseModifier object, which can be used
        to insert into or update a database collection given a file

        :param db_name: the name of the database to insert into
        :param db_path: the path to the database
        """
        super(DBClient, self).__init__(db_name, db_path)

    async def find_top(
        self,
        attorney_id: str,
        applicant_id: str,
        filters: Optional[dict] = {},
        order: [1, -1] = DESCENDING,
    ) -> Union[EmbeddedDocument, Document, None]:
        """
        Finds a mongoengine Document item from the collection and converts it to a mongo object
        Order is either ASCENDING or DESCENDING

        :param attorney_id: the business id of the document to find
        :param applicant_id: the user id of the document to find
        :param order: the order in which to sort the documents
        :return: the entry found in mongo db for the requesting model class instance
                converted to a mongo object
        """
        return await self.find_top_k(attorney_id, applicant_id, filters, 1, order)

    async def find_top_k(
        self,
        attorney_id: str,
        applicant_id: str,
        filters: Optional[dict] = {},
        k: int = 1,
        order: [ASCENDING, DESCENDING, 1, -1] = DESCENDING,
    ) -> Union[List[EmbeddedDocument], List[Document], None]:
        """
        Finds many document items given a limit k from the collection and converts them to mongo objects
        Order is either ASCENDING or DESCENDING

        :param attorney_id: the business id of the document to find
        :param applicant_id: the user id of the document to find
        :param k: the number of documents to find
        :param order: the order in which to sort the documents
        :return: entries found in mongo converted to list of mongo objects
        """
        _logger.debug(f"Database operation: find {k} documents by order: {order}")

        if self._collection is None:
            raise ValueError("Collection not set")
        if self._model is None:
            raise ValueError("DB Model not set")

        if order not in [ASCENDING, DESCENDING, 1, -1]:
            raise ValueError(
                f'Expected parameter "order" as 1 or -1. Instead, ' f"got {order}"
            )
        if k < 1:
            raise ValueError("Number of documents k must be greater than 0")

        return [
            self._model(**{k: v for k, v in item.items() if k != "_id"})
            async for item in self._collection.find(
                {"attorney_id": attorney_id, "applicant_id": applicant_id} | filters
            )
            .sort("date_created", order)
            .limit(k)
            .next()
        ]

    async def insert(self, doc: Union[EmbeddedDocument, Document]) -> ObjectId:
        """
        Inserts a mongo doc object into the mongo database

        :param attorney_id: the business id of the document to insert
        :param applicant_id: the user id of the document to insert
        :param doc: the object to insert into the database

        :return: the inserted mongo id
        """
        _logger.debug(f"Database operation: inserting document: {doc}")

        if not isinstance(doc, self._model):
            raise TypeError(
                f"The mongo doc provided {doc} of type {type(doc)} "
                f"needs to be type {self._model}"
            )

        result = await self._collection.insert_one(doc.to_mongo().to_dict())
        _logger.info(f"Document inserted. Mongo _id: {result.inserted_id}")

        return result.inserted_id
