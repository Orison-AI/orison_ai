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

import os
from pathlib import Path

PROJECT_ROOT_PATH = Path("/app/")
VAULT_PATH = Path(os.path.join(PROJECT_ROOT_PATH, "vault"))
CATEGORIES = ["research"]
FIREBASE_CREDENTIALS = VAULT_PATH / "credentials/firebase.json"
FIREBASE_STORAGE = "gs://orison-ai-visa-apply.appspot.com"
DB_NAME = "orison_ai"
REVISION = "1"
ROLE = """
    You are a helpful, respectful and honest assistant.
    Always answer as helpfully as possible and follow ALL given instructions.
    Do not speculate or make up information.
    Please describe the contribution to the field in words that someone with no technical background will understand. Use simple terms to express what makes the contribution so important or innovative and provide examples where applicable.
"""


def remove_protocol(url: str) -> str:
    """Remove the protocol from a Firebase Storage URL

    Args:
        url (str): A URL. Example: gs://orison-ai-visa-apply.appspot.com

    Returns:
        str: The URL without the protocol. Example: orison-ai-visa-apply.appspot.com
    """
    return url.split("://")[1]
