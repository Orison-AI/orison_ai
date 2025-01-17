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
from argparse import ArgumentParser
import subprocess
from print_firebase_identity_token import get_firebase_identity_token

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def send_curl_request(url, method, headers=None, data=None):
    curl_command = ["curl", "-X", method, url]

    # Add headers if provided
    if headers:
        for key, value in headers.items():
            curl_command.extend(["-H", f"{key}: {value}"])

    # Add data if provided
    if data:
        curl_command.extend(["-d", data])

    try:
        result = subprocess.run(
            curl_command, capture_output=True, text=True, check=True
        )
        _logger.info(f"Response:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        _logger.error(f"Error: {e.stderr}")


if __name__ == "__main__":
    # Example usage
    url_default = "0.0.0.0:3000"
    method = "POST"
    headers = {"Content-Type": "application/json"}

    parser = ArgumentParser()
    parser.add_argument("-d", "--data", type=str, required=True)
    parser.add_argument("-u", "--url", type=str, default=url_default)
    args = parser.parse_args()
    data = args.data
    url = args.url
    headers["Authorization"] = f"Bearer {get_firebase_identity_token()}"

    send_curl_request(url, method, headers, data)
