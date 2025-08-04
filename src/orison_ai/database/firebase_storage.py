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

import logging
import os
from firebase_admin import storage

# Internal

from database.firebase_config import get_firebase_admin_app

logger = logging.getLogger(__name__)


class FirebaseStorage:
    """Firebase Storage helper class - preserved from original"""

    def __init__(self):
        pass

    @staticmethod
    def _bucket():
        """Private accessor for the Firebase Storage bucket - preserved from original"""
        # Ensure Firebase app is initialized before accessing storage
        app = get_firebase_admin_app()
        return storage.bucket(app=app)

    @staticmethod
    async def upload_file(local_file_path: str, remote_file_path: str):
        """Upload file to Firebase Storage - preserved from original"""
        try:
            # Check if local file exists
            if not os.path.exists(local_file_path):
                logger.error(f"Local file does not exist: {local_file_path}")
                raise FileNotFoundError(f"Local file not found: {local_file_path}")

            blob = FirebaseStorage._bucket().blob(remote_file_path)
            blob.upload_from_filename(local_file_path)
            logger.info(f"Uploaded file to {remote_file_path}")
        except Exception as e:
            logger.error(
                f"Error uploading file {local_file_path} to {remote_file_path}: {e}"
            )
            raise

    @staticmethod
    async def download_file(remote_file_path: str, local_file_path: str):
        """Download file from Firebase Storage - preserved from original"""
        try:
            blob = FirebaseStorage._bucket().get_blob(remote_file_path)
            if blob is None:
                logger.error(f"Blob {remote_file_path} could not be retrieved")
                raise FileNotFoundError(
                    f"File not found in storage: {remote_file_path}"
                )
            blob.download_to_filename(local_file_path)
            logger.info(f"Downloaded file to {local_file_path}")
        except Exception as e:
            logger.error(
                f"Error downloading file {remote_file_path} to {local_file_path}: {e}"
            )
            raise

    @staticmethod
    async def delete_file(remote_file_path: str):
        """Delete file from Firebase Storage"""
        try:
            blob = FirebaseStorage._bucket().blob(remote_file_path)
            blob.delete()
            logger.info(f"Deleted file from {remote_file_path}")
        except Exception as e:
            logger.error(f"Error deleting file {remote_file_path}: {e}")
            raise

    @staticmethod
    async def file_exists(remote_file_path: str) -> bool:
        """Check if file exists in Firebase Storage"""
        try:
            blob = FirebaseStorage._bucket().get_blob(remote_file_path)
            return blob is not None
        except Exception as e:
            logger.error(f"Error checking file existence {remote_file_path}: {e}")
            return False

    @staticmethod
    async def get_file_size(remote_file_path: str) -> int:
        """Get file size from Firebase Storage"""
        try:
            blob = FirebaseStorage._bucket().get_blob(remote_file_path)
            if blob is None:
                raise FileNotFoundError(f"File not found: {remote_file_path}")
            return blob.size
        except Exception as e:
            logger.error(f"Error getting file size for {remote_file_path}: {e}")
            raise
