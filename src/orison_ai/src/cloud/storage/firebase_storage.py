import firebase_admin
from firebase_admin import storage
import orison_ai.src.cloud.firebase  # This is needed to initialize the Firebase app
import logging

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
            blob = FirebaseStorage._bucket().blob(remote_file_path)
            blob.download_to_filename(local_file_path)
            _logger.debug(f"Downloaded file to {local_file_path}")
        except Exception as e:
            _logger.error(f"Error downloading file: {e}")
