#! /usr/bin/env python3.9

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
import requests
import logging

# Internal

from orison_ai.src.utils.exceptions import INVALID_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
