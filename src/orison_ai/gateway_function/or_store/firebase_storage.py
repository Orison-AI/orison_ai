#! /usr/bin/env python3.11

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

import logging

from firebase_admin import storage

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class FirebaseStorage:
    """
    This is a helper class to interact with Google Firebase Storage
    """

    def __init__(self):
        pass

    @staticmethod
    def _bucket():
        """Private accessor for the Firebase Storage bucket

        Returns:
            google.cloud.storage.Bucket: The Firebase Storage bucket
        """
        return storage.bucket()

    @staticmethod
    async def upload_file(local_file_path: str, remote_file_path: str):
        try:
            blob = FirebaseStorage._bucket().blob(remote_file_path)
            blob.upload_from_filename(local_file_path)
            _logger.debug(f"Uploaded file to {remote_file_path}")
        except Exception as e:
            _logger.error(f"Error uploading file: {e}")

    @staticmethod
    async def download_file(remote_file_path: str, local_file_path: str):
        try:
            blob = FirebaseStorage._bucket().get_blob(remote_file_path)
            if blob is None:
                _logger.error(f"Blob {remote_file_path} could not be retrieved")
                raise Exception("Blob does not exist")
            blob.download_to_filename(local_file_path)
            _logger.debug(f"Downloaded file to {local_file_path}")
        except Exception as e:
            _logger.error(f"Error downloading file: {e}")
