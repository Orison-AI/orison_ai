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

import time
import os
import asyncio
from asyncio.locks import Event
from typing import Callable, Any

OPENAI_SLEEP = 0.15  # Time to sleep between OpenAI requests


def file_extension(file_path: str) -> str:
    # Identify the file format based on the file extension
    return os.path.splitext(file_path)[1].lower()


def raise_and_log_error(message: str, logger, exception=Exception):
    logger.error(message)
    raise exception(message)


# Define an asynchronous generator function
async def async_generator_from_list(data_list: list):
    if not isinstance(data_list, list):
        raise TypeError("data_list must be a list")
    for item in data_list:
        yield item
        # Simulate some asynchronous operation
        await asyncio.sleep(0.001)


class ThrottleRequest:
    register_last = None  # Class variable to track the time of the last call
    throttle_lock = Event()  # Lock to throttle the requests
    logger = None

    @staticmethod
    def clear_and_log(func_name: str):
        # Update the time_elapsed to the current time
        ThrottleRequest.throttle_lock.clear()
        ThrottleRequest.register_last = time.time()

        if ThrottleRequest.logger:
            ThrottleRequest.logger.info(
                f"Throttling request for {func_name} at time: {time.time()}"
            )

    @staticmethod
    def set_and_log(func_name: str):
        if ThrottleRequest.logger:
            ThrottleRequest.logger.info(
                f"Throttling request for {func_name}....DONE at time: {time.time()}"
            )
        ThrottleRequest.throttle_lock.set()

    @staticmethod
    def throttle_call(fn: Callable[..., Any], *args, **kwargs) -> Any:
        if ThrottleRequest.register_last is not None:
            # Wait for the throttle lock to clear
            start_time = time.time()
            while not ThrottleRequest.throttle_lock.is_set():
                if time.time() - start_time > 5.0:
                    raise TimeoutError("Throttle lock not cleared")
                time.sleep(0.001)
            time_elapsed = start_time - ThrottleRequest.register_last
            if time_elapsed <= OPENAI_SLEEP:
                time.sleep(OPENAI_SLEEP - time_elapsed)
        ThrottleRequest.clear_and_log(fn.__name__)
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            if ThrottleRequest.logger:
                ThrottleRequest.logger.error(
                    f"Error occurred in throttled function {fn.__name__}: {e}"
                )
            raise e
        ThrottleRequest.set_and_log(fn.__name__)
        return result

    @staticmethod
    async def athrottle_call(future: Callable[..., Any], *args, **kwargs) -> Any:
        # Check if future is truly a future. Else convert it to one.
        if not asyncio.iscoroutinefunction(future):
            future = asyncio.coroutine(future)

        if ThrottleRequest.register_last is not None:
            # Wait for event to clear
            await ThrottleRequest.throttle_lock.wait()
            # Calculate the time since the last call
            time_elapsed = time.time() - ThrottleRequest.register_last
            # If the time since the last call is less than the limit, wait for the remaining time
            if time_elapsed <= OPENAI_SLEEP:
                await asyncio.sleep(OPENAI_SLEEP - time_elapsed)

        ThrottleRequest.clear_and_log(future.__name__)
        try:
            result = await future(*args, **kwargs)
        except Exception as e:
            if ThrottleRequest.logger:
                ThrottleRequest.logger.error(
                    f"Error occurred in throttled function {future.__name__}: {e}"
                )
            raise e
        ThrottleRequest.set_and_log(future.__name__)
        # Return the result
        return result
