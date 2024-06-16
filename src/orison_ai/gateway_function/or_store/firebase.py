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
from dataclasses import dataclass
import datetime
from exceptions import (
    CREDENTIALS_NOT_FOUND,
    INVALID_CREDENTIALS,
    FIRESTORE_CONNECTION_FAILED,
)
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


PROJECT_PREFIX_FOR_SECRET_MANAGER = "projects/685108028813/secrets/"


@dataclass
class OrisonSecrets:
    openai_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    collection_name: str

    @classmethod
    def from_attorney_applicant(cls, attorney_id: str, applicant_id: str):
        _logger.debug(
            f"Processing file for attorney {attorney_id} and applicant {applicant_id}"
        )
        return cls(
            openai_api_key=environment_or_secret("OPENAI_API_KEY"),
            qdrant_url=environment_or_secret("QDRANT_URL"),
            qdrant_api_key=environment_or_secret("QDRANT_API_KEY"),
            # TODO: Need to sanitize the path to avoid path traversal attacks
            collection_name=f"{attorney_id}_{applicant_id}_collection",
        )


def environment_or_secret(key: str):
    value = os.getenv(key.upper())
    if value is None:
        _logger.info(
            f"Missing {key.upper()} in environment variable. Attempting secret manager"
        )
        try:
            # Getting secrets
            value = read_remote_secret_url_as_string(build_secret_url(key.lower()))
        except Exception as e:
            message = f"{key.lower()} not found in secret manager. Error: {e}"
            raise CREDENTIALS_NOT_FOUND(message=message)
    return value


def build_secret_url(
    secret_name: str, project_prefix: str = PROJECT_PREFIX_FOR_SECRET_MANAGER
):
    return project_prefix + secret_name + "/versions/latest"


def read_remote_secret_url_as_string(secret_url: str) -> str:
    # Create the Secret Manager client.
    client = SecretManagerServiceClient()
    # Access the secret version.
    response = client.access_secret_version(request={"name": secret_url})
    # Get the payload as a JSON string.
    payload = response.payload.data.decode("UTF-8")
    return payload


def get_firebase_admin_app():
    try:
        secret = environment_or_secret("FIREBASE_CREDENTIALS")
        cred_dict = json.loads(secret)
    except CREDENTIALS_NOT_FOUND as e:
        raise e
    except json.JSONDecodeError:
        raise INVALID_CREDENTIALS("Invalid JSON in FIREBASE_CREDENTIALS")
    except Exception as e:
        _logger.error(f"Unknown error: {e}")
    options = {}
    try:
        bucket_str = environment_or_secret("BUCKET")
        options = {"storageBucket": bucket_str}
    except CREDENTIALS_NOT_FOUND as e:
        _logger.error(f"No bucket found in environment variables. Error: {e}")
    except Exception as e:
        _logger.error(f"Unknown error: {e}")

    # Convert string back to JSON
    cred = credentials.Certificate(cred_dict)

    try:
        _logger.info("Getting existing Firestore client")
        return firebase_admin.get_app()
    except ValueError as e:
        _logger.info("No existing client found. Creating new Firestore client")
        app = firebase_admin.initialize_app(cred, options)
        _logger.info(f"Firestore client created with name: {app.name}")
        return app
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
        attorney_id: str,
        applicant_id: str,
        filters: Optional[dict] = {},
        order=DESCENDING,
    ) -> Union[EmbeddedDocument, Document, None]:
        """
        Finds a firestore Document item from the collection and converts it to a mongo object
        Order is either ASCENDING or DESCENDING

        :param attorney_id: the business id of the document to find
        :param applicant_id: the user id of the document to find
        :param order: the order in which to sort the documents
        :return: the entry found in firestore db for the requesting model class instance
                converted to a mongo object
        """
        result = await self.find_top_k(attorney_id, applicant_id, filters, 1, order)
        return result[0]

    async def find_top_k(
        self,
        attorney_id: str,
        applicant_id: str,
        filters: Optional[dict] = {},
        k: int = 1,
        order=DESCENDING,
    ) -> Union[List[EmbeddedDocument], List[Document], None]:
        """
        Finds top K firestore document items given a limit k from the collection
        and converts them to mongo objects
        Order is either ASCENDING or DESCENDING

        :param attorney_id: the business id of the document to find
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
        filters = {"attorney_id": attorney_id, "applicant_id": applicant_id} | filters
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

        :param attorney_id: the business id of the document to insert
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
