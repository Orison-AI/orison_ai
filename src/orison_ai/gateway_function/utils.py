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

import time
import os
import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Any


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
    SLEEP_SECONDS = 0.15  # Time to sleep between OpenAI requests
    executor = ThreadPoolExecutor(max_workers=1)

    def __init__(self, logger):
        self._logger = logger
        self._request_queue = asyncio.Queue()  # Async queue to manage requests
        self._worker_task = asyncio.create_task(self._process_requests())

    async def _process_requests(self):
        if self._logger:
            self._logger.info("Starting ThrottleRequest worker")
        while True:
            fn, args, kwargs, result_future = await self._request_queue.get()

            if ThrottleRequest.register_last is not None:
                time_elapsed = time.time() - ThrottleRequest.register_last
                if time_elapsed <= ThrottleRequest.SLEEP_SECONDS:
                    await asyncio.sleep(ThrottleRequest.SLEEP_SECONDS - time_elapsed)

            if self._logger:
                self._logger.info(
                    f"Throttling request for {fn.__name__} at time: {time.time()}"
                )

            try:
                result = (
                    await fn(*args, **kwargs)
                    if asyncio.iscoroutinefunction(fn)
                    else await asyncio.get_running_loop().run_in_executor(
                        ThrottleRequest.executor, fn, *args, **kwargs
                    )
                )
                result_future.set_result(result)
            except Exception as e:
                if self._logger:
                    self._logger.error(
                        f"Error occurred in throttled function {fn.__name__}: {e}"
                    )
                result_future.set_exception(e)

            if self._logger:
                self._logger.info(
                    f"Throttling request for {fn.__name__}....DONE at time: {time.time()}"
                )
            ThrottleRequest.register_last = time.time()
            self._request_queue.task_done()

    # @staticmethod
    # def throttle_call(fn: Callable[..., Any], *args, **kwargs) -> Any:
    #     if not ThrottleRequest.worker_start:
    #         threading.Thread(target=ThrottleRequest.start_worker).start()
    #     loop = asyncio.get_running_loop()
    #     result_future = Future()
    #     asyncio.run_coroutine_threadsafe(
    #         ThrottleRequest.request_queue.put((fn, args, kwargs, result_future)), loop
    #     )
    #     return result_future.result()

    async def athrottle_call(self, fn: Callable[..., Any], *args, **kwargs) -> Any:
        result_future = Future()
        await self._request_queue.put((fn, args, kwargs, result_future))
        return result_future.result()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    async def atest_fn():
        await asyncio.sleep(0.1)
        return "Async test function called"

    def test_fn():
        time.sleep(0.1)
        return "Test function called"

    async def main():
        throttle_requester = ThrottleRequest(logger)
        logger.info("Testing ThrottleRequest with one async call")
        result = await throttle_requester.athrottle_call(atest_fn)
        logger.info(f"Test complete. Result: {result}")
        # logger.info("Testing ThrottleRequest with one sync call")
        # result = ThrottleRequest.throttle_call(test_fn)
        # logger.info(f"Test complete. Result: {result}")

        # logger.info("Testing ThrottleRequest with multiple async calls")
        # result = await asyncio.gather(
        #     *[
        #         asyncio.create_task(ThrottleRequest.athrottle_call(atest_fn))
        #         for i in range(3)
        #     ]
        # )
        # logger.info(f"Test complete. Result: {result}")
        # logger.info("Testing ThrottleRequest with multiple sync calls")
        # results = []
        # for i in range(3):
        #     results.append(ThrottleRequest.throttle_call(test_fn))
        # logger.info(f"Test complete. Result: {results}")

    asyncio.run(main())
