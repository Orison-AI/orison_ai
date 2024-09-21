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

import sys

sys.path.append("../src/orison_ai/gateway_function")
import asyncio
import logging
from argparse import ArgumentParser
from print_firebase_identity_token import get_firebase_identity_token
import time
from asyncio.locks import Event

SLEEP = 0.3
LAST_CALL = None
event = Event()
event.set()

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


async def send_curl_request(url, method, headers=None, data=None):
    global LAST_CALL

    _logger.info(f"Sending {method} request to {url}")
    curl_command = ["curl", "-X", method, url]

    # Add headers if provided
    if headers:
        for key, value in headers.items():
            curl_command.extend(["-H", f"{key}: {value}"])

    # Add data if provided
    if data:
        curl_command.extend(["-d", data])

    await event.wait()
    event.clear()
    if not LAST_CALL:
        LAST_CALL = time.time()
    else:
        time_elapsed = time.time() - LAST_CALL
        if time_elapsed < SLEEP:
            time.sleep(SLEEP - time_elapsed)
        LAST_CALL = time.time()
    event.set()
    try:
        # Use asyncio to create and run the subprocess asynchronously
        process = await asyncio.create_subprocess_exec(
            *curl_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            message = f"Response:\n{stdout.decode()}"
            _logger.info(message)
        else:
            message = f"Error: {stderr.decode()}"
            _logger.error(message)

    except Exception as e:
        message = f"Exception occurred: {str(e)}"
        _logger.error(message)
    return message


async def main(url, method, headers, data):
    tasks = [send_curl_request(url, method, headers, data) for i in range(1000)]

    counter = 0
    for task in asyncio.as_completed(tasks):
        counter += 1
        result = await task
        print(f"Counter: {counter}. Result: {result}")


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

    asyncio.run(main(url, method, headers, data))
