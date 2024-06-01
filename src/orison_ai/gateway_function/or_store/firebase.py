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
import os
import json
import logging
import datetime
from google.cloud.firestore_v1.base_query import FieldFilter, BaseCompositeFilter
from google.cloud.firestore_v1.types import StructuredQuery
from google.cloud.secretmanager_v1 import SecretManagerServiceClient
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import firestore_async
from bson import ObjectId
from typing import Optional
from mongoengine import Document, EmbeddedDocument
from typing import List, Union
from pymongo import DESCENDING, ASCENDING

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class CREDENTIALS_NOT_FOUND(ValueError):
    def __init__(self, message="Invalid Credentials"):
        self.message = message
        super().__init__(self.message)


class INVALID_CREDENTIALS(Exception):
    def __init__(self, message="Invalid Credentials"):
        self.message = message
        super().__init__(self.message)


class FIRESTORE_CONNECTION_FAILED(Exception):
    def __init__(self, message="Failed to connect to Firestore"):
        self.message = message
        super().__init__(self.message)


PROJECT_PREFIX_FOR_SECRET_MANAGER = "projects/685108028813/secrets/"


def build_secret_url(secret_name: str, project_prefix: str = PROJECT_PREFIX_FOR_SECRET_MANAGER):
    return project_prefix + secret_name + "/versions/latest"


def read_remote_secret_by_url(secret_url: str):
    # Create the Secret Manager client.
    client = SecretManagerServiceClient()
    # Access the secret version.
    response = client.access_secret_version(request={"name": secret_url})
    # Get the payload as a JSON string.
    payload = response.payload.data.decode("UTF-8")
    payload_dict = json.loads(payload)
    return payload_dict


def get_firebase_admin_app():
    cred_str = os.getenv("FIREBASE_CREDENTIALS")
    if cred_str is None:
        _logger.info(
            "Missing FIREBASE_CREDENTIALS in environment variable. Attempting secret manager"
        )
        try:
            cred_dict = read_remote_secret_by_url(build_secret_url("firebase_credentials"))
        except Exception as e:
            raise CREDENTIALS_NOT_FOUND(
                "FIREBASE_CREDENTIALS not found in environment variable or secret manager"
            )
    else:
        try:
            cred_dict = json.loads(cred_str)
        except json.JSONDecodeError:
            raise INVALID_CREDENTIALS("Invalid JSON in FIREBASE_CREDENTIALS")

    # Convert string back to JSON
    cred = credentials.Certificate(cred_dict)
    options = {"storageBucket": read_remote_secret_by_url(build_secret_url("bucket"))}
    try:
        _logger.info("Getting existing Firestore client")
        return firebase_admin.get_app()
    except ValueError as e:
        _logger.info("No existing client found. Creating new Firestore client")
        return firebase_admin.initialize_app(cred, options)
    except Exception as e:
        raise FIRESTORE_CONNECTION_FAILED("Failed to connect to Firestore")


class FireStoreDB:
    def __init__(self):
        """
        Initializes an instance of a FireStoreDB object, which can be used to
        connect to a FireStoreDB database
        """
        app = get_firebase_admin_app()
        self.client = firestore_async.client(app)


class FirestoreClient(FireStoreDB):
    def __init__(self):
        """
        Initializes an instance of a FirestoreClient object, which can be used
        to insert into or update a Firestore collection given a file
        """
        super(FirestoreClient, self).__init__()

    async def find_top(
            self,
            user_id: str,
            applicant_id: str,
            filters: Optional[dict] = {},
            order: [ASCENDING, DESCENDING, 1, -1] = DESCENDING,
    ) -> Union[EmbeddedDocument, Document, None]:
        """
        Finds a firestore Document item from the collection and converts it to a mongo object
        Order is either ASCENDING or DESCENDING

        :param user_id: the business id of the document to find
        :param applicant_id: the user id of the document to find
        :param order: the order in which to sort the documents
        :return: the entry found in firestore db for the requesting model class instance
                converted to a mongo object
        """
        result = await self.find_top_k(user_id, applicant_id, filters, 1, order)
        return result[0]

    async def find_top_k(
            self,
            user_id: str,
            applicant_id: str,
            filters: Optional[dict] = {},
            k: int = 1,
            order: [ASCENDING, DESCENDING, 1, -1] = DESCENDING,
    ) -> Union[List[EmbeddedDocument], List[Document], None]:
        """
        Finds top K firestore document items given a limit k from the collection
        and converts them to mongo objects
        Order is either ASCENDING or DESCENDING

        :param user_id: the business id of the document to find
        :param applicant_id: the user id of the document to find
        :param k: the number of documents to find
        :param order: the order in which to sort the documents
        :return: entries found in firestore converted to list of mongo objects
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
        order = (
            firestore.Query.ASCENDING
            if order == ASCENDING
            else firestore.Query.DESCENDING
        )
        if k < 1:
            raise ValueError("Number of documents k must be greater than 0")

        # Apply filters
        filters = {"user_id": user_id, "applicant_id": applicant_id} | filters
        composite_filter = BaseCompositeFilter(
            operator=StructuredQuery.CompositeFilter.Operator.AND,
            filters=[
                FieldFilter(field, "==", value) for field, value in filters.items()
            ],
        )

        if ASCENDING:
            query = (
                self._collection.where(filter=composite_filter)
                .order_by("date_created", direction=firestore.Query.ASCENDING)
                .limit(k)
            )
        else:
            query = (
                self._collection.where(filter=composite_filter)
                .order_by("date_created", direction=firestore.Query.DESCENDING)
                .limit(k)
            )

        return [
            self._model(**{k: v for k, v in item.to_dict().items() if k != "id"})
            async for item in query.stream()
        ]

    async def insert(self, doc: Union[EmbeddedDocument, Document]) -> ObjectId:
        """
        Inserts a mongo doc object into the firestore

        :param user_id: the business id of the document to insert
        :param applicant_id: the user id of the document to insert
        :param doc: the object to insert into the database

        :return: the inserted firestore id
        """
        _logger.debug(f"Database operation: inserting document: {doc}")

        if not isinstance(doc, self._model):
            raise TypeError(
                f"The mongo doc provided {doc} of type {type(doc)} "
                f"needs to be type {self._model}"
            )
        doc.date_created = datetime.datetime.utcnow()
        _, doc_ref = await self._collection.add(doc.to_mongo().to_dict())
        _logger.info(f"Document inserted. Firestore id: {doc_ref.id}")

        return doc_ref.id
