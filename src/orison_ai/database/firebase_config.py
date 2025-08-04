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

import os
import json
import logging
import datetime
from typing import List, Union, Optional, Any
from google.cloud.firestore_v1.base_query import FieldFilter, BaseCompositeFilter
from google.cloud.firestore_v1.types import StructuredQuery
from google.cloud.secretmanager_v1 import SecretManagerServiceClient
import firebase_admin
from firebase_admin import firestore, credentials
from mongoengine import Document, EmbeddedDocument, DoesNotExist
from pymongo import DESCENDING, ASCENDING


# Custom exception classes
class CredentialsNotFound(Exception):
    """Exception raised when Firebase credentials are not found."""

    def __init__(self, exception=None):
        self.exception = exception
        super().__init__(str(exception) if exception else "Credentials not found")


class InvalidCredentials(Exception):
    """Exception raised when Firebase credentials are invalid."""

    def __init__(self, exception=None):
        self.exception = exception
        super().__init__(str(exception) if exception else "Invalid credentials")


class FirestoreConnectionFailed(Exception):
    """Exception raised when Firestore connection fails."""

    def __init__(self, exception=None):
        self.exception = exception
        super().__init__(str(exception) if exception else "Firestore connection failed")


# Backward compatibility constants
CREDENTIALS_NOT_FOUND = "CREDENTIALS_NOT_FOUND"
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
FIRESTORE_CONNECTION_FAILED = "FIRESTORE_CONNECTION_FAILED"

# Configuration constants
PROJECT_PREFIX_FOR_SECRET_MANAGER = "projects/685108028813/secrets/"

# Module logger
logger = logging.getLogger(__name__)


class SecretManager:
    """Handles secure retrieval of secrets from environment variables or Google Secret Manager."""

    def __init__(self, project_prefix: str = PROJECT_PREFIX_FOR_SECRET_MANAGER):
        self.project_prefix = project_prefix
        self._client: Optional[SecretManagerServiceClient] = None

    @property
    def client(self) -> SecretManagerServiceClient:
        """Lazy initialization of Secret Manager client."""
        if self._client is None:
            self._client = SecretManagerServiceClient()
        return self._client

    def build_secret_url(self, secret_name: str) -> str:
        """Build the full secret URL for Google Secret Manager."""
        return f"{self.project_prefix}{secret_name}/versions/latest"

    def read_remote_secret(self, secret_url: str) -> str:
        """Read secret from Google Secret Manager."""
        response = self.client.access_secret_version(request={"name": secret_url})
        payload = response.payload.data.decode("UTF-8")
        return payload

    def get_secret(self, key: str) -> Optional[str]:
        """Get a single secret from environment or Secret Manager."""
        # Try environment variable first
        value = os.getenv(key.upper())
        if value is not None:
            return value

        # Fall back to Secret Manager
        logger.info(
            f"Missing {key.upper()} in environment variable. Attempting secret manager"
        )
        try:
            value = self.read_remote_secret(self.build_secret_url(key.lower()))
            logger.info(f"{key.lower()} found in secret manager.")
            return value
        except Exception as e:
            logger.error(f"Error getting {key.lower()} from secret manager. Error: {e}")
            return None

    def get_secrets(self, keys: Union[str, List[str]]) -> Union[str, List[str]]:
        """Get multiple secrets from environment or Secret Manager."""
        if isinstance(keys, str):
            return self.get_secret(keys)

        values = [self.get_secret(key) for key in keys]
        return values


class FirebaseConfig:
    """Manages Firebase configuration and authentication."""

    def __init__(self):
        self.secret_manager = SecretManager()

    def _get_credentials(self) -> dict:
        """Retrieve and parse Firebase credentials."""
        secret = self.secret_manager.get_secret("FIREBASE_CREDENTIALS")
        if not secret:
            error_msg = "No Firebase credentials found in environment variables or secret manager"
            logger.error(error_msg)
            raise CredentialsNotFound(exception=error_msg)

        try:
            return json.loads(secret)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Firebase credentials JSON: {e}")
            raise InvalidCredentials(exception=e)

    def _get_storage_options(self) -> dict:
        """Retrieve storage bucket configuration."""
        try:
            bucket_str = self.secret_manager.get_secret("BUCKET")
            return {"storageBucket": str(bucket_str)} if bucket_str else {}
        except Exception as e:
            logger.error(f"Error getting bucket configuration: {e}")
            return {}

    def get_firebase_app(self) -> firebase_admin.App:
        """Get or create Firebase admin app instance."""
        try:
            logger.info("Getting existing Firestore client")
            return firebase_admin.get_app()
        except ValueError:
            logger.info("No existing client found. Creating new Firestore client")
            return self._create_new_app()
        except Exception as e:
            raise FirestoreConnectionFailed(exception=e)

    def _create_new_app(self) -> firebase_admin.App:
        """Create a new Firebase admin app."""
        try:
            cred_dict = self._get_credentials()
            options = self._get_storage_options()

            cred = credentials.Certificate(cred_dict)
            app = firebase_admin.initialize_app(cred, options)

            logger.info(f"Firestore client created with name: {app.name}")
            return app
        except Exception as e:
            logger.error(f"Error creating Firebase app: {e}")
            raise FirestoreConnectionFailed(exception=e)


# Maintain backward compatibility with existing function
def environment_or_secret(keys: Union[str, List[str]]):
    """Legacy function for backward compatibility."""
    secret_manager = SecretManager()
    return secret_manager.get_secrets(keys)


def build_secret_url(
    secret_name: str, project_prefix: str = PROJECT_PREFIX_FOR_SECRET_MANAGER
):
    """Legacy function for backward compatibility."""
    secret_manager = SecretManager(project_prefix)
    return secret_manager.build_secret_url(secret_name)


def read_remote_secret_url_as_string(
    client: SecretManagerServiceClient, secret_url: str
) -> str:
    """Legacy function for backward compatibility."""
    response = client.access_secret_version(request={"name": secret_url})
    payload = response.payload.data.decode("UTF-8")
    return payload


def get_firebase_admin_app():
    """Legacy function for backward compatibility."""
    config = FirebaseConfig()
    return config.get_firebase_app()


class FireStoreDB:
    """Base Firestore database client with document management capabilities."""

    def __init__(self, firebase_config: Optional[FirebaseConfig] = None):
        """Initialize FireStore client with optional custom config."""
        if firebase_config is None:
            firebase_config = FirebaseConfig()

        self.app = firebase_config.get_firebase_app()
        self.client = firestore.client(app=self.app)

    def _get_document_reference(self, collection_name: str, document_name: str):
        """Get document reference for the given collection and document."""
        return self.client.collection(collection_name).document(document_name)

    def _get_current_field_value(self, document_ref, field: str) -> Optional[Any]:
        """Retrieve current value of a field from document."""
        try:
            doc_data = document_ref.get().to_dict()
            return doc_data.get(field) if doc_data else None
        except Exception as e:
            logger.error(f"Error retrieving field {field}: {e}")
            return None

    def _validate_field_update_params(self, field: str, value: Any) -> bool:
        """Validate parameters for field update operations."""
        if not field:
            logger.error("Field cannot be empty")
            return False
        if not value:
            logger.error("Value cannot be empty")
            return False
        return True

    async def remove_value_from_field(
        self,
        collection_name: str,
        document_name: str,
        field: str,
        value: Union[Any, List[Any]],
    ) -> Optional[bool]:
        """
        Remove value from a field in a Firestore document.

        :param collection_name: Name of the collection
        :param document_name: Name of the document
        :param field: Field name to modify
        :param value: Value to remove
        :return: True if successful, None if failed
        """
        try:
            document_ref = self._get_document_reference(collection_name, document_name)
            current_value = self._get_current_field_value(document_ref, field)

            if current_value is None:
                logger.error("Field does not exist in document. Cannot update field")
                return None

            if isinstance(current_value, list):
                if value in current_value:
                    current_value.remove(value)
                    document_ref.update({field: current_value})
            else:
                document_ref.update({field: None})

            logger.info(
                f"Removed value from field {field} in {collection_name}/{document_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error removing value from field: {e}")
            return None

    async def update_collection_document(
        self,
        collection_name: str,
        document_name: str,
        field: str,
        value: Union[Any, List[Any]],
    ) -> Optional[bool]:
        """
        Update a field in a Firestore document.

        :param collection_name: Name of the collection
        :param document_name: Name of the document
        :param field: Field name to update
        :param value: New value for the field
        :return: True if successful, None if failed
        """
        if not self._validate_field_update_params(field, value):
            return None

        try:
            document_ref = self._get_document_reference(collection_name, document_name)
            current_value = self._get_current_field_value(document_ref, field)

            if current_value is None:
                logger.error("Field does not exist in document. Cannot update field")
                return None

            # Handle list field updates
            if isinstance(current_value, list):
                if isinstance(value, list):
                    # Add new values that don't exist
                    for val in value:
                        if val not in current_value:
                            current_value.append(val)
                elif value not in current_value:
                    current_value.append(value)
                document_ref.update({field: current_value})
            else:
                # Simple field update
                document_ref.update({field: value})

            logger.info(f"Updated field {field} in {collection_name}/{document_name}")
            return True

        except Exception as e:
            logger.error(f"Error updating document field: {e}")
            return None


class FirestoreClient(FireStoreDB):
    """Extended Firestore client with document querying and management capabilities."""

    def __init__(self, firebase_config: Optional[FirebaseConfig] = None):
        """Initialize FirestoreClient with optional custom config."""
        super().__init__(firebase_config)
        self._model = None
        self._collection = None

    def set_model(self, model_class):
        """Set the document model class for this client."""
        self._model = model_class

    def set_collection(self, collection):
        """Set the Firestore collection reference for this client."""
        self._collection = collection

    def _validate_client_state(self):
        """Validate that model and collection are properly set."""
        if self._collection is None:
            raise ValueError("Collection not set")
        if self._model is None:
            raise ValueError("DB Model not set")

    def _validate_query_params(self, k: int, order):
        """Validate query parameters."""
        if order not in [ASCENDING, DESCENDING, 1, -1]:
            raise ValueError(
                f'Expected parameter "order" as 1 or -1. Instead, got {order}'
            )
        if k < 1:
            raise ValueError("Number of documents k must be greater than 0")

    def _normalize_order(self, order):
        """Convert order parameter to Firestore Query direction."""
        return (
            firestore.Query.ASCENDING
            if order == ASCENDING
            else firestore.Query.DESCENDING
        )

    def _build_composite_filter(self, filters: dict) -> BaseCompositeFilter:
        """Build composite filter from filter dictionary."""
        return BaseCompositeFilter(
            operator=StructuredQuery.CompositeFilter.Operator.AND,
            filters=[
                FieldFilter(field, "==", value) for field, value in filters.items()
            ],
        )

    def _build_query(self, applicant_collection, composite_filter, order, k: int):
        """Build Firestore query with filters, ordering, and limit."""
        return (
            applicant_collection.where(filter=composite_filter)
            .order_by("date_created", direction=order)
            .limit(k)
        )

    def _process_query_results(self, query_stream):
        """Process query results into model instances."""
        return [
            (
                self._model(**{k: v for k, v in item.to_dict().items() if k != "id"}),
                item.id,
            )
            for item in query_stream
        ]

    async def find_top(
        self,
        attorney_id: str,
        applicant_id: str,
        filters: Optional[dict] = None,
        order=DESCENDING,
    ) -> Union[EmbeddedDocument, Document, None]:
        """
        Find the top document from the collection and convert to mongo object.

        :param attorney_id: Business ID of the document to find
        :param applicant_id: User ID of the document to find
        :param filters: Optional filter dictionary
        :param order: Sort order (ASCENDING or DESCENDING)
        :return: Document converted to mongo object
        :raises DoesNotExist: If no document is found
        """
        if filters is None:
            filters = {}

        result = await self.find_top_k(attorney_id, applicant_id, filters, 1, order)
        if result:
            return result[0]
        else:
            raise DoesNotExist

    async def find_top_k(
        self,
        attorney_id: str,
        applicant_id: str,
        filters: Optional[dict] = None,
        k: int = 1,
        order=DESCENDING,
    ) -> Union[List[EmbeddedDocument], List[Document], None]:
        """
        Find top K documents from the collection and convert to mongo objects.

        :param attorney_id: Business ID of the document to find
        :param applicant_id: User ID of the document to find
        :param filters: Optional filter dictionary
        :param k: Number of documents to find
        :param order: Sort order (ASCENDING or DESCENDING)
        :return: List of documents converted to mongo objects
        """
        if filters is None:
            filters = {}

        logger.info(f"Database operation: find {k} documents by order: {order}")

        # Validate client state and parameters
        self._validate_client_state()
        self._validate_query_params(k, order)

        # Normalize order parameter
        normalized_order = self._normalize_order(order)

        # Get nested collection reference
        attorney_document = self._collection.document(attorney_id)
        applicant_collection = attorney_document.collection(applicant_id)

        # Build and execute query
        composite_filter = self._build_composite_filter(filters)
        query = self._build_query(
            applicant_collection, composite_filter, normalized_order, k
        )

        # Process and return results
        return self._process_query_results(query.stream())

    def _validate_document_type(self, doc: Union[EmbeddedDocument, Document]):
        """Validate that document is of the correct model type."""
        if not isinstance(doc, self._model):
            raise TypeError(
                f"The mongo doc provided {doc} of type {type(doc)} "
                f"needs to be type {self._model}"
            )

    def _prepare_document_for_storage(self, doc: Union[EmbeddedDocument, Document]):
        """Prepare document for storage by setting creation timestamp."""
        doc.date_created = datetime.datetime.utcnow()
        return doc

    async def insert(
        self,
        attorney_id: str,
        applicant_id: str,
        doc: Union[EmbeddedDocument, Document],
    ) -> str:
        """
        Insert a document into Firestore.

        :param attorney_id: Business ID for document organization
        :param applicant_id: User ID for document organization
        :param doc: Document to insert
        :return: Firestore document ID
        """
        logger.info(f"Database operation: inserting document: {doc}")

        # Validate document type and prepare for storage
        self._validate_document_type(doc)
        prepared_doc = self._prepare_document_for_storage(doc)

        # Get nested collection and insert document
        attorney_document = self._collection.document(attorney_id)
        applicant_collection = attorney_document.collection(applicant_id)
        _, doc_ref = applicant_collection.add(prepared_doc.to_mongo().to_dict())

        logger.info(f"Document inserted. Firestore id: {doc_ref.id}")
        return doc_ref.id

    async def replace(
        self,
        attorney_id: str,
        applicant_id: str,
        doc_id: str,
        doc: Union[EmbeddedDocument, Document],
    ) -> str:
        """
        Replace an existing document in Firestore.

        :param attorney_id: Business ID for document organization
        :param applicant_id: User ID for document organization
        :param doc_id: ID of document to replace
        :param doc: New document data
        :return: Firestore document ID
        """
        logger.info(f"Database operation: replacing document with id {doc_id}: {doc}")

        # Validate document type and prepare for storage
        self._validate_document_type(doc)
        prepared_doc = self._prepare_document_for_storage(doc)

        # Get document reference and replace data
        attorney_document = self._collection.document(attorney_id)
        applicant_collection = attorney_document.collection(applicant_id)
        doc_ref = applicant_collection.document(doc_id)

        # Replace document data (merge=False for complete replacement)
        doc_ref.set(prepared_doc.to_mongo().to_dict(), merge=False)

        logger.info(f"Document replaced. Firestore id: {doc_ref.id}")
        return doc_ref.id

    async def delete(
        self,
        attorney_id: str,
        applicant_id: str,
        doc_id: str,
    ) -> bool:
        """
        Delete a document from Firestore.

        :param attorney_id: Business ID for document organization
        :param applicant_id: User ID for document organization
        :param doc_id: ID of document to delete
        :return: True if successful, False otherwise
        """
        try:
            logger.info(f"Database operation: deleting document with id {doc_id}")

            # Validate client state
            self._validate_client_state()

            # Get document reference and delete
            attorney_document = self._collection.document(attorney_id)
            applicant_collection = attorney_document.collection(applicant_id)
            doc_ref = applicant_collection.document(doc_id)

            # Check if document exists before deleting
            doc_snapshot = doc_ref.get()
            if not doc_snapshot.exists:
                logger.warning(f"Document {doc_id} does not exist, cannot delete")
                return False

            # Delete the document
            doc_ref.delete()

            # Verify deletion by checking if document still exists
            deleted_doc_snapshot = doc_ref.get()
            if deleted_doc_snapshot.exists:
                logger.error(f"Document {doc_id} still exists after delete operation")
                return False

            logger.info(f"Document deleted successfully. Firestore id: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document with id {doc_id}: {e}")
            return False
