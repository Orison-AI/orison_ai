import firebase_admin

# External
from firebase_admin import (
    credentials,
)
import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Internal
from orison_ai.src.utils.constants import (
    FIREBASE_CREDENTIALS,
    FIREBASE_STORAGE,
    remove_protocol,
)


def _initialize_firebase(credentials_path: str):
    cred = credentials.Certificate(credentials_path)
    options = {"storageBucket": remove_protocol(FIREBASE_STORAGE)}
    try:
        _logger.debug(f"Firebase app already initialized.")
        app = firebase_admin.get_app()
    except:
        _logger.info(
            f"Initializing Firebase with credentials and options: {credentials_path}, {options}"
        )
        app = firebase_admin.initialize_app(cred, options)


_initialize_firebase(FIREBASE_CREDENTIALS)
