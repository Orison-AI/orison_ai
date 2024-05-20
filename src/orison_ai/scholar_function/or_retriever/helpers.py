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

import traceback
import re
import requests
import traceback
import logging

# Internal

from or_retriever.google_scholar import get_google_scholar_info
from or_store.models import GoogleScholarRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def stringify_keys(data):
    if isinstance(data, dict):
        return {str(key): stringify_keys(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [stringify_keys(element) for element in data]
    return data


class INVALID_URL(Exception):
    def __init__(self, message="Invalid URL"):
        self.message = message
        super().__init__(self.message)


class INVALID_USER(Exception):
    def __init__(self, message="Invalid User"):
        self.message = message
        super().__init__(self.message)


async def url_exists(url: str):
    """
    Check if a URL exists by sending a HEAD request to the URL
    and checking the response status code.
    :param url: The URL to check
    :return: True if the URL exists, False otherwise
    """

    try:
        if url == "":
            raise ValueError("URL is empty")

        requests.head(url, allow_redirects=True, timeout=5)

    except ValueError as e:
        message = f"Invalid URL: {traceback.format_exc(e)}"
        logger.error(message)
        raise INVALID_URL(message)

    except requests.RequestException as e:
        # Handle possible exceptions, such as network problems
        message = (
            f"Request response timed-out while checking URL: {traceback.format_exc(e)}"
        )
        logger.error(message)
        raise INVALID_URL(message)

    except Exception as e:
        message = f"Unknown error checking URL: {traceback.format_exc(e)}"
        logger.error(message)
        raise INVALID_URL(message)


async def extract_user(url: str):
    """
    Extract the user ID from a Google Scholar URL.
    :param url: The Google Scholar URL
    """

    match = re.search(r"user=([a-zA-Z0-9]+)", url)
    if match:
        applicant_id = match.group(1)
        return applicant_id
    return None


async def fetch_scholar_helper(user_request: GoogleScholarRequest):
    try:
        scholar_info = await get_google_scholar_info(
            attorney_id=user_request.attorney_id,
            applicant_id=user_request.applicant_id,
            scholar_link=user_request.scholar_link,
        )
    except Exception as e:
        logger.error(
            f"Failed to generate google scholar database. Error: {traceback.format_exc(e)}"
        )
        raise e
    try:
        if scholar_info is not None:
            logger.info("Google scholar data class initialized")
            return scholar_info
    except Exception as e:
        logger.error(
            f"Failed to insert google scholar data. Error: {traceback.format_exc(e)}"
        )
        raise e
