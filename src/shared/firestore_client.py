#!/usr/bin/env python3

# External Imports
import json
from typing import Dict, Any, Optional, List
from google.cloud import firestore

# Internal Imports


class TokenManager:
    """Manages OAuth tokens in Firestore."""

    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.collection = "user_tokens"

    def save_token(
        self, user_id: str, provider: str, token_data: Dict[str, Any]
    ) -> None:
        """Save OAuth token for user and provider."""
        doc_ref = self.db.collection(self.collection).document(f"{user_id}_{provider}")
        doc_ref.set(token_data)

    def get_token(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        """Get OAuth token for user and provider."""
        doc_ref = self.db.collection(self.collection).document(f"{user_id}_{provider}")
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def delete_token(self, user_id: str, provider: str) -> None:
        """Delete OAuth token for user and provider."""
        doc_ref = self.db.collection(self.collection).document(f"{user_id}_{provider}")
        doc_ref.delete()


class LoadedFilesManager:
    """Tracks which Drive files a user has marked as 'loaded'."""

    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.collection = "user_loaded_files"

    def _doc(self, user_id: str):
        return self.db.collection(self.collection).document(user_id)

    def get_loaded_ids(self, user_id: str) -> List[str]:
        doc = self._doc(user_id).get()
        data = doc.to_dict() if doc.exists else None
        return data.get("file_ids", []) if data else []

    def add_loaded(self, user_id: str, file_ids: List[str]) -> None:
        current = set(self.get_loaded_ids(user_id))
        updated = list(current.union(file_ids))
        self._doc(user_id).set({"file_ids": updated})

    def remove_loaded(self, user_id: str, file_ids: List[str]) -> None:
        current = set(self.get_loaded_ids(user_id))
        updated = [fid for fid in current if fid not in set(file_ids)]
        self._doc(user_id).set({"file_ids": updated})

    def clear_loaded(self, user_id: str) -> None:
        self._doc(user_id).set({"file_ids": []})
